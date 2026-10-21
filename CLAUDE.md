# Sonara VO: guide for agents

This repo holds two things:

- `index.html`: the Sonara demo website (GitHub Pages). Its voice library plays ElevenLabs preview clips and cannot generate speech.
- `sonara_vo.py`: the Sonara VO tool. It turns a script into an MP3 voiceover plus captions, for free, using Microsoft Edge neural voices (`edge-tts`). Use this to make VO for Curioverse Reels (team Layar).

Do not generate VO with paid services (ElevenLabs or others) unless the user asks for it by name. The team wants free tools first.

## Setup (once per machine)

```bash
pip install -r requirements.txt     # edge-tts
# ffmpeg is recommended: real pauses + loudness levelled to -14 LUFS for Reels
#   macOS: brew install ffmpeg   ·   Ubuntu: sudo apt install ffmpeg   ·   Windows: winget install ffmpeg
python sonara_vo.py check           # confirms every voice preset still exists
```

The tool needs internet access to `speech.platform.bing.com`. Behind a proxy, set `SONARA_PROXY=http://host:port`.

## Making a Curioverse VO

1. **Write or take the script.** Save it as UTF-8 text, e.g. `output/2026-10-21-langit-biru.txt`. See `contoh/naskah-langit-biru.txt`.
2. **Pick the voice.** Default is `ardi` (Indonesian male narrator). `gadis` for a female narrator. Run `python sonara_vo.py list` for all voices. Only use a voice whose language matches the script: `ardi`/`gadis` for Indonesian, `ryan`/`sonia`/`libby`/`thomas` for British English, `andrew`/`ava`/`brian`/`emma` for American English. Javanese and Sundanese voices are experimental.
3. **Render:**
   ```bash
   python sonara_vo.py say -v ardi -i output/2026-10-21-langit-biru.txt -o output/2026-10-21-langit-biru.mp3 --words
   ```
   `--words` writes a word-by-word `.srt` for animated Reels captions; `--srt` writes sentence captions instead.
   Add `--json output/<name>.json` to record the voices used and each scene's start, end and duration (one paragraph = one scene). The Curioverse skill uses this as `vo.json`.
4. **Check the length.** The command prints the duration. Reels VO usually runs 30–60 s, which is roughly 75–150 Indonesian words. Trim the script if it runs long rather than speeding up past `--rate +12%`.
5. **Deliver** the `.mp3` and `.srt` paths to the user. `output/` is git-ignored; do not commit renders.

## Writing scripts that sound human

The engine reads exactly what is written, so the script decides how natural the VO sounds.

- Write the way people talk: short sentences, everyday words (*nggak, kayak, banget, nah, ternyata*). Avoid formal written phrasing like *adapun* or *merupakan*.
- One idea per sentence. Put the hook first, then `[jeda]` so it lands.
- Use punctuation for rhythm: commas for small breaths, `…` for a beat, `?` and `!` for intonation.
- `[jeda]` (0.5 s) or `[jeda 1.2]` for a set pause; a blank line between paragraphs adds 0.6 s.
- `[pelan]` before a key line, `[cepat]` for a quick aside, `[normal]` to reset. Speed carries over to later paragraphs until `[normal]`.
- `[suara gadis]` switches voice for the text that follows, for dialogue. `[suara ardi]` switches back. Keep each voice in its own language.
- Lines starting with `#` are ignored, so shot notes can stay in the script.
- Spell out anything the voice might misread: acronyms (*Ka-Pe-Ka* if it must be letters), foreign names, and units (*kilometer*, not *km*).
- Emotion tags like `[tertawa]` or `[berbisik]` are not supported by this engine and are skipped with a note.

## If it fails

- `Speech service failed`: usually a network block or a temporary outage. Retry once; if it still fails, tell the user. Do not switch to a paid engine on your own.
- `Unknown voice`: check the id with `python sonara_vo.py list`.
- No pauses in the output: ffmpeg is missing.
