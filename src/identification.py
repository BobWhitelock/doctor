
from fuzzywuzzy import fuzz, process

import docset
from docsentry import DocsEntry
from utils import debug


def identify(doc_set_name, search_term):
    index = docset.index(doc_set_name)

    match = _match_search_term(search_term, index)
    debug('Identified as: %s', match)

    entry = DocsEntry(doc_set_name, match['path'])
    debug('Entry: %s', entry)

    return entry


def _match_search_term(search_term, index):
    def do_search(extract_function, scorer, **kwargs):
        return extract_function(
            search_term,
            index.keys(),
            scorer=scorer,
            processor=_process_search_term,
            limit=50,
            **kwargs
        )

    matches = do_search(
        process.extractBests,
        fuzz.token_set_ratio,
        score_cutoff=40
    )
    if not matches:
        debug('No close matches; falling back to simpler search method')
        matches = do_search(process.extract, fuzz.ratio)

    sorted_matches = sorted(
        matches,
        key=_match_sort_key,
    )

    _log_matches(sorted_matches)

    match_name, _ = sorted_matches[0]
    return index[match_name]


def _process_search_term(search_term):
    """Simple processor for search term

    Needed as default processor (`fuzzywuzzy.utils.full_process`) strips all
    non-alphanumeric characters, but we want to be able to search for `==` etc.
    """
    return search_term.lower().strip()


def _match_sort_key(match):
    name, match_score = match

    # Sort matches based on how well they match, then favour shorter matches to
    # break ties.
    return -match_score, len(name)


def _log_matches(matches):
    for match, score in matches:
        debug('Match: %s - %s%%', match, score)
