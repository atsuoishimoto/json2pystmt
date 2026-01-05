from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Generator

__all__ = ["json2pystmt", "build_json_expr_lines", "main"]


class _listref:
    def __init__(self, n: int) -> None:
        self.numelems = n

    def __repr__(self) -> str:
        if self.numelems == 0:
            return "[]"
        else:
            return f"[None] * {self.numelems}"


def walk_container(
    parent: tuple[str | int, ...], obj: Any
) -> Generator[tuple[tuple[str | int, ...], Any], None, None]:
    match obj:
        case dict():
            yield parent, {}
            for k, v in obj.items():
                yield from walk_container(parent + (k,), v)
        case list():
            yield parent, _listref(len(obj))
            for n, v in enumerate(obj):
                yield from walk_container(parent + (n,), v)
        case _:
            yield parent, obj


def build_json_expr_lines(jsonobj: Any, rootname: str = "root") -> list[str]:
    if not jsonobj:
        return [f"{rootname} = {jsonobj!r}"]

    lines: list[str] = []
    for path, value in walk_container((), jsonobj):
        pathstr = "".join(f"[{repr(p)}]" for p in path)
        lines.append(f"{rootname}{pathstr} = {value!r}")
    return lines


def json2pystmt(jsonobj: Any, rootname: str = "root") -> list[str]:
    return build_json_expr_lines(jsonobj, rootname)


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

    try:
        data = json.load(args.file)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)

    lines = json2pystmt(data, args.root)
    if lines:
        for line in lines:
            print(line)
