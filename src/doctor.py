
from click import Choice
import click
import shutil
from flask import Flask
from http import HTTPStatus

import docset
import doc_parser
import identification
import exceptions


doctor_server = Flask(__name__)


@click.group()
def doctor():
    pass


# TODO: Make this the default command.
@doctor.command()
@click.argument('doc_set', type=Choice(docset.available_identifiers()))
@click.argument('search_term')
def search(doc_set, search_term):
    doc = _perform_search(doc_set, search_term)
    _echo_maybe_via_pager(doc)


@doctor.command()
def server():
    doctor_server.run()


@doctor_server.route('/<doc_set>/<search_term>', methods=['POST'])
def search_route(doc_set, search_term):
    try:
        doc = _perform_search(doc_set, search_term)
        click.echo_via_pager(doc)
        return '', HTTPStatus.NO_CONTENT
    except exceptions.UnknownDocSetException:
        response = 'Unknown doc set: {}'.format(doc_set)
        return response, HTTPStatus.BAD_REQUEST


def _perform_search(doc_set, search_term):
    doc_set = docset.from_identifier(doc_set)
    docs_entry = identification.identify(doc_set, search_term)
    with docs_entry.path.open() as f:
        return doc_parser.parse(f, docs_entry)


def _echo_maybe_via_pager(text):
    """Output text via pager or without, depending on terminal size."""
    fallback_terminal_size = (80, 20)
    _columns, lines = shutil.get_terminal_size(fallback_terminal_size)

    # Still want to output via pager if text is almost at terminal size, to
    # account for lines for prompt and feels better.
    buffer_lines = 4

    text_lines = len(text.splitlines())

    if lines - buffer_lines < text_lines:
        click.echo_via_pager(text)
    else:
        click.echo(text)
