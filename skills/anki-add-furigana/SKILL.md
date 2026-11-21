---
name: anki-add-furigana
description: Generate or repair Japanese furigana fields in Anki using contextual readings while preserving native Cloze markup. Use when Japanese cards need complete Anki furigana or a clean sentence must be converted into a furigana-and-Cloze display field.
---

# Anki Add Furigana

Generate Japanese furigana with Fugashi and UniDic, then update an Anki field
through AnkiConnect. The script takes a clean sentence and an exact answer
substring, then writes one furigana-bearing native Cloze to the destination
field. The card template must apply the filters as
`{{furigana:cloze:SentenceFurigana}}`.

## Requirements

- Python 3.9+
- `fugashi` and `unidic-lite` (`python3 -m pip install -r requirements.txt`)
- Anki running with AnkiConnect at `http://localhost:8765`
- A Japanese sentence field and an answer field on the selected note type

## Parameters

- `--deck`: Required Anki deck name.
- `--model`: Optional Anki note type filter.
- `--source-field`: Clean Japanese sentence input; defaults to `Sentence`.
- `--answer-field`: Exact answer substring input; defaults to `Answer`.
- `--target-field`: Furigana-and-Cloze output field; defaults to `SentenceFurigana`.
- `--limit`: Maximum notes to inspect.
- `--interactive` / `-i`: Approve each changed note before updating.
- `--dry-run`: Print generated values without changing Anki.
- `--yes`: Allow a non-interactive batch larger than 10 notes.

## Workflow

1. Run a dry run and inspect representative readings, especially compounds and
   words with multiple valid pronunciations.
2. Confirm that the generated text still represents the clean source sentence,
   contains one balanced native Cloze, and includes furigana inside the
   answer.
3. For a small batch, run the script without `--dry-run`. For more than ten
   changes, use `--interactive` or explicitly pass `--yes`.
4. Review the rendered question and answer in Anki after applying changes.

```bash
python3 skills/anki-add-furigana/scripts/generate_furigana.py \
  --deck "Language Japanese::Grammar" \
  --model "Japanese Grammar Production" \
  --limit 3 \
  --dry-run
```

The script reads the source and answer fields and updates only the target field.
It batches accepted writes through AnkiConnect's `multi` action. It may replace
an existing target field because this skill repairs incomplete or malformed
furigana; always use `--dry-run` before a broad update.
