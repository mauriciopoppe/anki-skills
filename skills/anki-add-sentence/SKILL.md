---
name: anki-add-sentence
description: Procedural workflow to generate i+1 example sentences for Anki notes. Use when an AI agent needs to enrich Anki decks with example sentences that only use vocabulary the user has already learned (plus the new target word). Supports Japanese by default.
---

# Anki Add Sentence

## Overview

This skill provides a procedural workflow for generating **i+1 example sentences** for Anki learning targets. **It specifically targets notes where the target field is currently empty**, ensuring no data is overwritten. It ensures that generated sentences only use words already learned by the user, plus the single new target word. It handles Anki furigana formatting and updates both the sentence and its English translation.

## Parameters

When this skill is triggered, respect the following parameters:

- `--deck`: (Required) The Anki Deck Name to process.
- `--source-field`: (Optional) The field containing the target word. Defaults to `Expression`.
- `--target-field`: (Optional) The field where the generated sentence will be stored. Defaults to `Sentence`.
- `--target-field-english`: (Optional) The field where the English translation will be stored. Defaults to `SentenceEnglish`.
- `--limit`: (Optional) Maximum number of notes to process in one run. Defaults to `20`.
- `--batch-size`: (Optional) The number of words to include in a single generation request. Defaults to `5`.
- `--dry-run`: (Optional) Show a list of words that would be processed without generating sentences or updating Anki.

## Workflow

To generate sentences for an Anki deck, follow these steps:

### 1. Identify Learned Vocabulary
Before generating any sentences, you must know what the user has already learned.
1. Run `scripts/extract_learned_vocab.py --deck "<deck-name>" --source-field "<field-name>"` for the target deck. Repeat both options for any additional learned-vocabulary decks.
2. Capture the `stdout` output as the list of learned words.

The deck name and source field come from the current AnkiConnect inspection;
there is no repository-specific deck configuration to keep in sync.

### 2. Fetch and Filter Notes (Strictly Empty Target)
Query AnkiConnect for notes in the specified `--deck` where the `--target-field` is **unset (empty)**.

**AnkiConnect Query Example:**
```bash
curl -s -X POST http://localhost:8765 -d '{
  "action": "findNotes",
  "version": 6,
  "params": {
    "query": "deck:\"'"$DECK"'\" \"'"$TARGET_FIELD"':\""
  }
}'
```

1. Fetch note details using `notesInfo`.
2. **Sort by Frequency**: Sort the resulting notes by the `Frequency` field (ascending) to prioritize common/important vocabulary.
3. **Limit**: Take only the first `--limit` from the sorted list.

### 3. Generate Sentences
Group the target words (from the `--source-field`) into batches of `--batch-size`.

**Generation Instruction (Japanese Example):**
> "You are an expert Japanese linguist. Generate one 'i+1' example sentence for each of the following target words.
>
> **LEARNED VOCABULARY:**
> [Insert content of extract_learned_vocab.py stdout here]
>
> **TARGET WORDS:**
> [List of target words from batch]
>
> **CONSTRAINTS:**
> 1. Use ONLY words from the learned list plus the target word.
> 2. Use a natural and conversational tone.
> 3. Make the English translation faithful to the sentence. Do not add facts, motives, time, or conditions that are not expressed in Japanese.
> 4. Keep the clean Japanese sentence free of furigana, HTML, and cloze markup; add furigana in a separate field only when the caller requests it.
> 5. For Japanese output, annotate complete lexical compounds with Anki furigana syntax (`漢字[ふりがな]`), using contextual readings such as `日本語[にほんご]` and `何時[なんじ]`; never split a compound into unrelated character readings.
> 6. Before returning each item, verify that the target occurs exactly once and that the English survives a Japanese-to-English back-translation.
> 7. Provide output as a JSON object: `{\"word\": {\"sentence\": \"...\", \"english\": \"...\"}}`."

### 4. Apply Updates
Map the generated sentences and translations back to the original Note IDs. Update Anki using the `multi` action to bundle multiple `updateNoteFields` and `addTags` requests into a single network call.

- **Field Mapping:**
  - `[--target-field]`: The generated sentence with proper formatting and bolding.
  - `[--target-field-english]`: The English translation of the sentence.

## Guidelines

- **Smart Fill Rule**: **NEVER** process notes that already have content in the `--target-field`. This is the primary filtering mechanism.
- **Priority**: Always sort by `Frequency` before limiting by `--limit`.
- **Batching**: Always respect the `--batch-size` to maintain quality and avoid context limits.
- **Language Formatting**: 
  - **Japanese**: Strictly follow the ` 漢字[ふりがな]` format with the preceding space.
  - **Other Languages**: Adjust formatting requirements (e.g. accents, gender agreement) in your internal instructions.
- **i+1 Principle**: The core value of this skill is the restricted vocabulary. Ensure this constraint is strictly followed.
