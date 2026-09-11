import urllib.request
import urllib.error
import json
import argparse
import os
import re

def invoke(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    try:
        req = urllib.request.Request("http://localhost:8765", data=payload, headers={'Content-Type': 'application/json'})
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

def extract_cloze_words(text):
    # Regex matches {{c1::target_word::hint}} or {{c1::target_word}}
    matches = re.findall(r'\{\{c\d+::(.*?)\}\}', text)
    words = []
    for m in matches:
        parts = m.split("::")
        if parts:
            word = parts[0].strip()
            if word:
                words.append(word)
    return words

def extract_words_from_note(note):
    fields = note.get('fields', {})

    # Check fields in order of preference
    raw_val = ""
    for field_name in ['Word', 'Expression', 'Word Furigana', 'ExpressionFurigana']:
        if field_name in fields:
            raw_val = fields[field_name].get('value', '')
            if raw_val:
                break

    if not raw_val:
        return []

    cleaned = clean_html(raw_val)
    if "{{c" in raw_val:
        clozes = extract_cloze_words(cleaned)
        if clozes:
            return clozes

    return [cleaned] if cleaned else []

def get_vocab_lists(deck_name, limit_learned, limit_next):
    # Query for learned cards (interval >= 1)
    learned_query = f'deck:"{deck_name}" prop:ivl>=1'
    learned_note_ids = invoke("findNotes", query=learned_query).get("result", [])

    # Query for new cards (interval == 0)
    new_query = f'deck:"{deck_name}" prop:ivl=0'
    new_note_ids = invoke("findNotes", query=new_query).get("result", [])

    # Fetch details for learned notes
    learned_words = set()
    if learned_note_ids:
        # Batch fetching if there are too many
        chunk_size = 500
        for i in range(0, len(learned_note_ids), chunk_size):
            chunk = learned_note_ids[i:i+chunk_size]
            notes_info = invoke("notesInfo", notes=chunk).get("result", [])
            for note in notes_info:
                words = extract_words_from_note(note)
                for w in words:
                    learned_words.add(w)

    # Sort learned words alphabetically
    sorted_learned = sorted(list(learned_words))
    if limit_learned and len(sorted_learned) > limit_learned:
        sorted_learned = sorted_learned[:limit_learned]

    # Fetch details for new notes
    new_words_raw = []
    if new_note_ids:
        # Retrieve in chunks
        chunk_size = 500
        for i in range(0, len(new_note_ids), chunk_size):
            chunk = new_note_ids[i:i+chunk_size]
            notes_info = invoke("notesInfo", notes=chunk).get("result", [])
            for note in notes_info:
                # Parse frequency if available to sort by it
                freq_val = 999999
                freq_field = note.get('fields', {}).get('Frequency', {})
                if freq_field:
                    try:
                        freq_val = int(clean_html(freq_field.get('value', '')))
                    except ValueError:
                        pass

                note_id = note.get('noteId', 0)
                words = extract_words_from_note(note)
                for w in words:
                    new_words_raw.append((w, freq_val, note_id))

    # Sort new words: first by frequency, then by note ID (chronological)
    new_words_raw.sort(key=lambda x: (x[1], x[2]))

    # De-duplicate next words while preserving order
    seen_next = set()
    ordered_next = []
    for w, _, _ in new_words_raw:
        # Ensure it's not already in learned words
        if w not in learned_words and w not in seen_next:
            seen_next.add(w)
            ordered_next.append(w)

    if limit_next:
        ordered_next = ordered_next[:limit_next]

    return sorted_learned, ordered_next

def main():
    parser = argparse.ArgumentParser(description='Generate an interactive vocabulary practice prompt for Gemini.')
    parser.add_argument('--deck', required=True, help='The name of the deck to query.')
    parser.add_argument('--limit-learned', type=int, default=1000, help='Maximum number of learned words to include.')
    parser.add_argument('--limit-next', type=int, default=10, help='Maximum number of new/upcoming words to practice.')
    parser.add_argument('--output', default='practice_prompt.md', help='Output path for the generated prompt.')
    parser.add_argument('--dry-run', action='store_true', help='Only print the extracted lists without writing to output.')

    args = parser.parse_args()

    print(f"Fetching vocabulary from deck '{args.deck}'...")
    try:
        learned, next_words = get_vocab_lists(args.deck, args.limit_learned, args.limit_next)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    print(f"Found {len(learned)} learned words/phrases.")
    print(f"Found {len(next_words)} upcoming words/phrases.")

    if args.dry_run:
        print("\n=== Learned Words (Sample/First 20) ===")
        print(", ".join(learned[:20]))
        print("\n=== Next Words to Practice ===")
        print(", ".join(next_words))
        return

    # Generate the prompt template
    prompt_content = f"""# Interactive Vocabulary Practice Session

You are an expert language tutor. The user is practicing vocabulary they study in Anki.
Your goal is to help them actively reinforce their vocabulary by writing answers to exercises.

## Context:
- Target Deck: `{args.deck}`
- Target Language: Auto-detect from vocabulary (typically French, Japanese, or Hindi)

## Vocabulary Databases:

### Learned Vocabulary (Words/phrases the user already knows):
{", ".join(learned)}

### Next Vocabulary (New/upcoming words/phrases to introduce and practice):
{", ".join(next_words)}

## Exercise Rules & Constraints:
1. **Act as an encouraging, professional, and interactive tutor.**
2. **Generate exactly 5 exercises** (e.g., translation from English/native language to the target language, fill-in-the-blank, or sentence composition).
3. **Strict Vocabulary Constraint**: Write all exercises and sentences using **ONLY** the words in the **Learned Vocabulary** list and the **Next Vocabulary** list. Do not introduce any new words that are not in these lists.
   * *Exceptions*: Extremely basic structural words/particles (like particles in Japanese, or basic prepositions in French) are allowed only if absolutely necessary to form valid sentences.
4. **Highlight New Words**: Bold any word from the **Next Vocabulary** list when it appears in an exercise (e.g. using `**` or `<b>`).
5. **Interactive Flow**: Ask the user to reply with their answers. Do not show the answers yet. Wait for the user's response, then grade their answers, explain any corrections in a friendly way, and provide the next 5 exercises.

---
Please begin the practice session now by greeting the user and presenting the first 5 exercises.
"""

    output_path = os.path.abspath(args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        print(f"Successfully generated practice prompt at: {output_path}")
    except Exception as e:
        print(f"Failed to write output file: {e}")
        exit(1)

if __name__ == "__main__":
    main()
