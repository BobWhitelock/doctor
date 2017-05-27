
from fuzzywuzzy import fuzz, process

import docset
from docsentry import DocsEntry


def identify(language, search_term):
    index = docset.language_index(language)

    match = match_search_term(search_term, index)
    return DocsEntry(language, match['path'])


def match_search_term(search_term, index):
    def do_search(extract_function, scorer, **kwargs):
        return extract_function(
            search_term,
            index.keys(),
            scorer=scorer,
            processor=process_search_term,
            limit=50,
            **kwargs
        )

    matches = do_search(
        process.extractBests,
        fuzz.token_set_ratio,
        score_cutoff=40
    )
    if not matches:
        # If no close matches, fall back to simpler method and use those.
        matches = do_search(process.extract, fuzz.ratio)

    sorted_matches = sorted(
        matches,
        key=match_sort_key,
    )
    print("matches:", sorted_matches)  # TODO log/use this better

    match_name, _ = sorted_matches[0]
    return index[match_name]


def process_search_term(search_term):
    """Simple processor for search term

    Needed as default processor (`fuzzywuzzy.utils.full_process`) strips all
    non-alphanumeric characters, but we want to be able to search for `==` etc.
    """
    return search_term.lower().strip()


def match_sort_key(match):
    name, match_score = match

    # Sort matches based on how well they match, then favour shorter matches to
    # break ties.
    return -match_score, len(name)
