
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


def test_lines_greater_than_terminal_size_for_short_text():
    assert utils.lines_greater_than_terminal_size(
        text='short', columns=10, lines=5
    ) == -4
    assert utils.lines_greater_than_terminal_size(
        text="here's\na\nfew\nvery\nshort\nlines", columns=10, lines=5
    ) == 1


def test_lines_greater_than_terminal_size_for_text_longer_than_columns():
    assert utils.lines_greater_than_terminal_size(
        text='this text should wrap twice', columns=10, lines=5
    ) == -2
