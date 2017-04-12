
from click import Choice
import click

from constants import DOC_PATH
import doc_parser
import identification


def available_languages():
    return [path.name for path in DOC_PATH.iterdir() if path.is_dir()]


@click.command()
@click.argument('language', type=Choice(available_languages()))
@click.argument('search_term')
def doctor(language, search_term):
    doc_path = identification.identify(language, search_term)
    with doc_path.open() as f:
        doc_parts = doc_parser.parse(f)

    click.echo('\n'.join(doc_parts))
