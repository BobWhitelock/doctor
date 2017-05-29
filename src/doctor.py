
from click import Choice
import click
import shutil
from flask import Flask
from http import HTTPStatus
import logging
import sys

import docset
import doc_parser
import identification
import exceptions
import click_adaptations
import utils


doctor_server = Flask(__name__)
results_pager_process = None


@click.group()
@click.option('--debug/--no-debug', '-d', default=False)
def doctor(debug):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(stream=sys.stderr, level=level)


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
        _display_server_search_result(doc)
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

    # Still want to output via pager if text is almost at terminal size, to
    # account for lines for prompt and feels better.
    buffer_lines = 4

    longer_than_terminal = _lines_greater_than_terminal_size(text)
    if longer_than_terminal + buffer_lines > 0:
        click.echo_via_pager(text)
    else:
        click.echo(text)


def _display_server_search_result(doc):
    global results_pager_process
    if results_pager_process:
        results_pager_process.terminate()
    results_pager_process = click_adaptations.echo_via_pager_non_blocking(doc)


def _lines_greater_than_terminal_size(text):
    terminal = _terminal_size()
    return utils.lines_greater_than_terminal_size(
        text=text,
        columns=terminal.columns,
        lines=terminal.lines
    )


def _terminal_size():
    fallback_terminal_size = (80, 20)
    return shutil.get_terminal_size(fallback_terminal_size)
