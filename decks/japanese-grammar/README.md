# Japanese Grammar Deck

Content rules and card-creation playbook for a Japanese grammar production deck (e.g., `Language Japanese::Grammar`).

- **Note Type:** [`Japanese Grammar Production`](../../note-types-templates/japanese-grammar/README.md)
- **Companion Prompts:**
  - Sentence generation: [`prompts/grammar_sentence_ja_prompt.txt`](../../prompts/grammar_sentence_ja_prompt.txt)
  - Quick Memory Hooks: [`prompts/grammar_kanji_hook_ja_prompt.txt`](../../prompts/grammar_kanji_hook_ja_prompt.txt)
- **Companion Skills:** `anki-add-furigana`, `anki-add-notes`, `anki-backup-deck`
- **Workflows:**
  - Promoting Yomitan mined words into this deck: [`promote-mined-vocab.md`](./promote-mined-vocab.md)

## Content Conventions

- **Lesson & Ordering:** Set `Lesson` to the topic/textbook lesson (e.g., `Minna no Nihongo 5`, `Seasons`, `Prohibition`) and `Sequence` to `max(existing Sequence) + 1`.
- **Source:** Use a unique stable ID per note (e.g., `minna-no-nihongo-l5-01`, `n5-seasons-01`).
- **Cue (No Spoilers):** Keep `Cue` short (`X → goal`). When testing vocabulary/kanji recall, never put the Japanese answer in `Cue` (use `spring → in spring`, not `春 → in spring`).
- **Explanation & ExplanationDetail:** Write a brief 1-line grammar rule in `Explanation` (the *what*) and an optional 1–2 line plain-language decision rule or contrast in `ExplanationDetail` (the *why*, e.g. `を` vs `が` or `に` vs `で`—anchored to Spanish/English intuition per [`docs/grammar-concepts.md`](../../docs/grammar-concepts.md)).
- **Notes (Quick Memory Hook):** Add a 1–2 line kanji/reading memory hook (no `Kanji:`/`Hook:` prefixes) for hard kanji or irregular readings following `prompts/grammar_kanji_hook_ja_prompt.txt`.
- **Audio:** Set `NativeTTS` to `"1"` and leave `SentenceAudio` empty unless custom audio is requested.
- **Tags:** Include level + lesson/source tags (e.g., `grammar::n5`, `minna-no-nihongo-l5`, `category::calendar`, `source::youtube-<id>`).

## Card-Creation Checklist

1. **Inspect live deck:** Query AnkiConnect for the current max `Sequence` and check for duplicate notes.
2. **Draft sentences:** Follow `prompts/grammar_sentence_ja_prompt.txt`—natural learner-level Japanese, exact English translation, `Answer` as an exact substring of `Sentence`.
3. **Check `Cue`:** Confirm it prompts the target form without spoiling the answer.
4. **Generate `SentenceFurigana`:** Prefer `anki-add-furigana` (`--dry-run` first) or verify contextual readings (`4月[しがつ]`, `7時[しちじ]`, `一人[ひとり]`) and leading spaces before kanji chunks.
5. **Add `Notes`:** Generate Quick Memory Hooks using `prompts/grammar_kanji_hook_ja_prompt.txt` (or backfill empty `Notes` via `anki-add-notes`).
6. **Add & verify:** Insert via AnkiConnect `addNotes` (`allowDuplicate: false`), then inspect representative notes to confirm cloze, furigana, and field formatting.
