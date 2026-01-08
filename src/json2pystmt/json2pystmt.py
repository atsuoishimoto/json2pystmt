from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Generator

__all__ = ["json2pystmt", "build_json_expr_lines", "main"]

def ellipsis(s, n):
    slen = len(s)
    if slen <= n+3: # ...
        return s

    if n == 0:
        return "..."

    if n == 1:
        return s[0]+"..."

    retlen = min(slen, n)
    nright = retlen // 2
    nleft = retlen - nright
    return s[:nleft]+"..."+s[nright*-1:]


def walk_container(
    parent: tuple[str | int, ...], obj: Any, max_value: int=-1
) -> Generator[tuple[tuple[str | int, ...], Any], None, None]:
    match obj:
        case dict():
            yield parent, {}
            for k, v in obj.items():
                yield from walk_container(parent + (k,), v, max_value)
        case list():
            n = len(obj)
            if n:
                liststr = f"[None] * {n}"
            else:
                liststr = "[]"

            yield parent, liststr
            for n, v in enumerate(obj):
                yield from walk_container(parent + (n,), v, max_value)
        case str():
            s = repr(obj)
            if max_value != -1:
                s = ellipsis(s, max_value+2)
            yield parent, s
        case _:
            s = repr(obj)
            if max_value != -1:
                s = ellipsis(s, max_value)
            yield parent, s

def build_json_expr_lines(jsonobj: Any, rootname: str = "root", max_key=-1, max_value=-1) -> list[str]:
    if not jsonobj:
        return [f"{rootname} = {jsonobj!r}"]

    lines: list[str] = []
    for path, value in walk_container((), jsonobj, max_value):
        path = [repr(p) for p in path]
        if max_key != -1:
            path = [ellipsis(p, max_key) for p in path]
        pathstr = "".join(f"[{p}]" for p in path)
        lines.append(f"{rootname}{pathstr} = {value}")
    return lines


def json2pystmt(jsonobj: Any, rootname: str = "root", max_key=-1, max_value=-1) -> list[str]:
    return build_json_expr_lines(jsonobj, rootname, max_key, max_value)


def main() -> None:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="json2pystmt",
        description="Convert JSON to executable Python statements",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-k",
        "--max-key-length",
        action="store",
        type=int,
        default=-1,
        dest="max_key",
        help="Maximum key length(>=2)"
    )
    parser.add_argument(
        "-m",
        "--max-value-length",
        action="store",
        type=int,
        default=-1,
        dest="max_value",
        help="Maximum key length(>=2)"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="JSON file to process (default: stdin)",
    )
    parser.add_argument(
        "-r",
        "--root",
        default="root",
        help="Root variable name (default: root)",
    )

    args = parser.parse_args()
    if not args.root:
        sys.exit("Invalid root name")

    if args.max_key < -1:
        sys.exit("Invalid max_key_length")

    if args.max_value < -1:
        sys.exit("Invalid max_value_length")

    try:
        data = json.load(args.file)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)

    lines = json2pystmt(data, args.root, args.max_key, args.max_value)
    if lines:
        for line in lines:
            print(line)
