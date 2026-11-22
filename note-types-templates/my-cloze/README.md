# My Cloze (Note Type)

Generic Cloze note type shared across multiple language decks. For language-specific prompts and field mappings, see the deck playbooks (e.g., [`decks/french-cloze/README.md`](../../decks/french-cloze/README.md), [`decks/hindi-cloze/README.md`](../../decks/hindi-cloze/README.md)).

## Model & Templates

- **Anki Model:** `My Cloze` (Cloze)
- **Template:** `Cloze` (`front.html`, `back.html`, `styling.css`)
- **Sync to Anki:**

```bash
python3 note-types-templates/my-cloze/sync.py
```

To also enable French native TTS (`NativeTTS=1`) on the French deck:

```bash
python3 note-types-templates/my-cloze/sync.py --enable-native-tts --dry-run
python3 note-types-templates/my-cloze/sync.py --enable-native-tts
```

## Card Layout

- **Front:** `{{cloze:Expression}}`
- **Back:** `{{cloze:Expression}}` → optional translations (`ExpressionFurigana`, `ExpressionSpanish`, `ExpressionEnglish`) → transparent `.answer-details` section (optional `Notes` → optional `Glossary` → optional `Image`) → optional `NativeTTS` French replay button (`fr_FR` on `cloze:Expression`) → optional `Tags`

## Fields

| Field | Role in Template |
|---|---|
| `Expression` | 1st field (Cloze source). Contains `{{c1::target::hint}}` markup. |
| `ExpressionEnglish` | Optional English translation shown on back. |
| `ExpressionSpanish` | Optional Spanish translation shown on back. |
| `ExpressionFurigana` | Optional Japanese furigana translation (`漢字[よみ]`) shown on back. |
| `Frequency` | Numeric frequency metadata (used for sorting; not rendered on card). |
| `Notes` | Optional explanation/notes section on back (supports HTML). |
| `Glossary` | Optional reference definitions section on back. |
| `Image` | Optional visual media on back. |
| `NativeTTS` | Non-empty value (e.g., `"1"`) enables Anki's built-in `fr_FR` TTS replay button on `{{cloze:Expression}}` (back side). Leave empty on non-French decks. |
