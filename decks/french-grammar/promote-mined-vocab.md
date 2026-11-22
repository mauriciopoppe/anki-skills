# Promoting Mined French Vocabulary to Grammar

Workflow for turning unlearned mined words/phrases captured in `Language French::Mining` into full-sentence production cards in `Language French::Grammar`.

Read [`decks/french-grammar/README.md`](./README.md), [`note-types-templates/french-grammar/README.md`](../../note-types-templates/french-grammar/README.md), and [`docs/french/french-grammar-program.md`](../../docs/french/french-grammar-program.md) alongside this workflow.

## Prerequisites

- Anki Desktop is running locally with AnkiConnect at `http://localhost:8765`.
  - If AnkiConnect is unreachable (e.g., during a scheduled run while Anki is closed), exit cleanly without error.
- Check `config/anki-profile.local.md` (if present) for the current French study phase (`current_phase`) and deck names, then verify via AnkiConnect.

## Workflow

### 1. Select Top Unlearned Candidates

Query AnkiConnect for unpromoted, unlearned notes in `Language French::Mining`:

- Find new, unsuspended, unpromoted cards:
  ```text
  deck:"Language French::Mining" is:new -is:suspended -tag:promoted::grammar
  ```
- Exclude any note that already has a reviewed card (`prop:ivl>0`) or whose cloze target already appears as a `Target` or `Answer` in `Language French::Grammar`.
- Extract the target word/phrase from `Expression` (stripping `{{c1::target::hint}}` cloze markers) and sort remaining candidates numerically by `Frequency` ascending (treat empty/non-numeric or `9999999` as `9999999`, breaking ties by newest or cleanest sentence). Take the top `N` (default: `5`).

### 2. Generate French Grammar Production Cards

For each selected item, build a `French Grammar Production` note following [`decks/french-grammar/README.md`](./README.md):

- **Sentence:** Reuse the mined `Expression` (with cloze/HTML stripped) if it is natural, concise, and clean; otherwise craft a natural i+1 French sentence practicing a pattern from `current_phase` in `docs/french/french-grammar-program.md`.
- **SentenceCloze:** Same as `Sentence` with exactly one `{{c1::Answer}}` cloze around `Answer`.
- **SentenceSpanish:** Exact, natural Spanish translation matching `Sentence`.
- **Cue:** Short Spanish/French transformation hint without spoiling `Answer` (e.g., `tenir (je) → futur simple` or `convaincu → adjetivo`).
- **Explanation:** Concise 1-line Spanish grammar/usage rule.
- **ExplanationDetail:** Optional shorter breakdown of formation or cross-pattern link.
- **Notes:** 1–2 line Spanish-vs-French trap, irregular stem family, or memory hook in HTML (`<b>`, `<i>`, `<br>`). Never use Markdown (`**`) or labels like `Hook:`.
- **Metadata:**
  - `Lesson`: `Mined Vocabulary` (or matching unit title from `docs/french/french-grammar-program.md` if it directly drills a unit)
  - `Sequence`: `max(existing Sequence) + 1`, incremented per note
  - `Source`: `fr-mined-<nnn>` (continuing from existing `fr-mined-*` notes)
  - `NativeTTS`: `"1"`
  - `SentenceAudio`: `""`
  - `Tags`: `grammar::a2` or `grammar::b1` (matching level), `source::mined`

### 3. Add, Tag, Suspend, and Sync

1. Add the new notes to `Language French::Grammar` via AnkiConnect `addNotes` (`allowDuplicate: false`).
2. Only for notes that succeeded:
   - Tag the source Mining notes with `promoted::grammar` (`addTags`).
   - Suspend all cards belonging to those source Mining notes (`suspend`) so they are not reviewed in both decks.
3. Trigger AnkiConnect `sync` so the updated collection syncs to AnkiWeb / mobile.
4. Report the promoted words/phrases, new `Sequence` numbers, and any skipped candidates.
