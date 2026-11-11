#!/usr/bin/env python3
"""
swapper.py — expand each word of a wordlist with its leet-swapped variants.

USAGE :
    python swapper.py <input_file> [--skip N] <output_file>

ARGS :
    input_file    path to the wordlist to read
    --skip N      number of lines to skip at the start (default 0)
    output_file   path to the expanded output file
"""

import argparse
import sys
from itertools import product


spec_list = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
# community.owasp.org/password-special-characters
regu_list = "abcdefghijklmnopqrstuvwxyz"
numb_list = "0123456789"

# map: character -> list of possible replacements
swap: dict = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$"],
    "b": ["5"],
    "l": ["1", "!", "7"],
}

class equivalents:
    def __init__(self, string: str):
        self.string = string

    def find(self) -> list[str]:
        """Return every variant of self.string obtained by swapping
        any subset of swappable characters, using their alternatives."""
        options_per_char = []
        for char in self.string:
            if char in swap:
                options_per_char.append([char] + swap[char])
            else:
                options_per_char.append([char])
        return ["".join(combo) for combo in product(*options_per_char)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Expand each word of a wordlist with its leet-swapped variants."
    )
    parser.add_argument("input", help="path to the input wordlist")
    parser.add_argument("output", help="path to the output file")
    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        metavar="N",
        help="number of lines to skip at the beginning (default: 0)",
    )
    parser.add_argument(
        "--strip-newline",
        action="store_true",
        help="strip trailing \\r as well as \\n",
    )
    parser.add_argument(
        "--dedup",
        action="store_true",
        help="avoid writing the same variant twice",
    )
    args = parser.parse_args()

    if args.skip < 0:
        print(f"ERROR : --skip must be >= 0 (got {args.skip})", file=sys.stderr)
        return 1

    total_in = 0
    total_out = 0
    seen: set[str] = set()

    try:
        with open(args.input, "r", encoding="utf-8") as fin, \
             open(args.output, "w", encoding="utf-8") as fout:

            # skip N lines
            for _ in range(args.skip):
                if fin.readline() == "":
                    print(f"WARN : input has fewer than {args.skip} lines, "
                          f"nothing left to process", file=sys.stderr)
                    return 0

            for line_no, line in enumerate(fin, start=args.skip + 1):
                word = line.rstrip("\n")
                if args.strip_newline:
                    word = word.rstrip("\r\n")

                if not word:
                    continue

                total_in += 1
                try:
                    variants = equivalents(word).find()
                except Exception as e:
                    print(f"WARN : line {line_no} ({word!r}) — {e}",
                          file=sys.stderr)
                    continue

                for v in variants:
                    if args.dedup:
                        if v in seen:
                            continue
                        seen.add(v)
                    fout.write(v + "\n")
                    total_out += 1

    except FileNotFoundError:
        print(f"ERROR : input file not found: {args.input}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR : {e}", file=sys.stderr)
        return 3

    print(f"DEBUG : read {total_in} words, wrote {total_out} variants "
          f"to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())