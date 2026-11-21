# Lapis (Note Type)

Schema, layout, and template sync guide for the **`Lapis`** Anki note type. For deck-specific augmentation workflows, see [`decks/japanese-mining/README.md`](../../decks/japanese-mining/README.md).

## Model & Templates

- **Anki Model:** `Lapis`
- **Templates:**
  - `Comprehension` (`front_comprehension.html`, `back_comprehension.html`)
  - `Production` (`front_production.html`, `back_production.html`)
  - Shared stylesheet: `styling.css`
- **Sync to Anki:**

```bash
python3 note-types-templates/lapis/sync.py
```

## Key Fields

| Field | Role in Template |
|---|---|
| `Expression` | Target word/phrase (front of `Comprehension`, back of `Production`). |
| `ExpressionFurigana` | Target with Anki furigana (`漢字[よみ]`). |
| `ExpressionReading` | Hiragana reading of `Expression`. |
| `Sentence` | Contextual example sentence (`{{kanji:Sentence}}` on front, full HTML with `<b>` highlight on back; also used for native `ja_JP` TTS). |
| `SentenceEnglish` | English translation of `Sentence`. |
| `MainDefinition` / `Glossary` | Primary definition and collapsible/full glossary. |
| `Hint` / `SelectionText` | Optional front hint or highlighted selection. |
| `IsWordAndSentenceCard` / `IsClickCard` / `IsSentenceCard` | Display-mode toggles controlling front layout. |
| `PitchPosition` / `PitchCategories` | Pitch-accent rendering metadata. |
| `Frequency` | Frequency rank badge and sort key. |
| `Notes` | Secondary study/mnemonic notes block (supports HTML). |
| `ExpressionAudio` / `SentenceAudio` / `Picture` / `DefinitionPicture` | Optional media fields. |
