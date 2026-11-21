---
name: anki-add-audio
description: Generate local text-to-speech audio for empty Anki fields on macOS using a system voice and FFmpeg. Use to add or backfill pronunciation or sentence audio without cloud TTS.
---

# Anki Add Audio

Generate MP3 audio locally, store it through AnkiConnect, and fill only empty destination fields.

## Native TTS preference

When the card template and review clients support Anki's built-in text-to-speech, mention that option first. Native TTS uses a `{{tts ...}}` template replacement and avoids adding audio media to notes. This skill still performs its normal local synthesis and field update when the user explicitly wants stored audio, consistent audio across devices, offline playback, or a deck that does not use native TTS.

## Requirements

- macOS `say`, an installed voice, FFmpeg, and a running AnkiConnect.
- List voices with `say -v '?'`; the default is Japanese voice `Kyoko`.

## Parameters

- `--deck`: Required deck name.
- `--source-field`: Text to speak; default `Sentence`.
- `--target-field`: Audio field; default `SentenceAudio`.
- `--voice`: macOS voice; default `Kyoko`.
- `--rate`: Speaking rate; default `175`.
- `--limit`: Maximum notes; default `20`.
- `--sort-field`: Numeric ordering field; default `Frequency`.
- `--interactive`: Approve each note.
- `--dry-run`: Preview without writes.
- `--yes`: Approve a non-interactive batch larger than 10 notes.

## Workflow

1. Run `scripts/anki_add_audio.py` with `--dry-run` and report the preview.
2. Confirm authorization for the reported Anki update.
3. Run without `--dry-run`; use `--interactive` for per-note review.
4. Report updated and skipped counts.

```bash
python3 skills/anki-add-audio/scripts/anki_add_audio.py \
  --deck "Language Japanese::Grammar" --limit 3 --dry-run
```

## Invariants

- Never overwrite non-empty target fields.
- Validate source and target fields first.
- Keep synthesis local; never substitute cloud TTS silently.
- Normalize HTML, Cloze, and Anki furigana; prefer supplied readings.
- Use deterministic filenames and tag updated notes with `anki_audio` and date.
