
from fuzzywuzzy import fuzz, process
import json

from constants import DOC_PATH


def identify(language, search_term):
    language_docs = DOC_PATH.joinpath(language)

    index_file = language_docs.joinpath('index.json')
    with index_file.open() as f:
        index = json.load(f)

    index_entries = {
        entry['name']: entry for entry in index['entries']
    }

    matches = process.extract(
        search_term,
        index_entries.keys(),
        scorer=fuzz.partial_ratio,
        processor=process_search_term,
        limit=5,
    )
    print("matches:", matches)
    match_name, _ = matches[0]
    match = index_entries[match_name]

    entry_path = match['path'].split('#')[0] + '.html'
    doc_path = language_docs.joinpath(entry_path)
    return doc_path


def process_search_term(search_term):
    """Simple processor for search term

    Needed as default processor (`fuzzywuzzy.utils.full_process`) strips all
    non-alphanumeric characters, but we want to be able to search for `==` etc.
    """
    return search_term.lower().strip()
