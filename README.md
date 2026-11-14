# SCTA Prosopography

The list of people (authors, editors, and persons named in texts) used by the
[Scholastic Commentaries and Texts Archive (SCTA)](https://scta.info).

## Files

- **`Prosopography.xml`**: the main TEI list of persons, grouped by category (Arabic, Biblical, Classical, Divine, Patristic, Scholastic, Other). Each `<person>` has an `xml:id`, a preferred English name and, where possible, a Wikidata id.
- **`ProsopographySupplement.xml`**: birth year, death year and short description for each person, generated from Wikidata. Don't edit it by hand; it is rebuilt by `update_supplement.py`. Dates that Wikidata records only to the decade, century or millennium carry a `precision` attribute.
- **`add_person.py`**: adds a new person to `Prosopography.xml` with a new `per-xxxxxx` id.
- **`update_supplement.py`**: regenerates `ProsopographySupplement.xml` from Wikidata.
- **`sandbox/`**: older experiments (JSON-LD graphs); not used in production.

## Adding a person through a GitHub issue

You don't need to edit XML or know how pull requests work.

1. [Open a new "Add a person" issue](https://github.com/scta/scta-people/issues/new?template=new-person.yml).
2. Fill in:
   - **Preferred name**: the English form of the name as it should appear in the SCTA.
   - **Wikidata ID**: the Q-number from the person's Wikidata page, e.g. `Q326431` (a full Wikidata URL also works). [Search Wikidata](https://www.wikidata.org) if you don't know it.
   - **Category**: Scholastic by default.
   - **Note** (optional): context for editors, e.g. "editor of 1904 Godfrey quodlibet edition".
3. Submit the issue.

Within a minute, a pull request is opened that adds the person with a new id and pulls their dates and description from Wikidata. A link to it is posted on your issue. An editor then checks that the Wikidata entry is the intended person and merges it, which closes your issue.

If the request can't be processed (for example, the Wikidata id is already in the list or doesn't exist), the issue gets a comment explaining why.

## Working locally

Both scripts need only Python 3; there is nothing to install.

```sh
# add a person
python3 add_person.py --name "Jacques Paul Migne" --wikidata Q326431 --category Other

# fetch dates and descriptions for people not yet in the supplement
python3 update_supplement.py --missing-only

# or refresh everyone from Wikidata (review with git diff before committing)
python3 update_supplement.py
```

If you add a person to `Prosopography.xml` by hand, run `update_supplement.py --missing-only` afterwards. If you change an existing person's Wikidata id, run the full refresh, since `--missing-only` keeps existing entries as they are.

## License

Published under a [Creative Commons Attribution-NonCommercial-NoDerivs 3.0 License](http://creativecommons.org/licenses/by-nc-nd/3.0/).
