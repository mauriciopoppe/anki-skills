# Promoting Mined Vocabulary to Grammar

Workflow for turning unlearned Yomitan words captured in `Language Japanese::Mining` into full-sentence production cards in `Language Japanese::Grammar`.

Read [`decks/japanese-grammar/README.md`](./README.md) and [`note-types-templates/japanese-grammar/README.md`](../../note-types-templates/japanese-grammar/README.md) alongside this workflow.

## Prerequisites

- Anki Desktop is running locally with AnkiConnect at `http://localhost:8765`.
  - If AnkiConnect is unreachable (e.g., during a scheduled run while Anki is closed), exit cleanly without error.
- Check `config/anki-profile.local.md` (if present) for the current grammar level (e.g., `current_lesson`) and deck names, then verify via AnkiConnect.

## Workflow

### 1. Build the Learned Vocabulary Pool (All Japanese Decks)

Extract learned vocabulary (`prop:ivl>=1`, which includes suspended reviewed cards such as retired Comprehension cards) across **all Japanese decks** using [`extract_learned_vocab.py`](../../skills/anki-add-sentence/scripts/extract_learned_vocab.py):

```bash
python3 skills/anki-add-sentence/scripts/extract_learned_vocab.py \
  --deck "Language Japanese::Kaishi 1.5k" --source-field "Word" \
  --deck "Language Japanese::Mining" --source-field "Expression" \
  --deck "Language Japanese::Grammar" --source-field "Target"
```

Keep this combined list for both candidate deduplication below and i+1 sentence generation in Step 3.

### 2. Select Top Unlearned Candidates

Query AnkiConnect for unpromoted, unlearned notes in `Language Japanese::Mining`:

- Find new, unsuspended, unpromoted cards:
  ```text
  deck:"Language Japanese::Mining" is:new -is:suspended -tag:promoted::grammar
  ```
- Exclude any note that:
  - already has a reviewed card (`prop:ivl>0`, including suspended cards),
  - has an `Expression` in the combined learned vocabulary list from Step 1 (across `Kaishi 1.5k`, `Mining`, and `Grammar`), or
  - already appears as a `Target` in `Language Japanese::Grammar` (including unreviewed notes).
- Sort remaining candidates numerically by `Frequency` ascending (treat empty/non-numeric as `999999`) and take the top `N` (default: `5`).

### 3. Generate Grammar Production Cards

For each selected word, build a `Japanese Grammar Production` note following [`decks/japanese-grammar/README.md`](./README.md):

- **Sentence:** Reuse the Yomitan `Sentence` if it is natural and at the learner's current grammar level; otherwise craft a clean i+1 sentence using the combined learned vocabulary pool from Step 1 and grammar from the current lesson (`current_lesson` and earlier).
- **SentenceEnglish:** Exact, natural English translation matching `Sentence`.
- **Cue:** Short prompt without spoiling the Japanese answer (e.g., `company employee → occupation`).
- **SentenceFurigana:** Generate via `anki-add-furigana` (or verify contextual readings and leading spaces before kanji chunks) with one `{{c1::...}}` cloze around `Answer`.
- **Explanation:** Concise 1-line grammar/word usage note.
- **Notes:** 1–2 line **Quick Memory Hook** (no `Kanji:`/`Hook:` prefixes) following [`prompts/grammar_kanji_hook_ja_prompt.txt`](../../prompts/grammar_kanji_hook_ja_prompt.txt).
- **Metadata:**
  - `Lesson`: `Mined Vocabulary`
  - `Sequence`: `max(existing Sequence) + 1`, incremented per note
  - `Source`: `mined-promote-<nn>` (continuing from existing `mined-promote-*` notes)
  - `NativeTTS`: `"1"`
  - `SentenceAudio`: `""`
  - `Tags`: `grammar::n5`, `source::mined-vocab`

### 4. Add, Tag, Suspend, and Sync

1. Add the new notes to `Language Japanese::Grammar` via AnkiConnect `addNotes` (`allowDuplicate: false`).
2. Only for words that succeeded:
   - Tag the source Mining notes with `promoted::grammar` (`addTags`).
   - Suspend all cards belonging to those source Mining notes (`suspend`) so they are not reviewed in both decks.
3. Trigger AnkiConnect `sync` so the updated collection syncs to AnkiWeb / mobile.
4. Report the promoted words, new `Sequence` numbers, and any skipped candidates.
