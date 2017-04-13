
from click import Choice
import click

import docs
import doc_parser
import identification


@click.command()
@click.argument('language', type=Choice(docs.available_languages()))
@click.argument('search_term')
def doctor(language, search_term):
    doc_path = identification.identify(language, search_term)
    with doc_path.open() as f:
        doc_parts = doc_parser.parse(f)

    click.echo('\n'.join(doc_parts))
