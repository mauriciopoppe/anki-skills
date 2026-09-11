---
name: anki-practice-session
description: Generate an interactive vocabulary practice session prompt for Gemini. It queries AnkiConnect to retrieve words already learned and words that come next, and formats a structured system prompt to practice vocabulary interactively.
---

# Anki Practice Session

## Overview

This skill generates a personalized interactive language tutor prompt based on your actual learning progress in Anki. By feeding this prompt into Gemini, you can practice vocabulary with dynamic exercises that strictly respect what you have already learned and what is next in your queue.

## Parameters

When this skill is triggered, respect the following parameters:

- `--deck`: (Required) The Anki Deck Name to process (e.g. `"Language French::My french words and phrases"`, `"Language Japanese::Kaishi 1.5k"`, `"Language Japanese::Mining"`, or `"Language Hindi::My hindi words and phrases"`).
- `--limit-learned`: (Optional) Maximum number of learned words to include in the database. Defaults to `1000`.
- `--limit-next`: (Optional) Maximum number of upcoming words/phrases to introduce and practice. Defaults to `10`.
- `--output`: (Optional) Path to write the generated markdown prompt to. Defaults to `practice_prompt.md`.
- `--dry-run`: (Optional) Print the list of learned and next words without generating the prompt file.

## Workflow

To generate a practice session:

1. Run the `scripts/generate_practice.py` script.
2. Provide the required `--deck` parameter and any optional settings.
3. The script will query Anki via AnkiConnect, partition notes into learned and upcoming, parse cloze structures, and output a markdown prompt to the specified path.
4. Copy the contents of the generated prompt file and paste them into Gemini to begin your interactive practice session!
