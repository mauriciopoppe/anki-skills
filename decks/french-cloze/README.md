# French Cloze Deck

Augmentation and content playbook for a French cloze vocabulary/phrases deck (e.g., `Language French::Mining`).

- **Note Type:** [`My Cloze`](../../note-types-templates/my-cloze/README.md)
- **Companion Prompts:**
  - Explanations: [`prompts/explain_es_prompt.txt`](../../prompts/explain_es_prompt.txt) (or [`prompts/explain_fr_prompt.txt`](../../prompts/explain_fr_prompt.txt))
  - Translations: [`prompts/translate_es_prompt.txt`](../../prompts/translate_es_prompt.txt)
- **Companion Skills:** `anki-add-frequency`, `anki-add-notes`, `anki-monolingual-hints`, `anki-backup-deck`

## Field Mapping & Pipeline

| Step | Skill | Target Field | Prompt / Notes |
|---|---|---|---|
| 1. Backup | `anki-backup-deck` | — | Run before large batch updates. |
| 2. Frequency | `anki-add-frequency` | `Frequency` | Conversational frequency (`1`–`1000`). |
| 3. Explanations | `anki-add-notes` | `Notes` | `prompts/explain_es_prompt.txt` (concise usage/grammar note). |
| 4. Translation | `anki-add-notes` | `ExpressionSpanish` | `prompts/translate_es_prompt.txt` (strips cloze markers). |
| 5. Hints | `anki-monolingual-hints` | `Expression` | Converts cloze hints to concise French cues with Spanish in parentheses. |

## Safety Rules

- Only populate empty target fields; never overwrite existing study material.
- Sort candidates by `Frequency` before applying `--limit`.
