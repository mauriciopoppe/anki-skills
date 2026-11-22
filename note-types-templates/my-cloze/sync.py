#!/usr/bin/env python3
"""Synchronize the My Cloze note type templates, styling, and NativeTTS field."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ANKI_CONNECT_URL = "http://localhost:8765"
MODEL_NAME = "My Cloze"
TEMPLATE_NAME = "Cloze"
DEFAULT_TTS_DECK = "Language French::Mining"

FIELDS = [
    "Expression",
    "ExpressionEnglish",
    "ExpressionSpanish",
    "ExpressionFurigana",
    "Frequency",
    "Glossary",
    "Notes",
    "Image",
    "NativeTTS",
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
    return front, back, css


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


def enable_native_tts(deck_name, batch_size=100, dry_run=False):
    query = f'deck:"{deck_name}" note:"{MODEL_NAME}"'
    note_ids = invoke("findNotes", query=query)
    if not note_ids:
        print(f"No {MODEL_NAME} notes found in deck: {deck_name}")
        return

    infos = invoke("notesInfo", notes=note_ids)
    to_update = [
        info["noteId"]
        for info in infos
        if not info["fields"].get("NativeTTS", {}).get("value", "").strip()
    ]
    already_enabled = len(note_ids) - len(to_update)

    if dry_run:
        print(
            f"Would enable NativeTTS on {len(to_update)} notes in '{deck_name}' "
            f"(already populated: {already_enabled})"
        )
        return

    for start in range(0, len(to_update), batch_size):
        batch = to_update[start : start + batch_size]
        actions = [
            {
                "action": "updateNoteFields",
                "params": {"note": {"id": note_id, "fields": {"NativeTTS": "1"}}},
            }
            for note_id in batch
        ]
        results = invoke("multi", actions=actions)
        for result in results:
            if isinstance(result, dict) and result.get("error"):
                raise RuntimeError(result["error"])

    print(
        f"Enabled NativeTTS in '{deck_name}': "
        f"updated={len(to_update)}, already_enabled={already_enabled}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enable-native-tts",
        action="store_true",
        help="Set NativeTTS=1 on empty notes in the target deck.",
    )
    parser.add_argument(
        "--deck",
        default=DEFAULT_TTS_DECK,
        help=f"Target deck for --enable-native-tts (default: {DEFAULT_TTS_DECK}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for AnkiConnect multi updates (default: 100).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Describe changes without modifying Anki.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    front, back, css = read_templates()
    ensure_model(front, back, css, dry_run=args.dry_run)
    if args.enable_native_tts:
        enable_native_tts(
            deck_name=args.deck,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
