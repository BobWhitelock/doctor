
import lxml.html as html
import re
import terminaltables

from formatting import header, strong, code, pre


HEADER_REGEX = '^h(\d)$'

HEADER_PREFIX = '#'
UNORDERED_LIST_PREFIX = '-'

LIST_ELEMENTS = ['ul', 'ol']


def parse(html_doc_file, docs_entry):
    parser = html.HTMLParser(encoding='utf-8')
    parsed_doc = html.parse(html_doc_file, parser)

    # If entry specfied with an ID start parsing from that element's parent
    # onwards, otherwise start from the `body`.
    if docs_entry.entry_id:
        doc_root = parsed_doc.getroot()
        entry_element = doc_root.get_element_by_id(docs_entry.entry_id)
        parse_root = \
            entry_element.getparent()
    else:
        parse_root = parsed_doc.find('body')

    parsed_elements = []
    found_element = False
    for element in parse_root.iterchildren():
        element_id = element.get('id')
        if element_id == docs_entry.entry_id:
            found_element = True

        if found_element:
            if docs_entry.is_sibling_id(element_id):
                # Only want to display from specified entry up until next
                # sibling entry, so break once we reach this.
                break

            empty_text = element.text_content().strip() == ''
            if empty_text:
                continue

            parsed_element = _parse_element(element)
            if parsed_element:
                parsed_elements.append(parsed_element)

    return '\n'.join(parsed_elements)


def _parse_element(element):
    if element.tag in LIST_ELEMENTS:
        return _parse_list_element(element)
    elif element.tag == 'table':
        return _parse_table(element)
    elif element.tag == 'pre':
        return _parse_pre(element)
    else:
        return _parse_textual_element(element)


def _parse_textual_element(element):
    parsed_element = []

    header_match = re.fullmatch(HEADER_REGEX, element.tag)
    if header_match:
        header_number = int(header_match.group(1))
        formatter = _create_header_formatter(header_number)
    elif element.tag in ['strong', 'em']:
        formatter = strong
    elif element.tag == 'code':
        formatter = code
    else:
        formatter = lambda x: x  # noqa

    text = element.text if element.text else ''
    parsed_element.append(text)

    for child in element.iterchildren():
        child_content = _parse_element(child)
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


def _create_header_formatter(header_number):
    def formatter(text):
        prefix = HEADER_PREFIX * header_number
        return header(prefix + ' ' + text)

    return formatter


def _parse_list_element(element):
    if element.tag == 'ul':
        prefix = lambda index: UNORDERED_LIST_PREFIX  # noqa
    else:
        prefix = lambda index: str(index + 1) + '.'  # noqa

    parsed_element = []

    for index, child in enumerate(element.iter('li')):
        parsed_element.append(
            prefix(index) + ' ' + _parse_textual_element(child)
        )

    return '\n'.join(parsed_element)


def _parse_pre(element):
    return pre(element.text_content())


def _parse_table(element):
    table_data = []
    for row in element.iter('tr'):
        row_content = _parse_table_row(row)
        table_data.append(row_content)

    table = terminaltables.UnicodeSingleTable(table_data).table
    return table


def _parse_table_row(row_element):
    row_data = []
    for cell in row_element.iter(['td', 'th']):
        cell_content = _parse_table_cell(cell)
        row_data.append(cell_content)
    return row_data


def _parse_table_cell(cell_element):
    cell_content = _parse_textual_element(cell_element)
    if cell_element.tag == 'th':
        cell_content = strong(cell_content)
    return cell_content
