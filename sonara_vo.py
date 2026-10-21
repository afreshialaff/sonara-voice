#!/usr/bin/env python3
"""Sonara VO: turn a script into a voiceover MP3 (plus SRT captions) for Reels.

Engine: Microsoft Edge neural voices via the free `edge-tts` package.
ffmpeg is optional but recommended: it adds real pauses and evens out loudness.

Usage:
  python sonara_vo.py list
  python sonara_vo.py say -v ardi -i naskah.txt -o vo.mp3 --srt
  python sonara_vo.py say -v ryan -t "A quick line of text." -o line.mp3
  python sonara_vo.py say -v ardi -i naskah.txt -o reel/vo.mp3 --words --json reel/vo.json
  python sonara_vo.py samples
  python sonara_vo.py check

Script markup (all optional):
  blank line        pause between paragraphs (default 0.6 s)
  [jeda] [pause]    short pause (0.5 s); [jeda 1.2] sets the length in seconds
  [cepat] [pelan]   speak the following text faster or slower; [normal] resets
  [suara gadis]     switch to another voice for the following text (dialogue)
  # comment         lines starting with # are ignored (shot notes, visuals)
"""
import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Run: pip install edge-tts")

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "sonara-voices.json"
PARAGRAPH_PAUSE = 0.6
TAG_PAUSE = 0.5
SPEED = {"cepat": 10, "fast": 10, "pelan": -12, "slow": -12, "normal": 0}
SAMPLE_TEXT = {
    "id": "Pernah kepikiran nggak, kenapa langit warnanya biru? Jawabannya ternyata ada di cahaya matahari, yang terdiri dari banyak sekali warna.",
    "jv": "Sugeng enjang, para sedulur. Dina iki kita bakal sinau bab sejarah candhi Borobudur.",
    "su": "Wilujeng enjing, dulur-dulur. Dinten ieu urang bakal diajar ngeunaan sajarah Gunung Tangkuban Parahu.",
    "en": "Have you ever wondered why the sky is blue? The answer is hiding in sunlight, which is made of many different colours.",
}
HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return {v["id"]: v for v in json.load(f)["voices"]}


def find_voice(catalog, key):
    key = key.lower().strip()
    if key in catalog:
        return catalog[key]
    for v in catalog.values():
        if key in (v["name"].lower(), v["engine_voice"].lower()):
            return v
    sys.exit(f"Unknown voice '{key}'. Run `python sonara_vo.py list` to see the voices.")


def pct(value):
    return int(str(value).replace("%", "") or 0)


def parse_script(text):
    """Split the script into ('speak', text, speed, voice_key, scene) and ('pause', seconds) parts.

    Each paragraph is one scene; voice_key is None until a [suara x] tag switches voice.
    """
    parts, speed, voice_key = [], 0, None
    lines = [l for l in text.splitlines() if not l.lstrip().startswith("#")]
    paragraphs = re.split(r"\n\s*\n", "\n".join(lines))
    for p_index, para in enumerate(paragraphs):
        if p_index and parts and parts[-1][0] != "pause":
            parts.append(("pause", PARAGRAPH_PAUSE))
        for token in re.split(r"(\[[^\]]+\])", para):
            tag = re.fullmatch(r"\[\s*([a-zA-Z]+)\s*([\w.-]+)?\s*\]", token.strip())
            if tag:
                name, arg = tag.group(1).lower(), tag.group(2)
                if name in ("jeda", "pause"):
                    try:
                        parts.append(("pause", float(arg) if arg else TAG_PAUSE))
                    except ValueError:
                        print(f"  note: [{name} {arg}] needs a number of seconds and was skipped", file=sys.stderr)
                elif name in ("suara", "voice") and arg:
                    voice_key = arg.lower()
                elif name in SPEED:
                    speed = SPEED[name]
                else:
                    print(f"  note: tag [{name}] is not supported and was skipped", file=sys.stderr)
                continue
            clean = " ".join(token.split())
            if clean:
                parts.append(("speak", clean, speed, voice_key, p_index))
    while parts and parts[-1][0] == "pause":
        parts.pop()
    return parts


async def synth(text, voice, rate, pitch, path, boundary, proxy, tries=3):
    for attempt in range(1, tries + 1):
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary=boundary, proxy=proxy)
            marks = []
            with open(path, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                        marks.append((chunk["offset"] / 1e7, (chunk["offset"] + chunk["duration"]) / 1e7, chunk["text"]))
            return marks
        except Exception as e:  # network hiccups are common; retry a couple of times
            if attempt == tries:
                raise RuntimeError(f"Speech service failed after {tries} tries: {e}") from e
            await asyncio.sleep(1.5 * attempt)


def duration(path, fallback):
    if not HAS_FFMPEG:
        return fallback
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else fallback


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n\n")


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


async def render(script, voice, out, rate=None, pitch=None, srt=False, words=False, proxy=None, quiet=False, catalog=None):
    parts = parse_script(script)
    if not any(p[0] == "speak" for p in parts):
        sys.exit("The script has no text to speak.")
    catalog = catalog or load_catalog()
    # resolve every [suara x] tag up front so a typo fails before anything is rendered
    voices = {k: find_voice(catalog, k) for k in {p[3] for p in parts if p[0] == "speak" and p[3]}}
    boundary = "WordBoundary" if words else "SentenceBoundary"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cues, scenes, t = [], {}, 0.0

    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for i, part in enumerate(parts):
            if part[0] == "pause":
                if HAS_FFMPEG:
                    sil = Path(tmp) / f"{i:03}_pause.mp3"
                    ffmpeg("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", f"{part[1]:.2f}", "-c:a", "libmp3lame", "-b:a", "48k", str(sil))
                    files.append(sil)
                t += part[1] if HAS_FFMPEG else 0
                continue
            _, text, speed, key, scene = part
            v = voices[key] if key else voice
            # an explicit --rate/--pitch applies to the main voice only; switched voices keep their own delivery
            r = pct(rate if (rate is not None and v is voice) else v["rate"]) + speed
            p = (pitch if v is voice else None) or v["pitch"]
            seg = Path(tmp) / f"{i:03}.mp3"
            if not quiet:
                who = f"[{v['name']}] " if key else ""
                print(f"  speaking: {who}{text[:70]}{'…' if len(text) > 70 else ''}")
            marks = await synth(text, v["engine_voice"], f"{r:+d}%", p, seg, boundary, proxy)
            cues += [(t + a, t + b, txt) for a, b, txt in marks]
            start = t
            t += duration(seg, marks[-1][1] if marks else 0)
            sc = scenes.setdefault(scene, {"scene": len(scenes) + 1, "start": start, "text": [], "voices": []})
            sc["end"], sc["text"] = t, sc["text"] + [text]
            if v["id"] not in sc["voices"]:
                sc["voices"].append(v["id"])
            files.append(seg)

        if HAS_FFMPEG:
            listing = Path(tmp) / "list.txt"
            listing.write_text("".join(f"file '{f.as_posix()}'\n" for f in files))
            # concatenate, then level to -14 LUFS, the usual target for Reels and TikTok
            ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing),
                   "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(out))
        else:
            with open(out, "wb") as dst:
                for f in files:
                    dst.write(f.read_bytes())
            if any(p[0] == "pause" for p in parts):
                print("  note: ffmpeg not found, so pauses were skipped. Install ffmpeg for pauses and loudness levelling.", file=sys.stderr)

    if srt or words:
        write_srt(cues, out.with_suffix(".srt"))
    scene_list = [dict(s, start=round(s["start"], 2), end=round(s["end"], 2),
                       duration=round(s["end"] - s["start"], 2), text=" ".join(s["text"])) for s in scenes.values()]
    return out, t, scene_list


def cmd_list(catalog, _args):
    print(f"{'id':<13}{'accent':<11}{'gender':<8}style")
    for v in catalog.values():
        flag = " (experimental)" if v.get("experimental") else ""
        print(f"{v['id']:<13}{v['accent']:<11}{v['gender']:<8}{v['style']}{flag}")


def cmd_say(catalog, args):
    voice = find_voice(catalog, args.voice)
    if args.text:
        script = args.text
    elif args.input:
        script = Path(args.input).read_text(encoding="utf-8")
    else:
        script = sys.stdin.read()
    out, secs, scenes = asyncio.run(render(script, voice, args.output, args.rate, args.pitch, args.srt, args.words, args.proxy, catalog=catalog))
    extra = f" + {out.with_suffix('.srt').name}" if (args.srt or args.words) else ""
    if args.json:
        used = sorted({v for s in scenes for v in s["voices"]}, key=lambda k: list(catalog).index(k))
        info = {
            "tool": "sonara-vo", "engine": "edge-tts", "ai_voice": True,
            "voice": voice["id"], "voices_used": [{"id": k, "name": catalog[k]["name"], "engine_voice": catalog[k]["engine_voice"]} for k in used],
            "audio": out.name, "captions": out.with_suffix(".srt").name if (args.srt or args.words) else None,
            "duration": round(secs, 2), "scenes": scenes,
        }
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        extra += f" + {Path(args.json).name}"
    print(f"Saved {out}{extra} · {voice['name']} · about {secs:.1f} s · {len(scenes)} scenes")


def cmd_samples(catalog, args):
    folder = Path(args.output or HERE / "samples")
    for v in catalog.values():
        path = folder / f"{v['id']}.mp3"
        try:
            asyncio.run(render(SAMPLE_TEXT[v["lang"]], v, path, proxy=args.proxy, quiet=True))
            print(f"  ok  {path}")
        except Exception as e:
            print(f"  failed  {v['id']}: {e}")


def cmd_check(catalog, args):
    available = {v["ShortName"] for v in asyncio.run(edge_tts.list_voices(proxy=args.proxy))}
    missing = [v["id"] for v in catalog.values() if v["engine_voice"] not in available]
    print("All Sonara voices are available." if not missing else "Missing from the engine: " + ", ".join(missing))


def main():
    ap = argparse.ArgumentParser(description="Sonara VO: script to voiceover")
    ap.add_argument("--proxy", default=os.environ.get("SONARA_PROXY"), help="HTTP proxy for the speech service, if your network needs one")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="show the voices")
    s = sub.add_parser("say", help="render a script to MP3")
    s.add_argument("-v", "--voice", default="ardi")
    s.add_argument("-i", "--input", help="script file (UTF-8 text)")
    s.add_argument("-t", "--text", help="text to speak instead of a file")
    s.add_argument("-o", "--output", default="vo.mp3")
    s.add_argument("--rate", help="override speed, e.g. +8%% or -5%%")
    s.add_argument("--pitch", help="override pitch, e.g. +2Hz or -3Hz")
    s.add_argument("--srt", action="store_true", help="also write sentence captions (.srt)")
    s.add_argument("--words", action="store_true", help="write word-by-word captions (.srt) for animated Reels subtitles")
    s.add_argument("--json", help="write a vo.json with voices used and per-scene timings")
    sm = sub.add_parser("samples", help="render one sample per voice so the team can listen and choose")
    sm.add_argument("-o", "--output", help="folder (default: samples/)")
    sub.add_parser("check", help="confirm every preset still exists in the engine")
    args = ap.parse_args()
    catalog = load_catalog()
    {"list": cmd_list, "say": cmd_say, "samples": cmd_samples, "check": cmd_check}[args.cmd](catalog, args)


if __name__ == "__main__":
    main()
