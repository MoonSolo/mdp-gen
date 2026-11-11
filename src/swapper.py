"""
swapper.py — expand each word of a wordlist with its "leet" equivalents.

USAGE :
    python swapper.py <input_file> [--skip N] <output_file>

ARGS :
    input_file    path to the wordlist to read
    --skip N      number of lines to skip at the start (default 0)
    output_file   path to the expanded output file

Relies on mdpgen.equivalents (see mdpgen.py).
"""

import argparse
import sys

from mdpgen import equivalents


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
        help="strip trailing newline characters explicitly (they usually are by default)",
    )
    args = parser.parse_args()

    if args.skip < 0:
        print(f"ERROR : --skip must be >= 0 (got {args.skip})", file=sys.stderr)
        return 1

    total_in = 0
    total_out = 0

    try:
        with open(args.input, "r", encoding="utf-8") as fin, \
             open(args.output, "w", encoding="utf-8") as fout:

            # skip N lines
            for _ in range(args.skip):
                if fin.readline() == "":
                    # file shorter than skip count — nothing to do
                    print(f"WARN : input has fewer than {args.skip} lines, "
                          f"nothing left to process", file=sys.stderr)
                    return 0

            for line_no, line in enumerate(fin, start=args.skip + 1):
                word = line.rstrip("\n")
                if args.strip_newline:
                    word = word.rstrip("\r\n")

                # skip empty lines silently
                if not word:
                    continue

                total_in += 1
                try:
                    variants = equivalents(word).find()
                except Exception as e:  # don't let one bad word kill the run
                    print(f"WARN : line {line_no} ({word!r}) — {e}",
                          file=sys.stderr)
                    continue

                for v in variants:
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