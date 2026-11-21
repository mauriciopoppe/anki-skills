# Anki Skills

An ecosystem of **AI Skills** for Anki that automates the creation of high-quality study materials. These tools follow the [Agent Skills](https://github.com/vercel-labs/skills) specification and enable AI agents to enrich your decks with mnemonics, i+1 example sentences, furigana, audio, conversational frequency data, and monolingual hints directly through AnkiConnect.

## Getting Started

### Prerequisites

All skills require **Anki** to be running with the **[AnkiConnect](https://ankiweb.net/shared/info/2055492159)** add-on installed.

Verify your connection:

```bash
curl -s -X POST http://localhost:8765 -d '{"action": "version", "version": 6}'
```

### Installation

Install all skills with the `npx skills` CLI (supports 50+ agents including Gemini CLI, Claude Code, Cursor, Windsurf, etc.):

```bash
npx skills add mauriciopoppe/anki-skills
```

Or load them from a local clone:

```bash
npx skills add .
```

### Local Collection Context (Optional)

If you use this repository repeatedly with one Anki collection, you can create a gitignored `config/anki-profile.local.md` to record durable deck roles, relationships, and study preferences. It is advisory context only—live AnkiConnect queries remain the source of truth for mutable facts. See [`config/README.md`](./config/README.md) for the convention and an example.

---

## Repository Structure

This repository mirrors Anki's separation between **generic note types** (schema & presentation) and **decks** (content rules & study workflows):

```text
skills/                 # Portable Agent Skills (SKILL.md + deterministic scripts)
prompts/                # Reusable {FieldName} prompt templates for anki-add-notes
note-types-templates/   # Generic Anki note-type HTML, CSS, sync scripts, and schema READMEs
decks/                  # Portable deck playbooks linking note types, prompts, skills, and checklists
config/                 # Local collection profile conventions (gitignored anki-profile.local.md)
```

- **Note Types (`note-types-templates/`):**
  - [`japanese-grammar`](./note-types-templates/japanese-grammar/README.md) (`Japanese Grammar Production`)
  - [`lapis`](./note-types-templates/lapis/README.md) (`Lapis`)
  - [`my-cloze`](./note-types-templates/my-cloze/README.md) (`My Cloze` — shared across multiple language decks)
- **Deck Playbooks (`decks/`):**
  - [`japanese-grammar`](./decks/japanese-grammar/README.md) — Japanese grammar production cards & Quick Memory Hooks
  - [`japanese-mining`](./decks/japanese-mining/README.md) — Japanese vocabulary mining (`Lapis`)
  - [`french-cloze`](./decks/french-cloze/README.md) — French cloze phrases (`My Cloze`)
  - [`hindi-cloze`](./decks/hindi-cloze/README.md) — Hindi cloze phrases (`My Cloze`)

---

## Skills

### `anki-add-notes`

Orchestrates AI augmentation of Anki notes by scanning a deck for empty fields and filling them using a `{FieldName}` prompt template read from a local file.

#### Examples

**1. Explain Sentences** — Takes a Cloze deletion like `Sur ça, tu touches un point {{c1::assez juste}}` and adds a concise explanation to `Notes`.

| Before | After |
| --- | --- |
| ![before](./resources/french-explain-before.png) | ![after](./resources/french-explain-after.png) |

> Use anki-add-notes for deck "Language French::My french words and phrases", target field "Notes", and prompt file "./prompts/explain_fr_prompt.txt".

**2. Generate Kanji Mnemonics** — Creates a concise visual + sound memory hook for the `Notes` field.

| Card |
| --- |
| ![after](./resources/kanji-mnemonic-after.png) |

> Use anki-add-notes for deck "Language Japanese::Mining", target field "Notes", and prompt file "./prompts/kanji_mnemonic_ja_prompt.txt".

**3. Translate Sentences** — Translates a field (like `Expression`) into your target language, automatically cleaning Anki cloze markers.

> Use anki-add-notes for deck "Language Hindi::My hindi words and phrases", target field "ExpressionEnglish", and prompt file "./prompts/translate_en_prompt.txt".

#### Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Required) The field you want to fill (e.g., `Notes`).
- `--prompt-file`: (Required) Path to your prompt template. Use `{FieldName}` placeholders to pull data from your cards. Bundled templates: [English explanation](./prompts/explain_en_prompt.txt), [French explanation](./prompts/explain_fr_prompt.txt), [Spanish explanation](./prompts/explain_es_prompt.txt), [Japanese kanji mnemonic](./prompts/kanji_mnemonic_ja_prompt.txt), [Japanese grammar kanji hook](./prompts/grammar_kanji_hook_ja_prompt.txt), [Translation in English](./prompts/translate_en_prompt.txt), [Translation in Spanish](./prompts/translate_es_prompt.txt), [Translation in Japanese (furigana)](./prompts/translate_ja_prompt.txt), and [Japanese grammar sentence](./prompts/grammar_sentence_ja_prompt.txt).
- `--limit`: (Optional) Limit the number of notes processed. Defaults to `20`.
- `--sort-field`: (Optional) Field used for sorting notes. Defaults to `Frequency`.
- `--interactive` / `-i`: (Optional) Review every AI response before it hits your deck.
- `--dry-run`: (Optional) List the notes that would be processed without calling the AI.

---

### `anki-monolingual-hints`

Transforms Anki cloze deletion hints from a source language into concise monolingual cues (definitions, synonyms, or grammar cues) in the target language, while preserving a translation in `--target-language` (defaults to English) in parentheses.

> Use anki-monolingual-hints for deck "Language French::My french words and phrases" with target language "Spanish".

#### Strategy Priority

1. **Zero Hint:** Only the target language hint (e.g., `{{c1::de::(de)}}`).
2. **Definition (TL):** Simple definition + target language (e.g., `{{c1::voiture::véhicule (coche)}}`).
3. **Synonym/Antonym (TL):** `=` or `≠` + target language (e.g., `{{c1::triste::≠ content (triste)}}`).
4. **Grammar Cue:** Conjugation or rule label + target language (e.g., `{{c1::suis::présent (soy)}}`).

Rules: encourage short abbreviations (`p.c.`, `f.`), never self-reference the target word or root, and keep hints as short as possible.

#### Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-language`: (Optional) Language for the parenthetical translation. Defaults to English.
- `--target-field`: (Optional) Field with the cloze deletions. Defaults to `Expression`.
- `--limit`: (Optional) Limit processing. Defaults to `5`.
- `--interactive` / `-i`: (Optional) Review every transformation.
- `--dry-run`: (Optional) Preview results only.

---

### `anki-add-sentence`

Generates **i+1 example sentences** for learning targets, ensuring sentences only use vocabulary you've already learned (via `extract_learned_vocab.py`) plus the single target word.

> Use anki-add-sentence for deck "Language Japanese::Mining". Process 5 notes.

#### Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--source-field`: (Optional) Field with the target word. Defaults to `Expression`.
- `--target-field`: (Optional) Field for the generated sentence. Defaults to `Sentence`.
- `--target-field-english`: (Optional) Field for the English translation. Defaults to `SentenceEnglish`.
- `--limit`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview words to be processed.

---

### `anki-add-frequency`

Estimates how common a word or phrase is in a conversational setting (scale `1`–`1000`, where `1` is very common and `1000` is rare) and fills an Anki field.

> Use anki-add-frequency for deck "Language Hindi::My hindi words and phrases". Process 10 notes.

#### Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--target-field`: (Optional) Field for the frequency number. Defaults to `Frequency`.
- `--limit`: (Optional) Limit processing. Defaults to `20`.
- `--batch-size`: (Optional) Notes per AI request. Defaults to `5`.
- `--dry-run`: (Optional) Preview results only.

---

### `anki-add-audio`

Generates MP3 audio locally on macOS with a system voice and FFmpeg, stores it in Anki media, and fills only empty audio fields.

> Use anki-add-audio for deck "Language Japanese::Grammar", reading from "Sentence" and writing to "SentenceAudio" with voice "Kyoko".

Run a preview from the repository root:

```bash
python3 skills/anki-add-audio/scripts/anki_add_audio.py \
  --deck "Language Japanese::Grammar" \
  --source-field Sentence \
  --target-field SentenceAudio \
  --voice Kyoko \
  --limit 3 \
  --dry-run
```

After reviewing the preview, remove `--dry-run` to generate and attach audio.

---

### `anki-add-furigana`

Generates or repairs Japanese furigana fields with contextual readings from Fugashi and UniDic while preserving native Anki Cloze markup.

> Use anki-add-furigana for deck "Language Japanese::Grammar", source field "Sentence", target field "SentenceFurigana", and answer field "Answer".

Run a preview before changing notes:

```bash
python3 skills/anki-add-furigana/scripts/generate_furigana.py \
  --deck "Language Japanese::Grammar" \
  --model "Japanese Grammar Production" \
  --limit 3 \
  --dry-run
```

Supports `--interactive` / `-i`, `--limit`, `--source-field`, `--answer-field`, `--target-field`, and `--yes` for a large non-interactive batch.

---

### `anki-backup-deck`

Backs up an Anki deck to a single `.apkg` binary file. Use this before making significant changes to your deck.

> Use anki-backup-deck to backup the "Language French::My french words and phrases" deck to "<backup-directory>".

---

### `anki-practice-session`

Generates a personalized AI tutor prompt from your Anki progress, combining learned vocabulary with the next words in your queue for interactive exercises.

> Use anki-practice-session for deck "Language Japanese::Mining". Include up to 1000 learned words and the next 10 words, and write the prompt to "practice_prompt.md".

#### Parameters

- `--deck`: (Required) The Anki Deck Name to process.
- `--limit-learned`: (Optional) Maximum learned words to include. Defaults to `1000`.
- `--limit-next`: (Optional) Maximum upcoming words to practice. Defaults to `10`.
- `--output`: (Optional) Path for the generated prompt. Defaults to `practice_prompt.md`.
- `--dry-run`: (Optional) Preview the learned and upcoming vocabulary without writing a prompt.

---

## Meta Prompts

Meta prompts combine multiple skills into a single workflow for processing large batches of new notes across multiple dimensions.

### French Deck Monolingualization

```text
In the deck "Language French::My french words and phrases":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes" and the prompt file "./prompts/explain_es_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionSpanish" and the prompt file "./prompts/translate_es_prompt.txt".
- use the skill anki-monolingual-hints.

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

### Japanese Mining Deck Augmentation

```text
In the deck "Language Japanese::Mining":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes", and prompt file "./prompts/kanji_mnemonic_ja_prompt.txt".
- use the skill anki-add-sentence.

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

### Hindi Deck Augmentation

```text
In the deck "Language Hindi::My hindi words and phrases":
- use the skill anki-add-frequency.
- use the skill anki-add-notes with the target field "Notes" and the prompt file "./prompts/explain_en_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionFurigana" and the prompt file "./prompts/translate_ja_prompt.txt".
- use the skill anki-add-notes with the target field "ExpressionEnglish" and the prompt file "./prompts/translate_en_prompt.txt".

Process a limit of 200 notes with a batch size of 50. Parallelize where possible. Prefer atomic changes.
```

---

## Safety & Testing

- **Back up your deck** using `anki-backup-deck` before running skills that modify your collection.
- **AnkiConnect** must be running and accessible at `http://localhost:8765`.
- Validate that all skills adhere to the [Agent Skills](https://github.com/vercel-labs/skills) specification:

```bash
python3 tests/validate_skills.py
```

## License

MIT
