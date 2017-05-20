
from doc_parser import parse
from io import StringIO
from unittest import mock
import terminaltables
import re

from formatting import header, strong, code, pre
from docs import DocsEntry


MOCK_DOCS_ENTRY = DocsEntry('javascript', 'javascript/Array')


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
        '<ul>'
        '<li>First</li>'
        '<li>Second</li>'
        '<li><em>Third is bold</em></li>'
        '</ul>',
        [
            '- First\n- Second\n- {}'.format(strong('Third is bold'))
        ]
    )


def test_parsing_ordered_list():
    parse_test(
        '<ol>'
        '<li>First</li>'
        '<li>Second</li>'
        '<li><em>Third is bold</em></li>'
        '</ol>',
        [
            '1. First\n2. Second\n3. {}'.format(strong('Third is bold'))
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


def test_parsing_nested_elements():
    parse_test(
        '<p><code>'
        '<strong>expr1</strong> && <strong>expr2</strong>'
        '</code></p>',
        [code('{} && {}'.format(strong('expr1'), strong('expr2')))]
    )

    parse_test(
        '<h2>   Heading <code> Some code </code></h2>',
        [header('## Heading {}'.format(code('Some code')))]
    )


def test_parsing_table(mocker):
    mocker.spy(terminaltables, 'SingleTable')

    # Wrapper div included to ensure table parsed at any level.
    html = (
        '<div><table>'
        '<tr><th>Header 1</th><th>Header 2</th></tr>'
        '<tr><td>Data 1</td><td>Data 2</td></tr>'
        '<tr><td><code>Some code</code></td><th>Another header</th></tr>'
        '</table></div>'
    )

    expected_table_data = [
        [strong('Header 1'), strong('Header 2')],
        ['Data 1', 'Data 2'],
        [code('Some code'), strong('Another header')],
    ]

    test_file = StringIO(html)
    parse(test_file, MOCK_DOCS_ENTRY)

    # Test table created with correct data (more easily debuggable than
    # `parse_test`).
    assert terminaltables.SingleTable.call_args_list == [
        mock.call(expected_table_data)
    ]

    # Ensure correct table generated.
    expected_terminal_table = terminaltables.SingleTable(
        expected_table_data
    ).table
    parse_test(html, [expected_terminal_table])


def parse_test(html, expected_parts):
    test_file = StringIO(html)
    parsed_file_parts = parse(test_file, MOCK_DOCS_ENTRY)
    assert parsed_file_parts == expected_parts


def test_displaying_nested_match():
    """Test correct section of document given for an entry with an ID"""
    docs_entry = DocsEntry('html', 'attributes#method-attribute')
    with docs_entry.path.open() as f:
        result = parse(f, docs_entry)[0]

    # Strip formatting; just want to test correct text given.
    assert strip_ansi_escape_sequences(result).strip() == (
        'method <form> Defines which HTTP method to use when submitting '
        'the form. Can be GET (default) or POST.'
    )


# From http://stackoverflow.com/a/38662876/2620402.
def strip_ansi_escape_sequences(text):
    ansi_escape_regex = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape_regex.sub('', text)
