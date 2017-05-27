
import utils


def test_available_aliases_includes_passed_doc_sets():
    assert utils.available_aliases(
        ['html', 'javascript'], {}
    ) == {
        'html': 'html',
        'javascript': 'javascript',
    }


def test_available_aliases_includes_passed_aliases():
    assert utils.available_aliases(
        ['html', 'javascript'], {'js': 'javascript'}
    ) == {
        'html': 'html',
        'javascript': 'javascript',
        'js': 'javascript',
    }


def test_available_aliases_does_not_include_aliases_for_not_present_doc_sets():
    assert utils.available_aliases(
        ['html', 'javascript'], {'python~3.6': 'python'}
    ) == {
        'html': 'html',
        'javascript': 'javascript',
    }
