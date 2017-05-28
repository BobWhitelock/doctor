
import re


def available_aliases(doc_sets, aliases_map):
    """Gives map from available names to doc set they resolves as.

    All doc sets in `doc_sets` will be included mapped to themselves, along
    with any additional mappings to these doc sets from the `aliases_map`.
    """
    available = {doc: doc for doc in doc_sets}
    available.update({
        alias: doc for alias, doc in aliases_map.items()
        if doc in doc_sets
    })
    return available


# From http://stackoverflow.com/a/38662876/2620402.
def strip_ansi_escape_sequences(text):
    ansi_escape_regex = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape_regex.sub('', text)


def lines_greater_than_terminal_size(*, text, columns, lines):
    """Gives the number of lines the text is greater than the terminal size.

    Accounts for both lines and columns (to account for lines which will need
    to be wrapped to show).
    """
    text_lines = text.splitlines()
    lines_wrapped_at_columns = _flatten([
        list(_chunks(line, columns)) for line in text_lines
    ])
    return len(lines_wrapped_at_columns) - lines


# From https://stackoverflow.com/a/312464.
def _chunks(l, n):
    """Yield successive n - sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]
