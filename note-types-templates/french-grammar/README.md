# French Grammar Production (Note Type)

Schema, layout, and template sync guide for the **`French Grammar Production`** Anki Cloze note type. Mirrors [`Japanese Grammar Production`](../japanese-grammar/README.md) for progressive French grammar production tailored to Spanish native speakers. For deck rules and promotion workflows, see [`decks/french-grammar/README.md`](../../decks/french-grammar/README.md).

## Model & Templates

- **Anki Model:** `French Grammar Production` (Cloze)
- **Template:** `Grammar Production` (`front.html`, `back.html`, `styling.css`)
- **Sync to Anki:**

```bash
python3 note-types-templates/french-grammar/sync.py
```

To install or update the grammar packs in `Language French::Grammar`:

```bash
python3 note-types-templates/french-grammar/sync.py --install-all --dry-run
python3 note-types-templates/french-grammar/sync.py --install-all
```

Individual packs: `--install-starter` (`starter_notes.json`, Phase 1 Seq 1–50) and `--install-phase2` (`phase2_notes.json`, Phase 2 + `en`/`y` Seq 51–87).

## Card Layout

- **Front:** `SentenceSpanish` → dimmed `SentenceCloze` (with `c1` cloze) → bordered `Cue`
- **Back:** `SentenceSpanish` → revealed `SentenceCloze` → transparent `.answer-details` section:
  1. `Lesson · GrammarPoint` (muted header; deduplicates automatically when identical)
  2. `Explanation` + optional `ExplanationDetail`
  3. `Target → Answer` (`Target →` auto-hides when `Target == Answer`)
  4. Top divider + `Notes` (Spanish-vs-French trap or memory hook)
  5. `NativeTTS` (`fr_FR` TTS replay button on `Sentence`, or `SentenceAudio` fallback)

## Fields

| Field | Role in Template |
|---|---|
| `SentenceCloze` | 1st field (duplicate key). Rendered via `{{cloze:SentenceCloze}}`. Contains one `{{c1::...}}` cloze around `Answer`. |
| `Lesson` | Displayed in `.lesson-header` (e.g., `1.1 Partitive & Negation`, `2.1 Futur Simple`). |
| `Sequence` | Numeric ordering metadata (`1`, `2`, …). |
| `GrammarPoint` | Displayed after `·` in `.lesson-header` (hidden if equal to `Lesson`). |
| `Pattern` | Structural rule metadata (not rendered directly on card). |
| `SentenceSpanish` | Spanish prompt displayed at top of front and back. |
| `Sentence` | Plain French text (no HTML/cloze); spoken by `NativeTTS`. |
| `Cue` | Front-side bordered transformation hint (must not spoil `Answer`). |
| `Target` | Left side of `.transformation` (hidden if equal to `Answer`). |
| `Answer` | Bolded right side of `.transformation`. |
| `TargetClass` | Classification metadata (e.g., `Grammar`, `Irregular Stem`). |
| `Explanation` | Primary 1-line Spanish grammar rule below `.lesson-header`. |
| `ExplanationDetail` | Optional smaller, muted pattern breakdown below `Explanation`. |
| `Notes` | Secondary block below a top divider (Spanish-vs-French traps, HTML `<b>`, `<i>`). |
| `SentenceAudio` | Fallback audio when `NativeTTS` is empty. |
| `NativeTTS` | Non-empty value (e.g., `"1"`) enables Anki's built-in `fr_FR` TTS on `Sentence`. |
| `TargetFrequency` | Optional frequency metadata. |
| `Source` | Unique stable note identifier for idempotent syncing (e.g., `fr-p1-001`). |
