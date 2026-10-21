# Sonara

Demo landing page for a fictional voice AI platform, inspired by modern AI voice sites.

- 27 voice samples in native Indonesian, Javanese-accented Indonesian, British and American English
- "Type your own" mode using the browser's built-in speech engine, matched to the chosen accent
- Single static `index.html`, no build step

Voice clips are the public preview recordings from the ElevenLabs voice library. Sonara is not a real company.

## Voice IDs for agents

`voices.json` lists every voice with its ElevenLabs `voice_id`, accent and style, so an agent can pick a voice by accent and pass the id to text-to-speech (model `eleven_v4`).
