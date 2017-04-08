
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
            parsed_element = parse_text(element)

        if parsed_element:
            parsed_elements.append(parsed_element)

    return parsed_elements


def parse_header(element, header_match):
    prefix = HEADER_PREFIX * int(header_match.group(1))
    header_text = prefix + ' ' + element.text_content().strip()
    return header(header_text)


def parse_text(element):
    parsed_element = []

    # Note: original element will be included.
    for child in element.iter():
        text = child.text

        # Handling empty child similar to in main `parse` function.
        empty_child = child.text_content().strip() == ''
        if empty_child:
            pass
        elif child.tag in ['strong', 'em']:
            text = strong(text)
        elif child.tag == 'code':
            text = code(text)

        if text:
            parsed_element.append(text)

        # The text following this element until the next child element.
        tail = child.tail
        if tail:
            parsed_element.append(tail)

    return ''.join(parsed_element).strip()


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
