# Hindi Grammar Production (Note Type)

Schema, layout, and template sync guide for the **`Hindi Grammar Production`** Anki Cloze note type. Mirrors [`Japanese Grammar Production`](../japanese-grammar/README.md) and [`French Grammar Production`](../french-grammar/README.md) for progressive Hindi grammar production with Devanagari passive exposure and native `hi_IN` TTS. For deck rules and curriculum, see [`decks/hindi-grammar/README.md`](../../decks/hindi-grammar/README.md).

## Model & Templates

- **Anki Model:** `Hindi Grammar Production` (Cloze)
- **Template:** `Grammar Production` (`front.html`, `back.html`, `styling.css`)
- **Sync to Anki:**

```bash
python3 note-types-templates/hindi-grammar/sync.py --install-starter --dry-run
python3 note-types-templates/hindi-grammar/sync.py --install-starter
```

## Card Layout

- **Front:** `SentenceEnglish` → dimmed romanized `SentenceCloze` (with `c1` cloze) → bordered `Cue`
- **Back:** `SentenceEnglish` → revealed romanized `SentenceCloze` → Devanagari `Sentence` → transparent `.answer-details` section:
  1. `Lesson · GrammarPoint` (muted header; deduplicates automatically when identical)
  2. `Explanation` + optional `ExplanationDetail`
  3. `Target → Answer （AnswerDevanagari）` (`Target →` auto-hides when `Target == Answer`)
  4. Top divider + `Notes` (Japanese SOV / Spanish parallels and memory hooks)
  5. `NativeTTS` (`hi_IN` TTS replay button on Devanagari `Sentence`, or `SentenceAudio` fallback)

## Fields

| Field | Role in Template |
|---|---|
| `SentenceCloze` | 1st field (duplicate key). Romanized Hindi with one `{{c1::...}}` cloze around `Answer`. |
| `Lesson` | Displayed in `.lesson-header` (e.g., `1.1 Copula honā`, `1.2 Postpositions`). |
| `Sequence` | Numeric ordering metadata (`1`, `2`, …). |
| `GrammarPoint` | Displayed after `·` in `.lesson-header` (hidden if equal to `Lesson`). |
| `Pattern` | Structural rule metadata. |
| `SentenceEnglish` | English prompt displayed at top of front and back. |
| `Sentence` | Devanagari Hindi sentence (shown on back and spoken by `NativeTTS` `hi_IN`). |
| `Cue` | Front-side bordered transformation hint (must not spoil `Answer`). |
| `Target` | Left side of `.transformation` (hidden if equal to `Answer`). |
| `Answer` | Bolded right side of `.transformation` (romanized). |
| `AnswerDevanagari` | Muted Devanagari form in parentheses `（...）` beside `Answer`. |
| `TargetClass` | Classification metadata. |
| `Explanation` | Primary 1-line grammar rule below `.lesson-header`. |
| `ExplanationDetail` | Optional smaller, muted breakdown below `Explanation`. |
| `Notes` | Secondary block below a top divider (Japanese SOV / Spanish bridges, HTML `<b>`, `<i>`). |
| `SentenceAudio` | Fallback audio when `NativeTTS` is empty. |
| `NativeTTS` | Non-empty value (e.g., `"1"`) enables Anki's built-in `hi_IN` TTS on `Sentence`. |
| `TargetFrequency` | Optional frequency metadata. |
| `Source` | Unique stable note identifier for idempotent syncing (e.g., `hi-p1-001`). |
