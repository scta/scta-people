#!/usr/bin/env python3
"""Add a new person to Prosopography.xml with a fresh per-XXXXXX id.

Usage:
    python3 add_person.py --name "Jacques Paul Migne" --wikidata Q326431 [--category Other] [--note "..."]
    python3 add_person.py --issue-body -    # parse a GitHub issue form body from stdin

The record is inserted as text at the end of the chosen <listPerson type="...">
so the rest of the file's formatting and comments are left untouched. Run
update_supplement.py --missing-only afterwards to fetch dates and description.

When run inside GitHub Actions, the new id, name and Wikidata label/description
are also written to $GITHUB_OUTPUT.
"""

import argparse
import os
import random
import re
import string
import sys
from xml.sax.saxutils import escape

from update_supplement import PROSOPOGRAPHY, fetch_entities

CATEGORIES = ["Arabic", "Biblical", "Classical", "Divine", "Patristic", "Scholastic", "Other"]

# Headings used in .github/ISSUE_TEMPLATE/new-person.yml
ISSUE_FIELDS = {
    "Preferred name": "name",
    "Wikidata ID": "wikidata",
    "Category": "category",
    "Note": "note",
}


def parse_issue_body(body):
    """Parse the '### Heading\\n\\nvalue' markdown GitHub renders for issue forms."""
    values = {}
    for section in re.split(r"^### ", body, flags=re.MULTILINE)[1:]:
        heading, _, value = section.partition("\n")
        value = value.strip()
        if heading.strip() in ISSUE_FIELDS and value != "_No response_":
            values[ISSUE_FIELDS[heading.strip()]] = value
    return values


def new_person_id(text):
    existing = set(re.findall(r'xml:id="([^"]+)"', text))
    alphabet = string.ascii_letters + string.digits
    while True:
        candidate = "per-" + "".join(random.choices(alphabet, k=6))
        if candidate not in existing:
            return candidate


def add_person(name, qid, category, note):
    text = PROSOPOGRAPHY.read_text(encoding="utf-8")

    existing = re.search(
        rf'<person xml:id="([^"]+)">(?:(?!</person>).)*<note type="wikidata-id">\s*{qid}\s*</note>',
        text, flags=re.DOTALL,
    )
    if existing:
        raise ValueError(f"{qid} is already in Prosopography.xml as {existing.group(1)}.")

    entity = fetch_entities([qid]).get(qid, {})
    if not entity or "missing" in entity:
        raise ValueError(f"{qid} was not found on Wikidata.")

    # Insert before the closing tag of the chosen category, matching its indentation.
    start = text.find(f'<listPerson type="{category}">')
    close = re.compile(r"^([ \t]*)</listPerson>", flags=re.MULTILINE).search(text, start)
    indent = close.group(1) + "  "

    person_id = new_person_id(text)
    lines = [
        f'{indent}<person xml:id="{person_id}">',
        f'{indent}  <persName xml:lang="en">{escape(name)}</persName>',
        f'{indent}  <note type="wikidata-id">{qid}</note>',
    ]
    if note:
        # XML comments may not contain "--" or end with "-".
        note = " ".join(note.split()).replace("--", "–").rstrip("-")
        lines.append(f"{indent}  <!-- {note} -->")
    lines.append(f"{indent}</person>")

    text = text[:close.start()] + "\n".join(lines) + "\n" + text[close.start():]
    PROSOPOGRAPHY.write_text(text, encoding="utf-8")

    return person_id, entity


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--name")
    parser.add_argument("--wikidata")
    parser.add_argument("--category", default="Scholastic", choices=CATEGORIES)
    parser.add_argument("--note")
    parser.add_argument("--issue-body", metavar="FILE", help="GitHub issue form body ('-' for stdin)")
    args = parser.parse_args()

    values = {"category": args.category}
    if args.issue_body:
        body = sys.stdin.read() if args.issue_body == "-" else open(args.issue_body).read()
        values.update(parse_issue_body(body))
    for key in ("name", "wikidata", "note"):
        if getattr(args, key):
            values[key] = getattr(args, key)

    name = " ".join(values.get("name", "").split())
    qid = values.get("wikidata", "").strip().upper()
    # Accept a pasted Wikidata URL as well as a bare id.
    match = re.search(r"Q\d+$", qid.rstrip("/"))
    try:
        if not name:
            raise ValueError("A preferred name is required.")
        if not match:
            raise ValueError(f'"{values.get("wikidata", "")}" is not a Wikidata id like Q326431.')
        if values["category"] not in CATEGORIES:
            raise ValueError(f'Unknown category "{values["category"]}".')
        person_id, entity = add_person(name, match.group(0), values["category"], values.get("note"))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    label = entity.get("labels", {}).get("en", {}).get("value", "")
    description = entity.get("descriptions", {}).get("en", {}).get("value", "")
    print(f"added {person_id} ({name}, {match.group(0)}) to {values['category']}", file=sys.stderr)

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            for key, value in [("person_id", person_id), ("name", name), ("qid", match.group(0)),
                               ("wikidata_label", label), ("wikidata_description", description)]:
                out.write(f"{key}={' '.join(value.split())}\n")


if __name__ == "__main__":
    main()
