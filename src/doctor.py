
from click import Choice
import click
import shutil

import docset
import doc_parser
import identification


@click.command()
@click.argument('doc_set', type=Choice(docset.available_identifiers()))
@click.argument('search_term')
def doctor(doc_set, search_term):
    doc_set = docset.from_identifier(doc_set)
    docs_entry = identification.identify(doc_set, search_term)
    with docs_entry.path.open() as f:
        parsed_doc = doc_parser.parse(f, docs_entry)

    echo_maybe_via_pager(parsed_doc)


def echo_maybe_via_pager(text):
    """Output text via pager or without, depending on terminal size."""
    fallback_terminal_size = (80, 20)
    _columns, lines = shutil.get_terminal_size(fallback_terminal_size)

    # Still want to output via pager if text is almost at terminal size, to
    # account for lines for prompt and feels better.
    buffer_lines = 3

    text_lines = len(text.splitlines())

    if lines - buffer_lines < text_lines:
        click.echo_via_pager(text)
    else:
        click.echo(text)
