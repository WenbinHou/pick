#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import signal
import errno


class PickException(Exception):
    pass


def main():
    """
    Usage:
    Python-like list-subscription expression, but 1-based!
        cat ... | pick 1            # pick the first line
        cat ... | pick -1           # pick the last line
        cat ... | pick :            # pick all lines
        cat ... | pick ::           # pick all lines
        cat ... | pick 2:           # pick all lines except the first line
        cat ... | pick :-1          # pick all lines except the last line
        cat ... | pick ::-1         # pick all lines (in reverse order)
        cat ... | pick 3:1:-1       # pick the first 3 lines (in reverse order)
        cat ... | pick ::2          # pick every other line
        ... (and more)

    Dash-split range expression:
        cat ... | pick 1-3          # pick the first 3 lines
        cat ... | pick 5-10         # pick the 5th to 10th lines
        cat ... | pick 10-1         # pick the 10th to 1st lines (in reverse order)

    Comma-split mixed expression:
        cat ... | pick 1,3::,5-7    # pick the 1st, then all except the first two, then the 5th to 7th lines
    """
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        print(main.__doc__)
        return 0 if len(sys.argv) == 2 else 1

    lines = [None]  # type: list[str | None]  # a placeholder for 1-based indexing
    lines += sys.stdin.readlines()

    # A list of line numbers corresponding to `lines`
    line_index_list = list(range(0, len(lines)))  # type: list[int]
    print_lines_index = []  # type: list[int]

    re_dash_range = re.compile("(\\d+)[ \t]*-[ \t]*(\\d+)")
    subscript_part_opt = "(?:(?:[ \t]*-?[ \t]*[0-9]+[ \t]*)?)"
    re_pythonic_subscript = re.compile("(?:%s:){0,2}(%s)" % (subscript_part_opt, subscript_part_opt))

    for part in sys.argv[1].split(","):  # type: str
        part = part.strip()
        if not part:  # ignore empty parts
            continue

        # Check dash-split range expression
        match = re_dash_range.match(part)
        if match and match.group(0) == part:  # `re.fullmatch` is not supported for Python <= 3.3
            start_line, end_line = map(int, match.groups())  # type: int, int
            if not (start_line > 0 and end_line > 0):
                raise PickException("range line numbers must be positive, but got '{}'".format(part))
            if start_line < end_line:
                start_line = min(start_line, len(lines))  # cap start_line to the last line + 1
                end_line = min(end_line, len(lines) - 1)  # cap end_line to the last line
                print_lines_index += list(range(start_line, end_line + 1))
            else:  # start_line >= end_line: reverse order
                start_line = min(start_line, len(lines) - 1)  # cap start_line to the last line
                end_line = min(end_line, len(lines))  # cap end_line to the last line + 1
                print_lines_index += list(range(start_line, end_line - 1, -1))
            continue

        # Otherwise, it's a Python-like list-subscription expression
        # TODO: is there still security issue here (code injection)?
        match = re_pythonic_subscript.match(part)
        if match and match.group(0) == part:  # `re.fullmatch` is not supported for Python <= 3.3
            res = eval("__line_index_list__[{}]".format(part), {"__line_index_list__": line_index_list})
            if isinstance(res, int):
                assert 0 <= res < len(lines), res
                if res != 0:  # skip the placeholder
                    print_lines_index.append(res)
            else:
                assert isinstance(res, list), res
                print_lines_index += [x for x in res if x != 0]  # skip the placeholder
            continue

        raise PickException("Invalid expression '{}'".format(part))

    # OK, print the selected lines
    for idx in print_lines_index:  # type: int
        assert 0 < idx < len(lines), idx
        print(lines[idx], end="", file=sys.stdout)
        sys.stdout.flush()


if __name__ == '__main__':
    try:
        exit(main() or 0)
    except KeyboardInterrupt:
        exit(128 + int(signal.SIGINT))  # don't say anything more
    except PickException as e:
        print("ERROR: {}".format(str(e)), file=sys.stderr)
        sys.stderr.flush()
        exit(1)
    except Exception as e:
        if isinstance(e, IOError) and e.errno == errno.EPIPE:
            exit(1)  # don't say anything more
        else:
            raise
