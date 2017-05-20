
from pathlib import Path
import json
from autorepr import autorepr


PATH = Path('/home/bob/repos/devdocs/public/docs')


class DocsEntry:

    def __init__(self, language, path):
        self.language = language

        if '#' in path:
            base_path, self.entry_id = path.split('#')
        else:
            base_path, self.entry_id = path, None

        self.path = entry_docs_path(language, base_path + '.html')

    __repr__ = autorepr(['language', 'path', 'entry_id'])


def available_languages():
    return [path.name for path in PATH.iterdir() if path.is_dir()]


def entry_docs_path(language, entry_path):
    return language_docs_path(language).joinpath(entry_path)


def language_index(language):
    """Get dict of entry names to data for given language"""
    index_file = language_docs_path(language).joinpath('index.json')
    with index_file.open() as f:
        index = json.load(f)

    index_entries = {
        entry['name']: entry for entry in index['entries']
    }
    return index_entries


def sibling_entry_ids(language, path):
    index = language_index(language)

    entry_ids = []
    for entry in index.values():
        docs_entry = DocsEntry(language, entry['path'])
        if docs_entry.path == path and docs_entry.entry_id:
            entry_ids.append(docs_entry.entry_id)

    return entry_ids


def language_docs_path(language):
    return PATH.joinpath(language)
