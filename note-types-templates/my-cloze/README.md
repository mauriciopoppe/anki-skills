# My Cloze (Note Type)

Generic Cloze note type shared across multiple language decks. For language-specific prompts and field mappings, see the deck playbooks (e.g., [`decks/french-cloze/README.md`](../../decks/french-cloze/README.md), [`decks/hindi-cloze/README.md`](../../decks/hindi-cloze/README.md)).

## Model & Templates

- **Anki Model:** `My Cloze` (Cloze)
- **Template:** `Cloze` (`front.html`, `back.html`, `styling.css`)
- **Sync to Anki:**

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/my-cloze/front.html)" \
  --arg b "$(cat note-types-templates/my-cloze/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "My Cloze", templates: {Cloze: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/my-cloze/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "My Cloze", css: $s}}}')"
```

## Card Layout

- **Front:** `{{cloze:Expression}}`
- **Back:** `{{cloze:Expression}}` → optional `ExpressionFurigana` (rendered with `{{furigana:...}}`) → optional `ExpressionSpanish` → optional `ExpressionEnglish` → optional `Notes` → optional `Glossary` → optional `Image` → `Tags`

## Fields

| Field | Role in Template |
|---|---|
| `Expression` | 1st field (Cloze source). Contains `{{c1::target::hint}}` markup. |
| `ExpressionEnglish` | Optional English translation shown on back. |
| `ExpressionSpanish` | Optional Spanish translation shown on back. |
| `ExpressionFurigana` | Optional Japanese furigana translation (`漢字[よみ]`) shown on back. |
| `Frequency` | Numeric frequency metadata (used for sorting; not rendered on card). |
| `Notes` | Optional explanation/notes box on back (supports HTML). |
| `Glossary` | Optional reference definitions box on back. |
| `Image` | Optional visual media on back. |
