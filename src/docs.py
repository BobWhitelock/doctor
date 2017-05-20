
from pathlib import Path
import json
from autorepr import autorepr
from functools import lru_cache


PATH = Path('/home/bob/repos/devdocs/public/docs')


class DocsEntry:

    def __init__(self, language, path):
        self.language = language

        if '#' in path:
            base_path, self.entry_id = path.split('#')
        else:
            base_path, self.entry_id = path, None

        self.path = self._entry_docs_path(base_path + '.html')

    __repr__ = autorepr(['language', 'path', 'entry_id'])

    def is_sibling_id(self, entry_id):
        """The given entry_id is for another entry in the same document as this

        Will be False if the entry_id is for the same entry as this. Will also
        always be False if this entry has no entry_id, i.e. this is a whole
        document entry.
        """
        not_identical_id = entry_id != self.entry_id
        is_sibling_id = entry_id in self._sibling_entry_ids()
        return not_identical_id and is_sibling_id

    # Cache this as will always give the same result but can be noticeably slow
    # if have to keep recalculating.
    @lru_cache()
    def _sibling_entry_ids(self):
        index = language_index(self.language)

        entry_ids = []
        for entry in index.values():
            docs_entry = DocsEntry(self.language, entry['path'])
            if docs_entry.path == self.path and docs_entry.entry_id:
                entry_ids.append(docs_entry.entry_id)

        return entry_ids

    def _entry_docs_path(self, entry_path):
        return language_docs_path(self.language).joinpath(entry_path)


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
