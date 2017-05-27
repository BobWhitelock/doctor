
from pathlib import Path
import json

PATH = Path('/home/bob/repos/devdocs/public/docs')


def available():
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
