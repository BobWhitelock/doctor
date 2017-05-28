
import os
import sys
import shlex

from click.globals import resolve_color_default
from click._compat import _default_text_stdout, text_type, string_types, \
    isatty, WIN, strip_ansi, get_best_encoding, open_stream


# This file copied and adapted from `click/termui.py` and
# `click/_termui_impl.py` in
# https://github.com/pallets/click/tree/e634d7f78b906294fd21fb8b166fa4a71746b76b,
# as for `doctor server` want to gain access to the underlying
# `subprocess.Popen` instance for the pager so can kill this directly when
# needed, and this is not possible using the existing Click `echo_via_pager`
# function.


def echo_via_pager_non_blocking(text, color=None):
    """This function takes a text and shows it via an environment specific
    pager on stdout.

    .. versionchanged:: 3.0
       Added the `color` flag.

    :param text: the text to page.
    :param color: controls if the pager supports ANSI colors or not.  The
                  default is autodetection.
    """
    color = resolve_color_default(color)
    if not isinstance(text, string_types):
        text = text_type(text)
    return pager(text + '\n', color)


def pager(text, color=None):
    """Decide what method to use for paging through text."""
    stdout = _default_text_stdout()
    if not isatty(sys.stdin) or not isatty(stdout):
        return _nullpager(stdout, text, color)
    pager_cmd = (os.environ.get('PAGER', None) or '').strip()
    if pager_cmd:
        if WIN:
            return _tempfilepager(text, pager_cmd, color)
        return _pipepager(text, pager_cmd, color)
    if os.environ.get('TERM') in ('dumb', 'emacs'):
        return _nullpager(stdout, text, color)
    if WIN or sys.platform.startswith('os2'):
        return _tempfilepager(text, 'more <', color)
    if hasattr(os, 'system') and os.system('(less) 2>/dev/null') == 0:
        return _pipepager(text, 'less', color)

    import tempfile
    fd, filename = tempfile.mkstemp()
    os.close(fd)
    try:
        if hasattr(os, 'system') and os.system('more "%s"' % filename) == 0:
            return _pipepager(text, 'more', color)
        return _nullpager(stdout, text, color)
    finally:
        os.unlink(filename)


def _pipepager(text, cmd, color):
    """Page through text by feeding it to another program.  Invoking a
    pager through this might support colors.
    """
    import subprocess
    env = dict(os.environ)

    # If we're piping to less we might support colors under the
    # condition that
    cmd_detail = cmd.rsplit('/', 1)[-1].split()
    if color is None and cmd_detail[0] == 'less':
        less_flags = os.environ.get('LESS', '') + ' '.join(cmd_detail[1:])
        if not less_flags:
            env['LESS'] = '-R'
            color = True
        elif 'r' in less_flags or 'R' in less_flags:
            color = True

    if not color:
        text = strip_ansi(text)

    c = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, env=env)
    encoding = get_best_encoding(c.stdin)
    try:
        c.stdin.write(text.encode(encoding, 'replace'))
        c.stdin.close()
    except (IOError, KeyboardInterrupt):
        pass

    return c

    # Less doesn't respect ^C, but catches it for its own UI purposes (aborting
    # search or other commands inside less).
    #
    # That means when the user hits ^C, the parent process (click) terminates,
    # but less is still alive, paging the output and messing up the terminal.
    #
    # If the user wants to make the pager exit on ^C, they should set
    # `LESS='-K'`. It's not our decision to make.
    # while True:
    #     try:
    #         c.wait()
    #     except KeyboardInterrupt:
    #         pass
    #     else:
    #         break


def _tempfilepager(text, cmd, color):
    """Page through text by invoking a program on a temporary file."""
    import tempfile
    filename = tempfile.mktemp()
    if not color:
        text = strip_ansi(text)
    encoding = get_best_encoding(sys.stdout)
    with open_stream(filename, 'wb')[0] as f:
        f.write(text.encode(encoding))
    try:
        os.system(cmd + ' "' + filename + '"')
    finally:
        os.unlink(filename)


def _nullpager(stream, text, color):
    """Simply print unformatted text.  This is the ultimate fallback."""
    if not color:
        text = strip_ansi(text)
    stream.write(text)
