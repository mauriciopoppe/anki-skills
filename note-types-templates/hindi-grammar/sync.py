#!/usr/bin/env python3
"""Synchronize the Hindi Grammar Production note type and grammar packs."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "Language Hindi::Grammar"
MODEL_NAME = "Hindi Grammar Production"
TEMPLATE_NAME = "Grammar Production"

FIELDS = [
    "SentenceCloze",
    "Lesson",
    "Sequence",
    "GrammarPoint",
    "Pattern",
    "SentenceEnglish",
    "Sentence",
    "Cue",
    "Target",
    "Answer",
    "AnswerDevanagari",
    "TargetClass",
    "Explanation",
    "ExplanationDetail",
    "Notes",
    "SentenceAudio",
    "NativeTTS",
    "TargetFrequency",
    "Source",
]


def invoke(action, **params):
    payload = json.dumps(
        {"action": action, "version": 6, "params": params}
    ).encode("utf-8")
    request = urllib.request.Request(ANKI_CONNECT_URL, data=payload)
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not connect to AnkiConnect at {ANKI_CONNECT_URL}: {error}"
        ) from error
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result.get("result")


def read_templates():
    directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(directory, "front.html"), encoding="utf-8") as file:
        front = file.read()
    with open(os.path.join(directory, "back.html"), encoding="utf-8") as file:
        back = file.read()
    with open(os.path.join(directory, "styling.css"), encoding="utf-8") as file:
        css = file.read()
    return directory, front, back, css


def normalize_fields(raw_note):
    return {field: str(raw_note.get(field, "")) for field in FIELDS}


def validate_notes(raw_notes):
    sources = set()
    sequences = []
    for raw in raw_notes:
        fields = normalize_fields(raw)
        source = fields["Source"]
        if not source:
            raise RuntimeError("Note is missing Source")
        if source in sources:
            raise RuntimeError(f"Duplicate Source: {source}")
        sources.add(source)

        sequences.append(int(fields["Sequence"]))

        cloze = fields["SentenceCloze"]
        matches = re.findall(r"\{\{c1::([^:}]+)\}\}", cloze)
        if len(matches) != 1:
            raise RuntimeError(
                f"{source}: SentenceCloze must contain exactly one {{c1::...}} cloze"
            )
        if matches[0] != fields["Answer"]:
            raise RuntimeError(
                f"{source}: cloze '{matches[0]}' != Answer '{fields['Answer']}'"
            )
        if not fields["Sentence"]:
            raise RuntimeError(f"{source}: Devanagari Sentence is required for TTS")
        if "**" in fields["Notes"]:
            raise RuntimeError(f"{source}: Markdown bold found in Notes")

    if sequences != sorted(sequences):
        raise RuntimeError("Notes are not sorted by Sequence")


def ensure_model(front, back, css, dry_run=False):
    model_names = invoke("modelNames")
    if MODEL_NAME not in model_names:
        if dry_run:
            print(f"Would create note type: {MODEL_NAME}")
            return
        invoke(
            "createModel",
            modelName=MODEL_NAME,
            inOrderFields=FIELDS,
            css=css,
            isCloze=True,
            cardTemplates=[
                {"Name": TEMPLATE_NAME, "Front": front, "Back": back}
            ],
        )
        print(f"Created note type: {MODEL_NAME}")
        return

    existing_fields = invoke("modelFieldNames", modelName=MODEL_NAME)
    missing_fields = [field for field in FIELDS if field not in existing_fields]
    if missing_fields:
        if dry_run:
            print("Would add fields:", ", ".join(missing_fields))
        else:
            for field in missing_fields:
                invoke("modelFieldAdd", modelName=MODEL_NAME, fieldName=field)
            print("Added fields:", ", ".join(missing_fields))

    if dry_run:
        print(f"Would update template '{TEMPLATE_NAME}' and styling on '{MODEL_NAME}'")
        return

    invoke(
        "updateModelTemplates",
        model={
            "name": MODEL_NAME,
            "templates": {TEMPLATE_NAME: {"Front": front, "Back": back}},
        },
    )
    invoke("updateModelStyling", model={"name": MODEL_NAME, "css": css})
    print(f"Updated template '{TEMPLATE_NAME}' and styling on '{MODEL_NAME}'")


def install_pack(directory, filename, label, dry_run=False):
    path = os.path.join(directory, filename)
    with open(path, encoding="utf-8") as file:
        raw_notes = json.load(file)

    validate_notes(raw_notes)

    if dry_run:
        print(f"Would create deck: {DECK_NAME}")
        print(
            f"Would install/update {len(raw_notes)} {label} grammar notes "
            "in Sequence order"
        )
        for raw in raw_notes[:5]:
            print(f"  [{raw['Sequence']}] {raw['Lesson']} | {raw['Answer']}")
        if len(raw_notes) > 5:
            print(f"  ... ({len(raw_notes) - 5} more)")
        return

    invoke("createDeck", deck=DECK_NAME)
    added = 0
    updated = 0
    for raw in raw_notes:
        fields = normalize_fields(raw)
        tags = list(raw.get("Tags", []))
        existing = invoke(
            "findNotes",
            query=f'note:"{MODEL_NAME}" Source:{fields["Source"]}',
        )
        if existing:
            invoke("updateNoteFields", note={"id": existing[0], "fields": fields})
            if tags:
                invoke("addTags", notes=[existing[0]], tags=" ".join(tags))
            updated += 1
            continue

        invoke(
            "addNote",
            note={
                "deckName": DECK_NAME,
                "modelName": MODEL_NAME,
                "fields": fields,
                "options": {"allowDuplicate": False},
                "tags": tags,
            },
        )
        added += 1

    print(
        f"Synced {label} pack to '{DECK_NAME}': added={added}, updated={updated}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install-starter",
        action="store_true",
        help="Install Phase 1 A1 Hindi grammar starter pack (Seq 1–28).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and describe changes without modifying Anki.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    directory, front, back, css = read_templates()
    ensure_model(front, back, css, dry_run=args.dry_run)
    if args.install_starter:
        install_pack(directory, "starter_notes.json", "starter", dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
