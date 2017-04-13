
from fuzzywuzzy import process

from docs import PATH
from identification import identify
import docs


def test_basic_identification_1():
    expected_doc_path = PATH.joinpath('html/element/input.html')
    assert identify('html', 'input') == expected_doc_path


def test_basic_identification_2():
    expected_doc_path = \
        PATH.joinpath('javascript/operators/comparison_operators.html')
    assert identify('javascript', '!=') == expected_doc_path


def test_basic_identification_3():
    expected_doc_path = PATH.joinpath('http/status/404.html')
    assert identify('http', '404') == expected_doc_path


def test_basic_identification_4():
    # Many matches for 'Array' for JavaScript, but without further
    # distinguishing information makes sense to have main 'Array' entry as the
    # top match.
    expected_doc_path = PATH.joinpath('javascript/global_objects/array.html')
    assert identify('javascript', 'Array') == expected_doc_path


def test_favours_exact_partial_match():
    """Given `method` give `method (attribute)` rather than e.g. `meta`"""
    expected_doc_path = PATH.joinpath('html/attributes.html')
    assert identify('html', 'method') == expected_doc_path


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
        docs, 'language_index',
        lambda l: {
            'thing': {
                'path': 'path/for/thing',
                'junk': "anything else can be in here; it doesn't matter",
            }
        }
    )

    expected_doc_path = \
        PATH.joinpath('any-language').joinpath('path/for/thing.html')
    assert identify('any-language', 'thing') == expected_doc_path


# TODO test that `identify` is deterministic
