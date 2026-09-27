# Local collection context

An optional `anki-profile.local.md` can help future agents understand a user's
deck roles, relationships, and study preferences without committing personal
collection details. The file is ignored by Git.

Keep only durable context that is difficult to infer, such as the relationship
between a grammar deck and a mining deck, or which field represents the
learning target. Do not store note/card counts, due counts, model inventories,
field inventories, or timestamps. AnkiConnect remains authoritative for all
live collection facts.

The local Markdown file may include prose plus a structured JSON block:

```json
{
  "version": 1,
  "decks": {
    "vocabulary": {
      "name": "<deck name>",
      "language": "<language>",
      "role": "vocabulary_mining",
      "learned_vocab_source_field": "<field name>"
    },
    "grammar": {
      "name": "<grammar deck name>",
      "language": "<language>",
      "role": "grammar",
      "study_context": {
        "daily_new": null,
        "desired_retention": null,
        "current_lesson": null
      }
    }
  },
  "relationships": {
    "grammar_supports": "vocabulary"
  }
}
```

Agents should read the local file for intent and relationships, then inspect
the live collection through AnkiConnect before acting.
