
from pathlib import Path
import json

PATH = Path('/home/bob/repos/devdocs/public/docs')


def available_languages():
    return [path.name for path in PATH.iterdir() if path.is_dir()]


def language_index(language):
    """Get dict of entry names to data for given language"""
    index_file = language_docs_path(language).joinpath('index.json')
    with index_file.open() as f:
        index = json.load(f)

    index_entries = {
        entry['name']: entry for entry in index['entries']
    }
    return index_entries


def language_docs_path(language):
    return PATH.joinpath(language)
