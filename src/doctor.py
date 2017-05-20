
from click import Choice
import click

import docs
import doc_parser
import identification


@click.command()
@click.argument('language', type=Choice(docs.available_languages()))
@click.argument('search_term')
def doctor(language, search_term):
    docs_entry = identification.identify(language, search_term)
    with docs_entry.path.open() as f:
        parsed_doc = doc_parser.parse(f, docs_entry)

    click.echo(parsed_doc)
