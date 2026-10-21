# Sonara

Free voiceover tool and demo site for the Curioverse Reels team (Layar).

## Sonara VO (the tool)

`sonara_vo.py` turns a script into an MP3 voiceover plus word-by-word captions. It uses free Microsoft Edge neural voices through [`edge-tts`](https://github.com/rany2/edge-tts), with no API key and no credits.

```bash
pip install -r requirements.txt
python sonara_vo.py list                                   # voices
python sonara_vo.py say -v ardi -i contoh/naskah-langit-biru.txt -o output/langit-biru.mp3 --words
python sonara_vo.py samples                                # one sample per voice in samples/
```

Voices (`sonara-voices.json`): Indonesian (Ardi, Gadis), British (Ryan, Sonia, Libby, Thomas), American (Andrew, Ava, Brian, Emma), plus experimental Javanese and Sundanese voices.

Script markup: blank line = paragraph pause, `[jeda]` / `[jeda 1.2]` = pause, `[pelan]` / `[cepat]` / `[normal]` = speed, `[suara gadis]` = switch voice (dialogue), `# ...` = ignored note. `--json` writes per-scene timings. ffmpeg is optional but adds real pauses and levels loudness to -14 LUFS.

See `CLAUDE.md` for the full workflow and script-writing tips. Claude agents read that file automatically.

**Limits.** `edge-tts` uses Microsoft's Edge read-aloud service, which has no official public API. It is free and works well today, but Microsoft could change or block it, and commercial use is not clearly covered by their terms. For guaranteed licensing, swap the engine for a paid service later. The script format stays the same.

## Curioverse skill

`skill/reels-curioverse-harian/SKILL.md` is the Reels skill updated to use Sonara VO instead of ElevenLabs. Upload it to claude.ai to replace the current version.

## Demo website

`index.html` is a landing page for the fictional Sonara brand, served with GitHub Pages. Its voice library plays the public preview recordings from the ElevenLabs voice library (listed in `demo-voices-elevenlabs.json`). These are different voices from the Sonara VO tool, and the site cannot generate speech. Sonara is not a real company.
