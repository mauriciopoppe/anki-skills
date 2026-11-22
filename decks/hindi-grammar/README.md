# Hindi Grammar Deck

Content rules and card-creation playbook for a lightweight Hindi grammar production deck (`Language Hindi::Grammar`).

- **Note Type:** [`Hindi Grammar Production`](../../note-types-templates/hindi-grammar/README.md)
- **Curriculum:** [`docs/hindi/hindi-grammar-program.md`](../../docs/hindi/hindi-grammar-program.md)
- **Companion Deck:** [`decks/hindi-cloze/README.md`](../hindi-cloze/README.md) (`Language Hindi::Mining`)

## Content Conventions

- **Pacing:** Recommended `3–5` new cards/day on its own FSRS preset (or shared with `Hindi` preset at `0.90` retention) so it stays light alongside Japanese and French.
- **Romanization + Devanagari:** Put clean romanized Hindi in `SentenceCloze` (with `{{c1::Answer}}`) for frictionless production, and put exact Devanagari in `Sentence` (rendered on the back and spoken by `NativeTTS` `hi_IN`) plus `AnswerDevanagari`.
- **Cue (No Spoilers):** Keep `Cue` short (`target → goal`, e.g., `pīnā (main, m.) → habitual`). Never leak `Answer` inside `Cue`.
- **Notes (Cross-Language Bridges):** Highlight **Japanese SOV / particle** parallels and **Spanish** cognates/traps in HTML (`<b>`, `<i>`, `<br>`). Never use Markdown (`**`).
- **Audio:** Set `NativeTTS` to `"1"` (`hi_IN` TTS on Devanagari `Sentence`).
- **Tags:** Include level + unit tags (e.g., `grammar::a1`, `unit::1-1-copula`).
