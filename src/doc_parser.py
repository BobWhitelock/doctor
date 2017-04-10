
import lxml.html as html
import re

from formatting import header, strong, code, pre


HEADER_REGEX = '^h(\d)$'

HEADER_PREFIX = '#'
UNORDERED_LIST_PREFIX = '-'

LIST_ELEMENTS = ['ul', 'ol']


def parse(html_doc_file):
    parsed_elements = []
    for element in html.parse(html_doc_file).find('body').iterchildren():

        empty_text = element.text_content().strip() == ''
        if empty_text:
            continue

        if element.tag in LIST_ELEMENTS:
            parsed_element = parse_list_element(element)
        elif element.tag == 'pre':
            parsed_element = parse_pre(element)
        else:
            parsed_element = parse_textual_element(element)

        if parsed_element:
            parsed_elements.append(parsed_element)

    return parsed_elements


def parse_textual_element(element):
    parsed_element = []

    header_match = re.fullmatch(HEADER_REGEX, element.tag)
    if header_match:
        header_number = int(header_match.group(1))
        formatter = create_header_formatter(header_number)
    elif element.tag in ['strong', 'em']:
        formatter = strong
    elif element.tag == 'code':
        formatter = code
    else:
        formatter = lambda x: x  # noqa

    text = element.text if element.text else ''
    parsed_element.append(text)

    for child in element.iterchildren():
        child_content = parse_textual_element(child)
        if child_content:
            parsed_element.append(child_content)

    element_content = ''.join(parsed_element).strip()
    if element_content:
        element_content = formatter(element_content)

    # The text following this element until the next sibling or end of parent
    # element.
    tail = element.tail if element.tail else ''
    element_content += tail

    return element_content


def create_header_formatter(header_number):
    def formatter(text):
        prefix = HEADER_PREFIX * header_number
        return header(prefix + ' ' + text)

    return formatter


def parse_list_element(element):
    if element.tag == 'ul':
        prefix = lambda index: UNORDERED_LIST_PREFIX  # noqa
    else:
        prefix = lambda index: str(index + 1) + '.'  # noqa

    parsed_element = []

    for index, child in enumerate(element.iter('li')):
        parsed_element.append(
            prefix(index) + ' ' + parse_textual_element(child)
        )

    return '\n'.join(parsed_element)


def parse_pre(element):
    return pre(element.text_content())
