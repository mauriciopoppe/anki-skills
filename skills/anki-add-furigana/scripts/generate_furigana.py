#!/usr/bin/env python3
"""Generate contextual Anki furigana while preserving native Cloze markup.

This helper takes a clean sentence and an exact answer substring, writes
Anki's ``漢字[よみ]`` syntax to the target field, and leaves the complete
furigana-bearing answer inside one native Cloze. The card template must apply
the filters in this order: ``{{furigana:cloze:Field}}``.

Dependencies: ``fugashi`` and ``unidic-lite``.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from fugashi import Tagger


ANKI_CONNECT_URL = "http://localhost:8765"
KANJI_RE = re.compile(r"[一-龯々〆ヵヶ]")
READING_RE = re.compile(
    r"(?P<surface>[0-9一-龯々〆ヵヶ]+)\[(?P<reading>[ぁ-ゖー]+)\]"
)


def to_hiragana(text: str) -> str:
    """Convert katakana readings returned by UniDic to hiragana."""

    return "".join(
        chr(ord(char) - 0x60) if "ァ" <= char <= "ヺ" else char
        for char in text
    )


def is_kanji(char: str) -> bool:
    return bool(KANJI_RE.fullmatch(char))


@dataclass(frozen=True)
class Piece:
    """A rendered piece and the source-character range it represents."""

    start: int
    end: int
    text: str


def _components(surface: str) -> list[tuple[int, int, bool]]:
    """Return contiguous (start, end, is_kanji) surface components."""

    if not surface:
        return []
    components: list[tuple[int, int, bool]] = []
    start = 0
    current = is_kanji(surface[0])
    for index, char in enumerate(surface[1:], 1):
        kind = is_kanji(char)
        if kind != current:
            components.append((start, index, current))
            start = index
            current = kind
    components.append((start, len(surface), current))
    return components


def _consume_kana(reading: str, cursor: int, surface: str) -> int:
    """Advance a reading cursor over a kana component when possible."""

    expected = to_hiragana(surface)
    if reading.startswith(expected, cursor):
        return cursor + len(expected)
    # UniDic can report a pronunciation that differs from the spelling (for
    # example は pronounced わ).  In that case leave alignment to the next
    # kanji component instead of inventing a reading for kana.
    return cursor


def render_token(
    surface: str,
    reading: str,
) -> list[Piece]:
    """Render one UniDic token as Anki furigana pieces.

    Cloze wrapping happens after tokenization, around the complete answer.
    This keeps multiword grammar expressions as one native Cloze.
    """

    components = _components(surface)
    if not components or not any(kanji for _, _, kanji in components):
        pieces = [Piece(0, len(surface), surface)] if surface else []
    else:
        hira_reading = to_hiragana(reading)
        kanji_runs = sum(1 for _, _, kanji in components if kanji)
        if kanji_runs > 1 and any(not kanji for _, _, kanji in components):
            return [
                Piece(
                    0,
                    len(surface),
                    surface if not hira_reading else f"{surface}[{hira_reading}]",
                )
            ]
        cursor = 0
        pieces = []
        for component_index, (start, end, kanji) in enumerate(components):
            text = surface[start:end]
            if not kanji:
                pieces.append(Piece(start, end, text))
                cursor = _consume_kana(hira_reading, cursor, text)
                continue

            # A following kana component is the okurigana for this kanji run.
            following_kana = ""
            if component_index + 1 < len(components):
                next_start, next_end, next_is_kanji = components[component_index + 1]
                if not next_is_kanji:
                    following_kana = surface[next_start:next_end]

            suffix = to_hiragana(following_kana)
            suffix_start = (
                hira_reading.find(suffix, cursor) if suffix else -1
            )
            if suffix_start >= 0:
                chunk = hira_reading[cursor:suffix_start]
            else:
                chunk = hira_reading[cursor:]
            cursor += len(chunk)
            rendered = text if not chunk else f"{text}[{chunk}]"
            pieces.append(Piece(start, end, rendered))

    return pieces


def existing_readings(value: str) -> dict[str, str]:
    """Read supplied annotations so regeneration does not discard corrections."""

    readings = {
        match.group("surface"): match.group("reading")
        for match in READING_RE.finditer(value or "")
    }
    return readings


def generate_furigana(
    sentence: str,
    answer: str,
    tagger: Tagger | None = None,
    cloze_index: int = 1,
    existing: str = "",
    include_cloze: bool = True,
) -> str:
    """Generate furigana, optionally hiding the answer with one Cloze."""

    if not sentence:
        raise ValueError("Sentence is empty")
    if not answer or sentence.count(answer) != 1:
        raise ValueError(f"Answer must occur exactly once in Sentence: {answer!r}")
    target_start = sentence.index(answer)
    target_end = target_start + len(answer)
    tagger = tagger or Tagger()

    output: list[str] = []
    supplied_readings = existing_readings(existing)
    tokens = list(tagger(sentence))
    cursor = 0
    token_index = 0
    cloze_open = False
    while token_index < len(tokens):
        token = tokens[token_index]
        surface = token.surface
        start = sentence.find(surface, cursor)
        if start < 0:
            raise ValueError(f"Could not align token {surface!r} in {sentence!r}")
        if start > cursor:
            output.append(sentence[cursor:start])
        end = start + len(surface)
        reading = token.feature.kana or ""
        # Prefer a reading that was already supplied by the user.  This also
        # preserves compound readings such as 日本語[にほんご] when UniDic
        # tokenizes the same text as 日本 + 語.
        selected_surface = surface
        selected_end = end
        selected_reading = None
        for candidate in sorted(supplied_readings, key=len, reverse=True):
            if not sentence.startswith(candidate, start):
                continue
            candidate_end = start + len(candidate)
            if start < target_end and candidate_end > target_start:
                # Keep supplied readings that fit entirely inside the answer,
                # while avoiding annotations that cross its Cloze boundary.
                if start < target_start or candidate_end > target_end:
                    continue
            covered = 0
            covered_length = 0
            while token_index + covered < len(tokens):
                next_surface = tokens[token_index + covered].surface
                next_start = start + covered_length
                if sentence.find(next_surface, next_start) != next_start:
                    break
                covered += 1
                covered_length += len(next_surface)
                if start + covered_length >= candidate_end:
                    break
            if start + covered_length == candidate_end:
                selected_surface = candidate
                selected_end = candidate_end
                selected_reading = supplied_readings[candidate]
                token_index += covered - 1
                break
        if selected_reading is None:
            selected_reading = reading
        overlaps_target = start < target_end and selected_end > target_start
        if overlaps_target and (start < target_start or selected_end > target_end):
            raise ValueError(
                f"Cloze boundary splits token {selected_surface!r}: "
                f"{target_start}:{target_end} vs {start}:{selected_end}"
            )
        starts_cloze = include_cloze and overlaps_target and not cloze_open
        rendered_pieces = render_token(selected_surface, selected_reading)
        rendered_token = "".join(piece.text for piece in rendered_pieces)
        if include_cloze and overlaps_target:
            if not cloze_open:
                rendered_token = f"{{{{c{cloze_index}::{rendered_token}"
                cloze_open = True
            if selected_end == target_end:
                rendered_token += "}}"
                cloze_open = False
        # Anki's furigana parser needs a boundary between adjacent lexical
        # units.  Without it, ``先生[せんせい]、時間[じかん]`` can be parsed as
        # one ruby element whose base incorrectly includes ``、時間``.
        needs_boundary = starts_cloze or ("[" in rendered_token and not overlaps_target)
        if (
            needs_boundary
            and output
            and not output[-1].endswith(" ")
        ):
            output.append(" ")
        output.append(rendered_token)
        cursor = selected_end
        token_index += 1
    output.append(sentence[cursor:])
    if include_cloze and cloze_open:
        raise ValueError("Cloze target did not close at the answer boundary")
    result = "".join(output)
    if include_cloze and result.count(f"{{{{c{cloze_index}::") != 1:
        raise ValueError("Generated output has no Cloze")
    return result


def invoke(action: str, **params):
    payload = json.dumps(
        {"action": action, "version": 6, "params": params}, ensure_ascii=False
    ).encode()
    request = urllib.request.Request(
        ANKI_CONNECT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not connect to AnkiConnect: {error}") from error
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result.get("result")


def fetch_notes(deck: str, model: str | None) -> list[dict]:
    query = f'deck:"{deck}"'
    if model:
        query += f' note:"{model}"'
    return invoke("notesInfo", notes=invoke("findNotes", query=query))


def numeric_sort_key(note: dict, field_name: str) -> tuple[float, int]:
    raw_value = note["fields"].get(field_name, {}).get("value", "")
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        value = float("inf")
    return value, note["noteId"]


def confirm_note(note: dict, target_field: str, generated: str) -> bool:
    fields = note["fields"]
    print(f"\nNote {note['noteId']} ({fields.get('Source', {}).get('value', '')})")
    print(f"old: {fields.get(target_field, {}).get('value', '')}")
    print(f"new: {generated}")
    return input("Apply this change? [y/N] ").strip().lower() == "y"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", required=True, help="Anki deck to process")
    parser.add_argument("--model", help="Optional Anki note type filter")
    parser.add_argument("--source-field", default="Sentence")
    parser.add_argument("--target-field", default="SentenceFurigana")
    parser.add_argument("--answer-field", default="Answer")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Approve each changed note before updating",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writes")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Allow non-interactive batches larger than 10 notes",
    )
    args = parser.parse_args()

    notes = fetch_notes(args.deck, args.model)
    notes.sort(key=lambda note: numeric_sort_key(note, "Sequence"))
    if args.limit is not None:
        notes = notes[: args.limit]
    tagger = Tagger()
    updates: list[dict] = []
    changed = 0
    for note in notes:
        fields = {name: value["value"] for name, value in note["fields"].items()}
        missing = [
            field
            for field in (args.source_field, args.target_field)
            if field not in fields
        ]
        if missing:
            raise RuntimeError(
                f"Note {note['noteId']} is missing field(s): {', '.join(missing)}"
            )
        if args.answer_field not in fields:
            raise RuntimeError(
                f"Note {note['noteId']} is missing field: {args.answer_field}"
            )
        answer = fields[args.answer_field]
        if not answer.strip():
            raise RuntimeError(f"Note {note['noteId']} has an empty answer field")
        generated = generate_furigana(
            fields[args.source_field],
            answer,
            tagger,
            existing=fields[args.target_field],
        )
        current = fields[args.target_field]
        status = "unchanged" if current == generated else "changed"
        print(f"{note['noteId']} {fields.get('Source', '')}: {status}")
        if current != generated:
            changed += 1
            if args.dry_run:
                print(f"  old: {current}")
                print(f"  new: {generated}")
            elif args.interactive and not confirm_note(
                note, args.target_field, generated
            ):
                print("  skipped")
            else:
                updates.append(
                    {
                        "action": "updateNoteFields",
                        "params": {
                            "note": {
                                "id": note["noteId"],
                                "fields": {args.target_field: generated},
                            }
                        },
                    }
                )
    if not args.dry_run and len(updates) > 10 and not args.interactive and not args.yes:
        raise RuntimeError("More than 10 notes requires --yes or --interactive")
    if updates:
        invoke("multi", actions=updates)
    suffix = " (dry run)" if args.dry_run else f"; applied {len(updates)}"
    print(f"Processed {len(notes)} notes; {changed} changed{suffix}")


if __name__ == "__main__":
    main()
