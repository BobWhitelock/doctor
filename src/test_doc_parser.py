
from doc_parser import parse
from io import StringIO

from formatting import header, strong, code, pre


def test_parsing_headers():
    parse_test(
        '<h1>First</h1><h2>Second</h2><h5>Fifth</h5>',
        [
            header('# First'),
            header('## Second'),
            header('##### Fifth'),
        ]
    )


def test_parsing_paragraph():
    parse_test(
        '<p>Here is a paragraph with some <strong>bold</strong> text</p>'
        '<p>Here is a paragraph with some <code>inline code</code></p>'
        '<p>Another kind of bold text: <em>like this</em></p>',
        [
            'Here is a paragraph with some {} text'.format(strong('bold')),
            'Here is a paragraph with some {}'.format(code('inline code')),
            'Another kind of bold text: {}'.format(strong('like this')),
        ]
    )


def test_parsing_unordered_list():
    parse_test(
        '<ul><li>First</li><li>Second</li></ul>',
        [
            '- First\n- Second'
        ]
    )


def test_parsing_ordered_list():
    parse_test(
        '<ol><li>First</li><li>Second</li></ol>',
        [
            '1. First\n2. Second'
        ]
    )


def test_other_element_parsed_as_text():
    parse_test(
        '<nav>Some element without <strong>special</strong> handling</nav>',
        [
            'Some element without {} handling'.format(strong('special'))
        ]
    )


def test_parsing_pre():
    parse_test(
        '<pre>//Some code: x+y == z</pre>',
        [
            pre('//Some code: x+y == z')
        ]
    )


def test_parsing_empty_elements():
    parse_test(
        '<code></code>'
        '<pre></pre>'
        '<pre>    </pre>'
        '<p>  <strong></strong>  <code></code><p>',
        []
    )

    # `strong` is empty so should not appear, but following text should.
    parse_test(
        '<p>  <strong></strong>  stuff<p>',
        ['stuff']
    )

    parse_test(
        '<h1>Stuff <strong></strong><h1>',
        [header('# Stuff')]
    )


def parse_test(html, expected_parts):
    test_file = StringIO(html)
    parsed_file_parts = parse(test_file)
    assert parsed_file_parts == expected_parts
