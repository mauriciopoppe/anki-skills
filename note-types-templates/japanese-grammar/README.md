# Japanese Grammar Production (Note Type)

Schema, layout, and template sync guide for the **`Japanese Grammar Production`** Anki Cloze note type. For deck-specific card-creation rules and prompts, see [`decks/japanese-grammar/README.md`](../../decks/japanese-grammar/README.md).

## Model & Templates

- **Anki Model:** `Japanese Grammar Production` (Cloze)
- **Template:** `Grammar Production` (`front.html`, `back.html`, `styling.css`)
- **Sync to Anki:**

```bash
python3 note-types-templates/japanese-grammar/sync.py
```

## Card Layout

- **Front:** `SentenceEnglish` → dimmed `SentenceFurigana` (with `c1` cloze; furigana `<rt>` hidden by default, hover/tap to peek) → `Cue`
- **Back:** `SentenceEnglish` → revealed `SentenceFurigana` → transparent `.answer-details` section:
  1. `Lesson · GrammarPoint` (muted header; deduplicates automatically when identical)
  2. `Explanation`
  3. `Target → Answer （AnswerReading）` (`Target →` auto-hides when `Target == Answer`)
  4. Top divider + `Notes`
  5. `NativeTTS` (or `SentenceAudio` fallback when `NativeTTS` is empty)

## Fields

| Field | Role in Template |
|---|---|
| `SentenceFurigana` | 1st field (duplicate key). Rendered via `{{furigana:cloze:SentenceFurigana}}`. Expects Anki furigana (`漢字[よみ]`) and one `{{c1::...}}` cloze around `Answer`, with a space before kanji chunks preceded by kana. |
| `Lesson` | Displayed in `.lesson-header`. |
| `Sequence` | Numeric ordering metadata. |
| `GrammarPoint` | Displayed after `·` in `.lesson-header` (hidden if equal to `Lesson`). |
| `Pattern` | Structural metadata (not rendered on card). |
| `SentenceEnglish` | Prompt sentence displayed at top of front and back. |
| `Sentence` | Plain Japanese text (no furigana/HTML/cloze); spoken by `NativeTTS`. |
| `Cue` | Front-side bordered hint box. |
| `Target` | Left side of `.transformation` (hidden if equal to `Answer`). |
| `TargetReading` | Reading metadata for `Target`. |
| `Answer` | Bolded right side of `.transformation`. |
| `AnswerReading` | Muted reading in parentheses `（...）` beside `Answer`. |
| `TargetClass` | Classification metadata (not rendered on card). |
| `Explanation` | Primary explanation text below `.lesson-header`. |
| `Notes` | Secondary block below a top divider (supports HTML `<b>`, `<i>`, `<br>`, `<p>`). |
| `SentenceAudio` | Fallback audio when `NativeTTS` is empty. |
| `TargetFrequency` | Frequency metadata. |
| `Source` | Unique stable note identifier for idempotent syncing. |
| `NativeTTS` | Non-empty value (e.g., `"1"`) enables Anki's built-in `ja_JP` TTS on `Sentence`. |

## Furigana Helper

[`anki-add-furigana`](../../skills/anki-add-furigana/SKILL.md) uses Fugashi with UniDic to populate `SentenceFurigana` from `Sentence` and `Answer`:

```sh
python3 -m pip install -r requirements.txt
python3 skills/anki-add-furigana/scripts/generate_furigana.py \
  --deck "Language Japanese::Grammar" \
  --model "Japanese Grammar Production" \
  --source-field Sentence \
  --answer-field Answer \
  --target-field SentenceFurigana \
  --dry-run
```

Remove `--dry-run` only after reviewing the preview. It updates only `SentenceFurigana`.
