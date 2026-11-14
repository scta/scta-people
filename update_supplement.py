#!/usr/bin/env python3
"""Regenerate ProsopographySupplement.xml from Wikidata.

Reads every <person> in Prosopography.xml that has a <note type="wikidata-id">,
fetches the English description, date of birth (P569) and date of death (P570)
from Wikidata, and writes them to ProsopographySupplement.xml, which is read by
scta-rdf/xsl_stylesheets/rdf_names_conversion.xsl.

Usage (from anywhere):
    python3 update_supplement.py               # refetch everyone
    python3 update_supplement.py --missing-only  # only people not yet in the supplement

Uses only the Python standard library.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
PROSOPOGRAPHY = ROOT / "Prosopography.xml"
SUPPLEMENT = ROOT / "ProsopographySupplement.xml"

TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

API = "https://www.wikidata.org/w/api.php"
# Wikidata asks API clients to identify themselves.
USER_AGENT = "scta-people-supplement/1.0 (https://scta.info)"
BATCH_SIZE = 50  # max ids per wbgetentities request

# Wikidata time precision codes coarser than a year. Such dates are still kept
# (they help order authors roughly) but are marked with a precision attribute.
PRECISION_LABELS = {8: "decade", 7: "century", 6: "millennium"}


def read_people():
    """Return [(shortId, Qid)] in document order."""
    root = ET.parse(PROSOPOGRAPHY).getroot()
    people = []
    for person in root.iter(TEI + "person"):
        short_id = person.get(XML_ID)
        qids = [
            (n.text or "").strip()
            for n in person.findall(TEI + "note")
            if n.get("type") == "wikidata-id" and (n.text or "").strip()
        ]
        if not short_id or not qids:
            continue
        if len(qids) > 1:
            print(f"warning: {short_id} has several wikidata ids, using {qids[0]}", file=sys.stderr)
        people.append((short_id, qids[0]))
    return people


def read_existing_supplement():
    """Return {shortId: {field: (value, precision)}} from the current supplement, if any."""
    if not SUPPLEMENT.exists() or SUPPLEMENT.stat().st_size == 0:
        return {}
    existing = {}
    for person in ET.parse(SUPPLEMENT).getroot().findall("person"):
        short_id = person.findtext("shortId")
        if short_id:
            existing[short_id] = {
                el.tag: (el.text, el.get("precision"))
                for el in person
                if el.tag != "shortId" and el.text
            }
    return existing


def fetch_entities(qids):
    """Fetch entities from Wikidata in batches. Returns {Qid: entity}."""
    entities = {}
    for i in range(0, len(qids), BATCH_SIZE):
        batch = qids[i:i + BATCH_SIZE]
        params = urllib.parse.urlencode({
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "descriptions|claims",
            "languages": "en",
            "format": "json",
        })
        request = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": USER_AGENT})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = json.load(response)
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise
                time.sleep(2 ** attempt * 5)
        if "error" in data:
            raise RuntimeError(f"Wikidata error: {data['error']}")
        for qid, entity in data.get("entities", {}).items():
            # Follow redirects: the API keys redirected entities by the requested id.
            entities[qid] = entity
        print(f"fetched {min(i + BATCH_SIZE, len(qids))}/{len(qids)}", file=sys.stderr)
    return entities


def best_claim(entity, prop):
    """Preferred-rank claim if there is one, else the first normal-rank claim with a value."""
    claims = [
        c for c in entity.get("claims", {}).get(prop, [])
        if c.get("rank") != "deprecated" and c["mainsnak"].get("snaktype") == "value"
    ]
    preferred = [c for c in claims if c.get("rank") == "preferred"]
    return (preferred or claims or [None])[0]


def year(entity, prop):
    """Return (year, precision) for a time claim, or None.

    year is a four-digit string ('-0384' for BC); precision is None for year
    precision or finer, else a label like 'century'.
    """
    claim = best_claim(entity, prop)
    if not claim:
        return None
    value = claim["mainsnak"]["datavalue"]["value"]
    precision = value.get("precision", 9)
    # time looks like "+1316-00-00T00:00:00Z" or "-0384-00-00T00:00:00Z"
    sign, rest = value["time"][0], value["time"][1:]
    y = int(rest.split("-")[0])
    label = None if precision >= 9 else PRECISION_LABELS.get(precision, "coarser")
    return (f"-{y:04d}" if sign == "-" else f"{y:04d}"), label


def extract(entity, short_id):
    if "missing" in entity:
        print(f"warning: {short_id} points to a missing Wikidata entity {entity.get('id')}", file=sys.stderr)
        return {}
    description = entity.get("descriptions", {}).get("en", {}).get("value")
    fields = {
        "dateofbirth": year(entity, "P569"),
        "dateofdeath": year(entity, "P570"),
        "description": (description, None) if description else None,
    }
    return {k: v for k, v in fields.items() if v}


def write_supplement(rows):
    """Write in the same flat format the old extract.js produced."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<persons>"]
    for short_id, fields in rows:
        lines.append("<person>")
        lines.append(f"<shortId>{escape(short_id)}</shortId>")
        for tag in ("dateofbirth", "dateofdeath", "description"):
            if fields.get(tag):
                text, precision = fields[tag]
                attr = f' precision="{precision}"' if precision else ""
                lines.append(f"<{tag}{attr}>{escape(text)}</{tag}>")
        lines.append("</person>")
    lines.append("</persons>")
    SUPPLEMENT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--missing-only", action="store_true",
        help="keep existing supplement entries and only fetch people not yet in it",
    )
    args = parser.parse_args()

    people = read_people()
    existing = read_existing_supplement() if args.missing_only else {}
    to_fetch = sorted({qid for short_id, qid in people if short_id not in existing})
    entities = fetch_entities(to_fetch) if to_fetch else {}

    rows = []
    for short_id, qid in people:
        if short_id in existing:
            fields = existing[short_id]
        elif qid in entities:
            fields = extract(entities[qid], short_id)
        else:
            print(f"warning: no Wikidata response for {short_id} ({qid})", file=sys.stderr)
            fields = {}
        if fields:
            rows.append((short_id, fields))

    write_supplement(rows)
    print(f"wrote {len(rows)} people to {SUPPLEMENT.name} "
          f"({len(to_fetch)} fetched from Wikidata)", file=sys.stderr)


if __name__ == "__main__":
    main()
