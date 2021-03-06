
from pathlib import Path
import json

import utils
import exceptions

PATH = Path('/home/bob/repos/devdocs/public/docs')

ALIASES = {
    'python': 'python~3.6',
    'js': 'javascript',
    'events': 'dom_events'
}


def available_identifiers():
    """The available names which can be used to identify a doc set."""
    return sorted(_identifiers_to_doc_sets().keys())


def from_identifier(identifier):
    """Return the corresponding doc set name given a valid identifier."""
    try:
        return _identifiers_to_doc_sets()[identifier]
    except KeyError:
        raise exceptions.UnknownDocSetException()


def _identifiers_to_doc_sets():
    return utils.available_aliases(_available_doc_sets(), ALIASES)


def _available_doc_sets():
    return [path.name for path in PATH.iterdir() if path.is_dir()]


def index(doc_set):
    """Get dict of entry names to data for given doc set"""
    index_file = path(doc_set).joinpath('index.json')
    with index_file.open() as f:
        index = json.load(f)

    index_entries = {
        entry['name']: entry for entry in index['entries']
    }
    return index_entries


def path(doc_set):
    return PATH.joinpath(doc_set)
