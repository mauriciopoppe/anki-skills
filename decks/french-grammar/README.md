# French Grammar Deck

Content rules, card-creation playbook, and mined-sentence promotion workflow for a French grammar production deck (`Language French::Grammar`).

- **Note Type:** [`French Grammar Production`](../../note-types-templates/french-grammar/README.md)
- **Curriculum:** [`docs/french/french-grammar-program.md`](../../docs/french/french-grammar-program.md)
- **Companion Deck (Mining):** [`decks/french-cloze/README.md`](../french-cloze/README.md) (`Language French::Mining`)
- **Companion Skills:** `anki-add-notes`, `anki-backup-deck`

## Content Conventions

- **Lesson & Ordering:** Set `Lesson` to the unit title (e.g., `1.1 Partitive & Negation`, `2.1 Futur Simple`) and `Sequence` to `max(existing Sequence) + 1` so Anki introduces lessons progressively.
- **Source:** Use a unique stable ID per note (e.g., `fr-p1-001`, `fr-p2-001`, or `fr-mined-001` for promoted mining cards).
- **Cue (No Spoilers):** Keep `Cue` short (`target → goal`, e.g., `tenir (je) → futur simple` or `négation → pas de`). Never include the inflected answer inside `Cue`.
- **Explanation & ExplanationDetail:** Write a 1-line Spanish grammar rule in `Explanation` and an optional formation breakdown in `ExplanationDetail`.
- **Notes (Spanish Trap / Memory Hook):** Highlight Spanish-vs-French traps, irregular stem families, or usage nuances in HTML (`<b>`, `<i>`, `<br>`). Never use Markdown (`**`).
- **Audio:** Set `NativeTTS` to `"1"` (uses Anki's `fr_FR` TTS on `Sentence`) and leave `SentenceAudio` empty unless custom audio is requested.
- **Tags:** Include phase + unit tags (e.g., `grammar::a2`, `grammar::b1`, `unit::2-1-futur-simple`, `source::mined`).

## Promoting Mined French Sentences into Grammar

Keep **mining** (`Language French::Mining`) separate from **grammar production** (`Language French::Grammar`), just like the Japanese workflow:

1. **Mine freely** into `Language French::Mining` when you encounter useful words, idioms, or natural sentences.
2. **Spot recurring grammar gaps or high-lapse cards** (e.g., `Je vous tiendrai au courant…` → `futur simple` irregular `-dr-` stem; `On aurait pu…` → `conditionnel passé`).
3. **Promote the pattern, not just the sentence:**
   - Map the sentence to its unit in [`docs/french/french-grammar-program.md`](../../docs/french/french-grammar-program.md).
   - Add 1–3 focused `French Grammar Production` cards covering the rule (reusing the mined sentence if it's clean and i+1, plus 1–2 companion examples from the same stem/pattern family).
   - Keep `Sequence` aligned with your current study frontier so new grammar cards appear right when you need them.

## Card-Creation Checklist

1. Inspect `Language French::Grammar` via AnkiConnect for the current max `Sequence` and existing `Source` IDs.
2. Ensure `Answer` is an exact substring of `Sentence` and `SentenceCloze` has exactly one `{{c1::Answer}}` cloze.
3. Verify `Cue` prompts the exact grammar choice without leaking `Answer`.
4. Set `NativeTTS` to `"1"` and confirm `Notes` uses HTML (`<b>`, `<i>`), never Markdown.
5. Run `python3 note-types-templates/french-grammar/sync.py --install-starter --dry-run` (or `--dry-run`) before writing.
