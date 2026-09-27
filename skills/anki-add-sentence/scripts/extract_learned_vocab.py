import json
import re
import urllib.request
import urllib.error
import argparse

def invoke(action, **params):
    payload = json.dumps(
        {"action": action, "version": 6, "params": params}
    ).encode("utf-8")
    try:
        req = urllib.request.Request(
            "http://localhost:8765",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as response:
            res = json.load(response)
            if res.get("error"):
                raise Exception(res["error"])
            return res
    except urllib.error.URLError as e:
        raise Exception(f"Failed to connect to AnkiConnect: {e}")

def clean_html(text):
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def get_learned_words(decks):
    learned_words = set()

    for deck in decks:
        query = f'deck:"{deck["name"]}" prop:ivl>=1'
        note_ids = invoke("findNotes", query=query).get("result", [])
        if not note_ids:
            continue

        notes = invoke("notesInfo", notes=note_ids).get("result", [])
        for note in notes:
            for source_field in deck["source_fields"]:
                word = note.get("fields", {}).get(source_field, {}).get("value")
                if word:
                    cleaned = clean_html(word)
                    if cleaned:
                        learned_words.add(cleaned)
                    break

    return sorted(list(learned_words))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract learned vocabulary from configured Anki decks."
    )
    parser.add_argument(
        "--deck",
        action="append",
        required=True,
        help="Anki deck to query; repeat for multiple decks.",
    )
    parser.add_argument(
        "--source-field",
        action="append",
        required=True,
        help="Field containing vocabulary; repeat in the same order as --deck.",
    )
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()
        if len(args.source_field) == 1:
            source_fields = args.source_field * len(args.deck)
        elif len(args.source_field) == len(args.deck):
            source_fields = args.source_field
        else:
            raise ValueError(
                "Pass one --source-field for all decks or one for each --deck."
            )

        decks = [
            {"name": name, "source_fields": [source_field]}
            for name, source_field in zip(args.deck, source_fields)
        ]

        words = get_learned_words(decks)
        print("\n".join(words))
    except Exception as e:
        print(f"Error: {e}")
