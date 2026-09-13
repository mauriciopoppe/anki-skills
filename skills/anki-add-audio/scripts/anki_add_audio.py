#!/usr/bin/env python3
"""Generate local TTS audio for empty Anki note fields."""
import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

URL = "http://localhost:8765"
CLOZE = re.compile(r"{{c\d+::(.*?)(?:::[^{}]*?)?}}")
FURIGANA = re.compile(r" ?([^\s\[\]]+)\[([^\[\]]+)]")
HTML = re.compile(r"<[^>]+>")


def invoke(action, **params):
    body = json.dumps(
        {"action": action, "version": 6, "params": params}, ensure_ascii=False
    ).encode()
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                URL, data=body, headers={"Content-Type": "application/json"}
            )
        ) as response:
            result = json.load(response)
    except OSError as error:
        raise RuntimeError(f"Could not connect to AnkiConnect: {error}") from error
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result.get("result")


def normalize_for_speech(value):
    value = CLOZE.sub(lambda m: m.group(1), html.unescape(value or ""))
    value = HTML.sub("", value)
    value = FURIGANA.sub(lambda m: m.group(2), value)
    return re.sub(r"\s+", " ", value).strip()


def number(note, field):
    try:
        return float(
            HTML.sub("", note.get("fields", {}).get(field, {}).get("value", "")).strip()
        )
    except ValueError:
        return float("inf")


def eligible(args):
    ids = invoke("findNotes", query=f'deck:"{args.deck}"')
    notes = invoke("notesInfo", notes=ids) if ids else []
    for note in notes:
        missing = [
            f for f in (args.source_field, args.target_field) if f not in note["fields"]
        ]
        if missing:
            raise RuntimeError("Missing fields: " + ", ".join(missing))
    notes = [
        n
        for n in notes
        if n["fields"][args.source_field]["value"].strip()
        and not n["fields"][args.target_field]["value"].strip()
    ]
    notes.sort(key=lambda n: (number(n, args.sort_field), n["noteId"]))
    return notes[: args.limit]


def check_dependencies(voice):
    missing = [c for c in ("say", "ffmpeg") if not shutil.which(c)]
    if missing:
        raise RuntimeError("Missing commands: " + ", ".join(missing))
    voices = subprocess.run(
        ["say", "-v", "?"], check=True, capture_output=True, text=True
    ).stdout
    if not any(line.split(maxsplit=1)[0] == voice for line in voices.splitlines()):
        raise RuntimeError(f"Voice is not installed: {voice}")


def synthesize(text, voice, rate, path):
    with tempfile.TemporaryDirectory(prefix="anki-audio-") as d:
        aiff = os.path.join(d, "speech.aiff")
        subprocess.run(
            ["say", "-v", voice, "-r", str(rate), "-o", aiff, text], check=True
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                aiff,
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "4",
                path,
            ],
            check=True,
        )


def process(notes, args):
    updated = skipped = 0
    for note in notes:
        nid = note["noteId"]
        text = normalize_for_speech(note["fields"][args.source_field]["value"])
        if not text:
            skipped += 1
            continue
        if args.interactive and input(f"Generate {text!r}? [y/N] ").lower() != "y":
            skipped += 1
            continue
        name = f"anki-audio-{nid}-{hashlib.sha256(text.encode()).hexdigest()[:10]}.mp3"
        with tempfile.TemporaryDirectory(prefix="anki-audio-mp3-") as d:
            path = os.path.join(d, name)
            synthesize(text, args.voice, args.rate, path)
            data = base64.b64encode(Path(path).read_bytes()).decode()
        invoke("storeMediaFile", filename=name, data=data)
        invoke(
            "updateNoteFields",
            note={"id": nid, "fields": {args.target_field: f"[sound:{name}]"}},
        )
        invoke("addTags", notes=[nid], tags=f"anki_audio {dt.date.today().isoformat()}")
        print(f"Updated {nid}: {name}")
        updated += 1
    return updated, skipped


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--deck", required=True)
    p.add_argument("--source-field", default="Sentence")
    p.add_argument("--target-field", default="SentenceAudio")
    p.add_argument("--voice", default="Kyoko")
    p.add_argument("--rate", type=int, default=175)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--sort-field", default="Frequency")
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes", action="store_true")
    return p.parse_args()


def main():
    args = arguments()
    if args.limit < 1:
        raise RuntimeError("--limit must be greater than zero")
    notes = eligible(args)
    print(f"Eligible: {len(notes)}; voice={args.voice}; target={args.target_field}")
    for note in notes:
        value = note["fields"][args.source_field]["value"]
        preview = normalize_for_speech(value)[:100]
        print(f"{note['noteId']} | {preview}")
    if args.dry_run or not notes:
        return
    check_dependencies(args.voice)
    if len(notes) > 10 and not args.interactive and not args.yes:
        raise RuntimeError("More than 10 notes requires --yes or --interactive")
    updated, skipped = process(notes, args)
    print(f"Complete: updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
