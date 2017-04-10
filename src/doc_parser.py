
import lxml.html as html
import re

from formatting import header, strong, code, pre


HEADER_REGEX = '^h(\d)$'

HEADER_PREFIX = '#'
UNORDERED_LIST_PREFIX = '-'


def parse(html_doc_file):
    parsed_elements = []
    for element in html.parse(html_doc_file).find('body').iterchildren():
        header_match = re.fullmatch(HEADER_REGEX, element.tag)

        empty_text = element.text_content().strip() == ''
        if empty_text:
            continue

        if header_match:
            parsed_element = parse_header(element, header_match)
        elif element.tag == 'ul':
            parsed_element = parse_unordered_list(element)
        elif element.tag == 'ol':
            parsed_element = parse_ordered_list(element)
        elif element.tag == 'pre':
            parsed_element = parse_pre(element)
        else:
            parsed_element = parse_textual_element(element)

        if parsed_element:
            parsed_elements.append(parsed_element)

    return parsed_elements


def parse_header(element, header_match):
    prefix = HEADER_PREFIX * int(header_match.group(1))
    header_text = prefix + ' ' + element.text_content().strip()
    return header(header_text)


def parse_textual_element(element):
    parsed_element = []

    if element.tag in ['strong', 'em']:
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


def parse_unordered_list(element):
    parsed_element = []

    for child in element.iter('li'):
        parsed_element.append(
            UNORDERED_LIST_PREFIX + ' ' + child.text_content().strip())

    return '\n'.join(parsed_element)


def parse_ordered_list(element):
    parsed_element = []

    for index, child in enumerate(element.iter('li')):
        item_number = str(index + 1)
        parsed_element.append(
            item_number + '. ' + child.text_content().strip())

    return '\n'.join(parsed_element)


def parse_pre(element):
    return pre(element.text_content())
