
from click import style


def header(text):
    return style(text, bold=True, fg='yellow')


def strong(text):
    return style(text, bold=True)


def code(text):
    return style(text, underline=True)


def pre(text):
    styled_text = style(text, dim=True)
    return '```\n{}\n```'.format(styled_text)
