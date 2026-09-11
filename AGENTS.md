# Agent System & Project Documentation

Welcome! This file serves as the definitive reference guide for AI Agents operating on the `anki-skills` repository. It consolidates product goals, learning methodologies, code guidelines, tech stack details, and templates.

---

## 1. Product Overview & Goals

This project provides a collection of AI Workspace Skills to automate and enhance Anki deck management.

### Target Audience
The primary users are **language learners** who use Anki for vocabulary and grammar retention. They manage large decks and need efficient ways to enrich their cards with high-quality study aids without manual effort.

### Core Goals
- **Automate high-quality study materials:** Focus on generating mnemonics and explanations that aid memory and understanding.
- **Save time through automation:** Enable users to bulk-populate empty fields in their Anki cards using an AI agent, reducing manual research and entry.
- **Provide context-aware learning:** Ensure that all generated content is deeply relevant to the specific word, sentence, or context provided in the card's existing fields.

---

## 2. Learning Methodology: The "Kaishi 1.5k" Approach

Effective card creation and reinforcement in this repository are defined by the following principles (analyzed from the "Kaishi 1.5k" Japanese deck):

### A. "i+1" Sentence Design
The deck follows a strict **"i+1" (one new piece of information)** philosophy. Each card introduces a single new **target word**, but the example sentence surrounding it is composed almost entirely of words already learned in previous cards.
*   *Example:* When learning the word **私 (I)**, the sentence is `私はアンです` (I am Ann). Later, when learning **好き (like)**, the sentence `私はワインが好きです` (I like wine) reuses the `私は...です` structure and the word `私` already known.

### B. Sentence Sharing across Multiple Notes
Unlike many decks where every word has a unique sentence, this approach frequently **shares the exact same sentence** across 2 or 3 different target words.
*   *Target Word A:* あなた (You) → Sentence: `あなたはトムさんですか。`
*   *Target Word B:* さん (San) → Sentence: `あなたはトムさんですか。`
This ensures that when moving from Word A to Word B, the word is seen in a familiar "habitat," which reduces cognitive load and reinforces the grammar and vocabulary of the shared sentence.

### C. Gradual Structural Expansion
The method reuses **grammatical frameworks** to provide scaffolding.
*   Early cards establish basic patterns like `[A] は [B] です` (A is B).
*   Subsequent cards slowly swap in new subjects, objects, or verbs into those established patterns.
*   By the time complex sentences are reached, the "scaffolding" (particles, pronouns, and common verbs) is already second nature.

### D. Visual and Auditory Consistency
- **Consistency:** The same audio and images are often used for shared sentences, creating a strong mental link between the sound, the context, and the words.
- **Focus:** The target word is typically **bolded** in the `Sentence` field on the front of the card, making it clear what the new "variable" is in the familiar sentence.

---

## 3. Product Guidelines for AI Agents

When generating content or modifying deck fields, AI agents must adhere to these guidelines:

### Tone and Voice
- **Encouraging and Friendly:** AI-generated explanations should use a supportive, helpful, and conversational tone to make complex linguistic concepts accessible.

### Content Structure and Formatting
- **Visual Emphasis:** Key vocabulary words, particles, or grammatical markers within explanations must be **bolded** or *italicized* to draw the learner's eye and reinforce recognition.
- **Clarity and Brevity:** Avoid unnecessary fluff. Focus on delivering high-value insights quickly.
- **Standard Markdown:** Use standard Markdown formatting for consistent rendering across Anki clients (Desktop, Mobile, Web).

### Linguistic Quality
- **Contextual Accuracy:** Explanations must be derived directly from the context provided in the card (e.g., the specific sentence or phrase).
- **Literal vs. Figurative:** Clearly distinguish between the literal meaning of a word and its usage in idiomatic or figurative contexts.
- **Etymological Hints:** Provide brief, high-impact etymological connections if they aid in memorization (e.g., "This kanji combines 'tree' and 'sun' to mean 'East'").

### Safety and Reliability
- **Disclaimer Awareness:** Remind users that content is AI-generated and should be verified if something seems incorrect.
- **Fail-Safe Generation:** If context is insufficient for a high-quality explanation, prefer a generic but accurate definition rather than hallucinating specific details.

---

## 4. Tech Stack & Environment

### Core Technologies
- **Python 3.9+:** The primary programming language for all automation scripts.
- **Agent Skills:** Most AI behavior is expressed as procedural `SKILL.md` instructions rather than a provider-specific LLM client.
- **AnkiConnect:** The bridge for interacting with a running Anki instance via its RESTful API on `http://localhost:8765`.

### Data and File Handling
- **Python standard library:** Scripts use `urllib.request` for HTTP, plus modules such as `json`, `csv`, and `zipfile`; avoid adding dependencies when the standard library is sufficient.
- **Lexique 3:** Used as the primary linguistic database for French lemmatization.

### Development and Quality
- **Ruff:** Fast Python linter and code formatter to ensure code quality and consistency.
- **Skill validator:** `tests/validate_skills.py` checks required skill frontmatter and structure.
- **Pip:** Standard package installer for Python dependencies listed in `requirements.txt`.

---

## 5. Repository Architecture & Operational Invariants

### Repository Map

- `skills/<skill-name>/SKILL.md`: portable, provider-independent workflows for AI agents.
- `skills/<skill-name>/scripts/`: deterministic helpers used when procedural instructions alone are insufficient.
- `note-types-templates/`: version-controlled Anki card HTML and CSS, plus synchronization helpers.
- `french-dictionary/`: pipeline for a Yomitan-compatible French frequency dictionary.
- `resources/`: project documentation images.
- `anki_backups/`: restorable `.apkg` deck exports.
- `docs/`: learning programs and supporting documentation.

### Deck Mutation Safety

- Anki must be running with AnkiConnect available at `http://localhost:8765` for live deck operations.
- Only process notes whose destination field is empty. Never silently overwrite existing study material.
- Honor `--dry-run` as a read-only preview and use interactive review when requested.
- Validate required note fields before generation or mutation; stop clearly when the note type does not match.
- Prefer AnkiConnect `multi` for batched `updateNoteFields` and `addTags` operations.
- Back up a deck before broad or difficult-to-reverse changes.

### Generation Invariants

- Sort candidates by the configured frequency field before limiting when a skill prioritizes vocabulary.
- For i+1 generation, a word is learned when its card interval is greater than zero. Sentences may use learned vocabulary plus exactly one target word.
- Japanese output uses Anki furigana syntax (`漢字[ふりがな]`), contextual readings, and `<b>` target highlighting where HTML is expected.
- Prefer natural daily-life language; accuracy and restricted vocabulary take priority over novelty.
- Respect `--batch-size` and report the intended scope before large runs.

### Development Workflow

1. Read the relevant `SKILL.md`, nearby scripts, and templates before changing behavior.
2. Make the smallest coherent change and prefer non-interactive commands.
3. Run relevant checks. At minimum, after modifying skill content:

   ```bash
   python3 tests/validate_skills.py
   ruff check <changed Python paths>
   ```

4. For live Anki integrations, use a dry run first when available, then verify representative notes and field formatting.
5. Before finishing, confirm functionality, readability, absence of committed secrets, and documentation of changed interfaces.

Historical Conductor plans remain available through Git history, but completed track metadata and Gemini-specific workflow state are not active project instructions.

---

## 6. Card Templates & Synchronization

HTML and CSS templates for various note types are version-controlled in the `note-types-templates/` directory.

### Syncing Templates to Anki via AnkiConnect

To synchronize local files with Anki, use the AnkiConnect API. The following commands read local HTML/CSS files and update the model templates and styling.

#### A. Japanese::Mining (Lapis Model)
- **Path:** `note-types-templates/lapis/`
- **Anki Model:** `Lapis`
- **Template Name:** `Mining`

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/lapis/front.html)" \
  --arg b "$(cat note-types-templates/lapis/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "Lapis", templates: {Mining: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/lapis/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "Lapis", css: $s}}}')"
```

#### B. My Cloze Model
- **Path:** `note-types-templates/my-cloze/`
- **Anki Model:** `My Cloze`
- **Template Name:** `Cloze`

```bash
curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg f "$(cat note-types-templates/my-cloze/front.html)" \
  --arg b "$(cat note-types-templates/my-cloze/back.html)" \
  '{action: "updateModelTemplates", version: 6, params: {model: {name: "My Cloze", templates: {Cloze: {Front: $f, Back: $b}}}}}')" && \
  curl -s -X POST http://localhost:8765 -d "$(jq -n \
  --arg s "$(cat note-types-templates/my-cloze/styling.css)" \
  '{action: "updateModelStyling", version: 6, params: {model: {name: "My Cloze", css: $s}}}')"
```
