# Japanese Mining Deck

Augmentation and content playbook for a Japanese vocabulary mining deck (e.g., `Language Japanese::Mining`).

- **Note Type:** [`Lapis`](../../note-types-templates/lapis/README.md)
- **Companion Prompts:**
  - Quick Memory Hooks: [`prompts/kanji_mnemonic_ja_prompt.txt`](../../prompts/kanji_mnemonic_ja_prompt.txt)
- **Companion Skills:** `anki-add-frequency`, `anki-add-notes`, `anki-add-sentence`, `anki-practice-session`, `anki-backup-deck`

## Field Mapping & Pipeline

| Step | Skill | Target Field(s) | Prompt / Notes |
|---|---|---|---|
| 1. Backup | `anki-backup-deck` | — | Run before large batch updates. |
| 2. Frequency | `anki-add-frequency` | `Frequency` | Conversational frequency (`1`–`1000`). |
| 3. Memory Hooks | `anki-add-notes` | `Notes` | `prompts/kanji_mnemonic_ja_prompt.txt` (`{Expression}`, `{ExpressionReading}`, `{Sentence}`). |
| 4. i+1 Sentences | `anki-add-sentence` | `Sentence`, `SentenceEnglish` | Uses learned vocab from core + mining decks (see `config/anki-profile.local.md`), bolding the target word with `<b>`. |

## Safety Rules

- Only populate empty target fields; never overwrite existing study material.
- Sort candidates by `Frequency` before applying `--limit`.
