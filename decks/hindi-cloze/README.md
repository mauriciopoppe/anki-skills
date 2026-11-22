# Hindi Cloze Deck

Augmentation and content playbook for a Hindi cloze vocabulary/phrases deck (e.g., `Language Hindi::Mining`).

- **Note Type:** [`My Cloze`](../../note-types-templates/my-cloze/README.md)
- **Companion Prompts:**
  - Explanations: [`prompts/explain_en_prompt.txt`](../../prompts/explain_en_prompt.txt)
  - Translations: [`prompts/translate_en_prompt.txt`](../../prompts/translate_en_prompt.txt), [`prompts/translate_ja_prompt.txt`](../../prompts/translate_ja_prompt.txt)
- **Companion Skills:** `anki-add-frequency`, `anki-add-notes`, `anki-backup-deck`

## Field Mapping & Pipeline

| Step | Skill | Target Field | Prompt / Notes |
|---|---|---|---|
| 1. Backup | `anki-backup-deck` | — | Run before large batch updates. |
| 2. Frequency | `anki-add-frequency` | `Frequency` | Conversational frequency (`1`–`1000`). |
| 3. Explanations | `anki-add-notes` | `Notes` | `prompts/explain_en_prompt.txt` (<40 words, no full translation). |
| 4. Japanese Translation | `anki-add-notes` | `ExpressionFurigana` | `prompts/translate_ja_prompt.txt` (natural Japanese with Anki furigana). |
| 5. English Translation | `anki-add-notes` | `ExpressionEnglish` | `prompts/translate_en_prompt.txt` (strips cloze markers). |

## Safety Rules

- Only populate empty target fields; never overwrite existing study material.
- Sort candidates by `Frequency` before applying `--limit`.
