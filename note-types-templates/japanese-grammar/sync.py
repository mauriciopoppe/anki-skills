#!/usr/bin/env python3
"""Synchronize the Japanese Grammar Production note type and its POC."""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "Language Japanese::Grammar"
MODEL_NAME = "Japanese Grammar Production"
TEMPLATE_NAME = "Grammar Production"
POC_TAG = "grammar-poc-v1"

FIELDS = [
    "SentenceFurigana",
    "Lesson",
    "Sequence",
    "GrammarPoint",
    "Pattern",
    "SentenceEnglish",
    "Sentence",
    "Cue",
    "Target",
    "TargetReading",
    "Answer",
    "AnswerReading",
    "TargetClass",
    "Explanation",
    "Notes",
    "SentenceAudio",
    "TargetFrequency",
    "Source",
]

TAGS = [
    "grammar::n5",
    "lesson::verb-classes-and-polite-nonpast",
    "category::verb-conjugation",
    "form::polite-nonpast",
    POC_TAG,
]

POC_NOTES = [
    {
        "Lesson": "Verb Classes and Polite Nonpast",
        "Sequence": "1",
        "GrammarPoint": "Polite nonpast: ichidan",
        "Pattern": "Remove る + ます",
        "SentenceEnglish": "I watch television every day.",
        "Sentence": "毎日、テレビを見ます。",
        "SentenceFurigana": (
            " 毎日[まいにち]、テレビを"
            "{{c1:: 見[み]ます}}。"
        ),
        "Cue": "見る → polite nonpast",
        "Target": "見る",
        "TargetReading": "みる",
        "Answer": "見ます",
        "AnswerReading": "みます",
        "TargetClass": "Ichidan",
        "Explanation": "Ichidan: remove る and add ます.",
        "Notes": "",
        "SentenceAudio": "[sound:japanese-grammar-poc-001.mp3]",
        "TargetFrequency": "40",
        "Source": "poc-verb-classes-001",
    },
    {
        "Lesson": "Verb Classes and Polite Nonpast",
        "Sequence": "2",
        "GrammarPoint": "Polite nonpast: godan",
        "Pattern": "Final kana to い-row + ます",
        "SentenceEnglish": "I read a Japanese book every day.",
        "Sentence": "毎日、日本語の本を読みます。",
        "SentenceFurigana": (
            " 毎日[まいにち]、 日本語[にほんご]の 本[ほん]を"
            "{{c1:: 読[よ]みます}}。"
        ),
        "Cue": "読む → polite nonpast",
        "Target": "読む",
        "TargetReading": "よむ",
        "Answer": "読みます",
        "AnswerReading": "よみます",
        "TargetClass": "Godan",
        "Explanation": "Godan: change む to み and add ます.",
        "Notes": "",
        "SentenceAudio": "[sound:japanese-grammar-poc-002.mp3]",
        "TargetFrequency": "250",
        "Source": "poc-verb-classes-002",
    },
    {
        "Lesson": "Verb Classes and Polite Nonpast",
        "Sequence": "3",
        "GrammarPoint": "Polite nonpast: irregular",
        "Pattern": "Noun + する → Noun + します",
        "SentenceEnglish": "I study Japanese every day.",
        "Sentence": "毎日、日本語を勉強します。",
        "SentenceFurigana": (
            " 毎日[まいにち]、 日本語[にほんご]を"
            "{{c1:: 勉強[べんきょう]します}}。"
        ),
        "Cue": "勉強する → polite nonpast",
        "Target": "勉強する",
        "TargetReading": "べんきょうする",
        "Answer": "勉強します",
        "AnswerReading": "べんきょうします",
        "TargetClass": "Irregular",
        "Explanation": "する-verb: change する to します.",
        "Notes": "勉強する is a noun plus する compound verb.",
        "SentenceAudio": "[sound:japanese-grammar-poc-003.mp3]",
        "TargetFrequency": "12",
        "Source": "poc-verb-classes-003",
    },
]


def invoke(action, **params):
    payload = json.dumps(
        {"action": action, "version": 6, "params": params},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        ANKI_CONNECT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
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

    existing_fields = invoke("modelFieldNames", modelName=MODEL_NAME)
    if existing_fields[0] != "SentenceFurigana":
        if dry_run:
            print("Would make SentenceFurigana the first field")
        else:
            invoke(
                "modelFieldReposition",
                modelName=MODEL_NAME,
                fieldName="SentenceFurigana",
                index=0,
            )
            print("Made SentenceFurigana the first field")

    if dry_run:
        print(f"Would update {TEMPLATE_NAME} template and styling")
        return
    invoke(
        "updateModelTemplates",
        model={
            "name": MODEL_NAME,
            "templates": {TEMPLATE_NAME: {"Front": front, "Back": back}},
        },
    )
    invoke("updateModelStyling", model={"name": MODEL_NAME, "css": css})
    print(f"Updated note type: {MODEL_NAME}")


def install_media(directory, dry_run=False):
    media_directory = os.path.join(directory, "media")
    filenames = sorted(
        filename
        for filename in os.listdir(media_directory)
        if filename.endswith(".mp3")
    )
    if dry_run:
        print("Would install media:", ", ".join(filenames) or "none")
        return
    for filename in filenames:
        with open(os.path.join(media_directory, filename), "rb") as file:
            data = base64.b64encode(file.read()).decode("ascii")
        invoke("storeMediaFile", filename=filename, data=data)
    print(f"Installed {len(filenames)} media files")


def validate_poc_notes():
    sources = set()
    for fields in POC_NOTES:
        missing = [field for field in FIELDS if field not in fields]
        if missing:
            raise RuntimeError(f"POC note is missing fields: {missing}")
        if fields["Source"] in sources:
            raise RuntimeError(f"Duplicate Source: {fields['Source']}")
        sources.add(fields["Source"])
        if fields["SentenceFurigana"].count("{{c1::") != 1:
            raise RuntimeError(f"Expected one c1 cloze: {fields['Source']}")
        if fields["Answer"] not in fields["Sentence"]:
            raise RuntimeError(f"Answer missing from Sentence: {fields['Source']}")


def install_poc(dry_run=False):
    validate_poc_notes()
    if dry_run:
        print(f"Would create deck: {DECK_NAME}")
        for fields in POC_NOTES:
            print(
                f"Would add sequence {fields['Sequence']}: "
                f"{fields['Target']} ({fields['TargetClass']})"
            )
        return

    invoke("createDeck", deck=DECK_NAME)
    added_note_ids = []
    for fields in POC_NOTES:
        existing = invoke(
            "findNotes",
            query=f'note:"{MODEL_NAME}" Source:{fields["Source"]}',
        )
        if existing:
            invoke(
                "updateNoteFields",
                note={"id": existing[0], "fields": fields},
            )
            invoke("addTags", notes=[existing[0]], tags=" ".join(TAGS))
            print(f"Updated managed POC note: {fields['Source']}")
            continue
        note_id = invoke(
            "addNote",
            note={
                "deckName": DECK_NAME,
                "modelName": MODEL_NAME,
                "fields": fields,
                "options": {"allowDuplicate": False},
                "tags": TAGS,
            },
        )
        added_note_ids.append(note_id)
        print(f"Added POC note: {fields['Source']}")

    if added_note_ids:
        print(f"Added {len(added_note_ids)} cards in Sequence order")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install-poc",
        action="store_true",
        help="Create the deck and install the three proof-of-concept notes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Describe changes without modifying Anki.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    directory, front, back, css = read_templates()
    ensure_model(front, back, css, dry_run=args.dry_run)
    if args.install_poc:
        install_media(directory, dry_run=args.dry_run)
        install_poc(dry_run=args.dry_run)
    elif args.dry_run:
        print("POC notes not requested; pass --install-poc to include them")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
