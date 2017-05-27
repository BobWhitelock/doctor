
from fuzzywuzzy import process

from docset import PATH
from identification import identify
import docset


def test_basic_identification_1():
    docs_entry = identify('html', 'input')
    assert docs_entry.path == PATH.joinpath('html/element/input.html')
    assert docs_entry.entry_id is None


def test_basic_identification_2():
    docs_entry = identify('javascript', '!=')
    assert docs_entry.path == PATH.joinpath(
        'javascript/operators/comparison_operators.html')
    assert docs_entry.entry_id == 'Inequality'


def test_basic_identification_3():
    docs_entry = identify('http', '404')
    assert docs_entry.path == PATH.joinpath('http/status/404.html')
    assert docs_entry.entry_id is None


def test_basic_identification_4():
    # Many matches for 'Array' for JavaScript, but without further
    # distinguishing information makes sense to have main 'Array' entry as the
    # top match.
    docs_entry = identify('javascript', 'Array')
    assert docs_entry.path == \
        PATH.joinpath('javascript/global_objects/array.html')
    assert docs_entry.entry_id is None


def test_favours_exact_partial_match():
    """Given `method` give `method (attribute)` rather than e.g. `meta`"""
    docs_entry = identify('html', 'method')
    assert docs_entry.path == PATH.joinpath('html/attributes.html')
    assert docs_entry.entry_id == 'method-attribute'


def test_favours_shorter_matches(monkeypatch):
    """When tie between matches, favour shorter rather than first to occur"""
    monkeypatch.setattr(
        process, 'extractBests',
        lambda *args, **kwargs: [
            ('some long thing', 100),
            ('thing', 100)
        ]
    )
    monkeypatch.setattr(
        docset, 'index',
        lambda l: {
            'thing': {
                'path': 'path/for/thing',
                'junk': "anything else can be in here; it doesn't matter",
            }
        }
    )

    docs_entry = identify('any-language', 'thing')

    expected_doc_path = \
        PATH.joinpath('any-language').joinpath('path/for/thing.html')
    assert docs_entry.path == expected_doc_path

    assert docs_entry.entry_id is None


# TODO test that `identify` is deterministic
