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
N5_CORE_TAGS = [
    "grammar::n5",
    "category::core-n5",
    "n5-core-v1",
]

TTS_SAMPLE_TAGS = [
    "grammar::n5",
    "category::native-tts",
    "tts-sample-v1",
]

COUNTING_TAGS = [
    "grammar::n5",
    "category::numbers",
    "form::cardinal",
    "counting-v1",
]

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
    "NativeTTS",
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
            " 毎日[まいにち]、 テレビを "
            "{{c1::見[み]ます}}。"
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
            " 毎日[まいにち]、 日本語[にほんご]の 本[ほん]を "
            "{{c1::読[よ]みます}}。"
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
            " 毎日[まいにち]、 日本語[にほんご]を "
            "{{c1::勉強[べんきょう]します}}。"
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


TTS_SAMPLE_NOTE = {
    "SentenceFurigana": "毎朝[まいあさ]、 {{c1::七時[しちじ]に起[お]きます}}。",
    "Lesson": "Native TTS Trial",
    "Sequence": "128",
    "GrammarPoint": "Native Anki text-to-speech",
    "Pattern": "{{tts ja_JP voices=O-ren_(Enhanced),O-ren,Apple_O-ren_(Enhanced),Apple_O-ren,Siri,Apple_Siri,Kyoko_(Enhanced),Kyoko,Apple_Kyoko_(Enhanced),Apple_Kyoko:Sentence}}",
    "SentenceEnglish": "I wake up at seven every morning.",
    "Sentence": "毎朝、七時に起きます。",
    "Cue": "起きる → polite nonpast",
    "Target": "起きる",
    "TargetReading": "おきる",
    "Answer": "起きます",
    "AnswerReading": "おきます",
    "TargetClass": "Ichidan",
    "Explanation": "This sample uses Anki's native Japanese TTS on the back of the card.",
    "Notes": "Try the replay button labeled by your Anki client; no audio file is stored for this note.",
    "SentenceAudio": "",
    "NativeTTS": "1",
    "TargetFrequency": "9999",
    "Source": "tts-native-sample-001",
}


def normalize_fields(fields):
    """Add optional model fields when loading older note datasets."""
    fields.setdefault("NativeTTS", "1")
    return fields


def validate_cloze_markup(value, source):
    """Accept repeated c1 spans used to hide ruby text and answer kana."""
    openings = value.count("{{c1::")
    closings = value.count("}}")
    if openings < 1 or openings != closings:
        raise RuntimeError(f"Invalid c1 cloze markup: {source}")


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


def read_counting_notes(directory):
    with open(os.path.join(directory, "counting_notes.json"), encoding="utf-8") as file:
        return json.load(file)


def read_n5_core_notes(directory):
    with open(os.path.join(directory, "n5_core_notes.json"), encoding="utf-8") as file:
        return json.load(file)


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
        normalize_fields(fields)
        missing = [field for field in FIELDS if field not in fields]
        if missing:
            raise RuntimeError(f"POC note is missing fields: {missing}")
        if fields["Source"] in sources:
            raise RuntimeError(f"Duplicate Source: {fields['Source']}")
        sources.add(fields["Source"])
        validate_cloze_markup(fields["SentenceFurigana"], fields["Source"])
        if fields["Answer"] not in fields["Sentence"]:
            raise RuntimeError(f"Answer missing from Sentence: {fields['Source']}")


def validate_counting_notes(notes):
    sources = set()
    for fields in notes:
        normalize_fields(fields)
        missing = [field for field in FIELDS if field not in fields]
        if missing:
            raise RuntimeError(f"Counting note is missing fields: {missing}")
        if fields["Source"] in sources:
            raise RuntimeError(f"Duplicate Source: {fields['Source']}")
        sources.add(fields["Source"])
        validate_cloze_markup(fields["SentenceFurigana"], fields["Source"])
        if fields["Target"] not in fields["Sentence"]:
            raise RuntimeError(f"Target missing from Sentence: {fields['Source']}")
        if fields["Answer"] != fields["Target"]:
            raise RuntimeError(f"Answer must match Target: {fields['Source']}")


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


def install_counting(directory, dry_run=False):
    notes = read_counting_notes(directory)
    validate_counting_notes(notes)
    if dry_run:
        print(f"Would create deck: {DECK_NAME}")
        for fields in notes:
            print(
                f"Would add sequence {fields['Sequence']}: "
                f"{fields['Target']} ({fields['TargetReading']})"
            )
        return

    invoke("createDeck", deck=DECK_NAME)
    added_note_ids = []
    for fields in notes:
        existing = invoke(
            "findNotes",
            query=f'note:"{MODEL_NAME}" Source:{fields["Source"]}',
        )
        if existing:
            invoke(
                "updateNoteFields",
                note={"id": existing[0], "fields": fields},
            )
            invoke("addTags", notes=[existing[0]], tags=" ".join(COUNTING_TAGS))
            print(f"Updated counting note: {fields['Source']}")
            continue
        note_id = invoke(
            "addNote",
            note={
                "deckName": DECK_NAME,
                "modelName": MODEL_NAME,
                "fields": fields,
                "options": {"allowDuplicate": False},
                "tags": COUNTING_TAGS,
            },
        )
        added_note_ids.append(note_id)
        print(f"Added counting note: {fields['Source']}")

    if added_note_ids:
        print(f"Added {len(added_note_ids)} counting cards in Sequence order")


def validate_n5_core_notes(notes):
    sources = set()
    for fields in notes:
        normalize_fields(fields)
        missing = [field for field in FIELDS if field not in fields]
        if missing:
            raise RuntimeError(f"N5 core note is missing fields: {missing}")
        if fields["Source"] in sources:
            raise RuntimeError(f"Duplicate Source: {fields['Source']}")
        sources.add(fields["Source"])
        validate_cloze_markup(fields["SentenceFurigana"], fields["Source"])
        if fields["Answer"] not in fields["Sentence"]:
            raise RuntimeError(f"Answer missing from Sentence: {fields['Source']}")


def install_n5_core(directory, dry_run=False):
    notes = read_n5_core_notes(directory)
    validate_n5_core_notes(notes)
    if dry_run:
        print(f"Would create deck: {DECK_NAME}")
        for fields in notes:
            print(
                f"Would add sequence {fields['Sequence']}: "
                f"{fields['Lesson']} — {fields['Answer']}"
            )
        return

    invoke("createDeck", deck=DECK_NAME)
    added_note_ids = []
    for fields in notes:
        existing = invoke(
            "findNotes",
            query=f'note:"{MODEL_NAME}" Source:{fields["Source"]}',
        )
        if existing:
            invoke(
                "updateNoteFields",
                note={"id": existing[0], "fields": fields},
            )
            invoke("addTags", notes=[existing[0]], tags=" ".join(N5_CORE_TAGS))
            print(f"Updated N5 core note: {fields['Source']}")
            continue
        note_id = invoke(
            "addNote",
            note={
                "deckName": DECK_NAME,
                "modelName": MODEL_NAME,
                "fields": fields,
                "options": {"allowDuplicate": False},
                "tags": N5_CORE_TAGS,
            },
        )
        added_note_ids.append(note_id)
        print(f"Added N5 core note: {fields['Source']}")

    if added_note_ids:
        print(f"Added {len(added_note_ids)} N5 core cards in Sequence order")


def install_tts_sample(dry_run=False):
    fields = normalize_fields(dict(TTS_SAMPLE_NOTE))
    if dry_run:
        print(f"Would create deck: {DECK_NAME}")
        print(f"Would add native TTS sample: {fields['Source']}")
        return

    invoke("createDeck", deck=DECK_NAME)
    existing = invoke(
        "findNotes",
        query=f'note:"{MODEL_NAME}" Source:{fields["Source"]}',
    )
    if existing:
        invoke("updateNoteFields", note={"id": existing[0], "fields": fields})
        invoke("addTags", notes=[existing[0]], tags=" ".join(TTS_SAMPLE_TAGS))
        print(f"Updated native TTS sample: {fields['Source']}")
        return

    note_id = invoke(
        "addNote",
        note={
            "deckName": DECK_NAME,
            "modelName": MODEL_NAME,
            "fields": fields,
            "options": {"allowDuplicate": False},
            "tags": TTS_SAMPLE_TAGS,
        },
    )
    print(f"Added native TTS sample: {fields['Source']} ({note_id})")


def enable_native_tts(dry_run=False):
    query = f'deck:"{DECK_NAME}" note:"{MODEL_NAME}"'
    note_ids = invoke("findNotes", query=query)
    if dry_run:
        print(f"Would enable native TTS for {len(note_ids)} Grammar notes")
        return

    infos = invoke("notesInfo", notes=note_ids)
    updated = 0
    for info in infos:
        fields = {name: value["value"] for name, value in info["fields"].items()}
        if fields.get("NativeTTS") == "1":
            continue
        fields["NativeTTS"] = "1"
        invoke("updateNoteFields", note={"id": info["noteId"], "fields": fields})
        updated += 1
    print(f"Enabled native TTS: updated={updated}, already_enabled={len(note_ids) - updated}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enable-native-tts",
        action="store_true",
        help="Enable native Anki TTS on every Grammar note.",
    )
    parser.add_argument(
        "--install-poc",
        action="store_true",
        help="Create the deck and install the three proof-of-concept notes.",
    )
    parser.add_argument(
        "--install-n5-core",
        action="store_true",
        help="Create the deck and install the Phase 1 N5 grammar notes.",
    )
    parser.add_argument(
        "--install-tts-sample",
        action="store_true",
        help="Create or update one sample note using native Anki TTS.",
    )
    parser.add_argument(
        "--install-counting",
        action="store_true",
        help="Create the deck and install the counting lesson notes.",
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
    if args.enable_native_tts:
        enable_native_tts(dry_run=args.dry_run)
    elif args.install_poc:
        install_media(directory, dry_run=args.dry_run)
        install_poc(dry_run=args.dry_run)
    elif args.install_tts_sample:
        install_tts_sample(dry_run=args.dry_run)
    elif args.install_counting:
        install_counting(directory, dry_run=args.dry_run)
    elif args.install_n5_core:
        install_n5_core(directory, dry_run=args.dry_run)
    elif args.dry_run:
        print("No notes requested; pass --install-poc, --install-tts-sample, --install-counting, or --install-n5-core")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
