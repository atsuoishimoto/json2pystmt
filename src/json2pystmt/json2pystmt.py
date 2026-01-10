from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Generator, TypeAlias

__all__ = ["json2pystmt", "build_json_expr_lines", "main"]


def ellipsis(s: str, n: int) -> str:
    """Truncate string s to length n with ellipsis in the middle."""
    slen = len(s)
    if slen <= n + 3:  # ...
        return s

    if n == 0:
        return "..."

    if n == 1:
        return s[0] + "..."

    retlen = min(slen, n)
    nright = retlen // 2
    nleft = retlen - nright
    return s[:nleft] + "..." + s[nright * -1 :]


class _Statement:
    def __init__(self, stmt: str) -> None:
        self.stmt = stmt

    def __repr__(self) -> str:
        return repr(self.stmt)

    def __str__(self) -> str:
        return self.stmt


def _to_str(v: Any, n: int) -> str:
    s = repr(v)
    match v:
        case str():
            s = repr(v)
            if n != -1:
                s = ellipsis(s, n + 2)  # account for quotes
        case int():
            return str(v)
        case _Statement():
            return str(v)
        case _:
            s = repr(v)
            if n != -1:
                s = ellipsis(s, n)
    return s


JsonValue: TypeAlias = dict[str, Any] | list[Any] | str | int
JsonStmt: TypeAlias = tuple[tuple[str | int, ...], Any]


def walk_container(
    parent: tuple[str | int, ...], obj: JsonValue
) -> Generator[JsonStmt, None, None]:
    match obj:
        case dict():
            yield parent, {}
            for k, v in obj.items():
                yield from walk_container(parent + (k,), v)
        case list():
            n = len(obj)
            if n:
                liststr = _Statement(f"[None] * {n}")
            else:
                liststr = _Statement("[]")

            yield parent, liststr
            for n, v in enumerate(obj):
                yield from walk_container(parent + (n,), v)
        case _:
            yield parent, obj


def build_json_expr_lines(
    jsonobj: Any, rootname: str = "root", max_key: int = -1, max_value: int = -1
) -> list[str]:
    if not jsonobj:
        return [f"{rootname} = {jsonobj!r}"]

    lines: list[str] = []
    for path, value in walk_container((), jsonobj):
        spath = tuple(_to_str(p, max_key) for p in path)
        pathstr = "".join(f"[{p}]" for p in spath)
        lines.append(f"{rootname}{pathstr} = {_to_str(value, max_value)}")
    return lines


def json2pystmt(
    jsonobj: Any, rootname: str = "root", max_key: int = -1, max_value: int = -1
) -> list[str]:
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
        help="Maximum key length  (default: -1)",
    )
    parser.add_argument(
        "-m",
        "--max-value-length",
        action="store",
        type=int,
        default=-1,
        dest="max_value",
        help="Maximum key length  (default: -1)",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        type=str,
        default="-",
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

    if args.filename == "-":
        f = sys.stdin
    else:
        f = open(args.filename)

    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)

    lines = json2pystmt(data, args.root, args.max_key, args.max_value)
    if lines:
        for line in lines:
            print(line)
