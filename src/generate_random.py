#!/usr/bin/env python3
"""
generate_random.py — write up to `limit` random word combinations to a file.

USAGE :
    python generate_random.py <output_file> [--minlen N] [--maxlen N]
                              [--no-special] [--exclude CHARS] [--limit N]
                              [--seed S]

ARGS :
    output_file       path to the output file
    --minlen N        minimum word length (default 1)
    --maxlen N        maximum word length (default 2)
    --no-special      exclude special characters (default: included)
    --exclude CHARS   characters to exclude, as one string (e.g. "lO0")
    --limit N         maximum number of words written (default 10000)
    --seed S          RNG seed for reproducibility (default: random)
"""

import argparse
import os
import random
import sys
from itertools import product

spec_list = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
# community.owasp.org/password-special-characters
regu_list = "abcdefghijklmnopqrstuvwxyz"
numb_list = "0123456789"

def enumerable_gen(minlen: int = 1,
                   maxlen: int = 2,
                   special: bool = True,
                   exclude: list[str] = [],
                   output: str = "output/generated.txt") -> int:
    """Writes all combinations of characters possible in a file."""
    if minlen < 1:
        raise ValueError("minlen must be >= 1")
    if maxlen < minlen:
        raise ValueError("maxlen must be >= minlen")

    alphabet = regu_list + regu_list.upper()
    alphabet += numb_list
    if special:
        alphabet += spec_list

    excluded = set(exclude)
    alphabet = "".join(c for c in alphabet if c not in excluded)
    if not alphabet:
        raise ValueError("alphabet is empty after exclusions")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    total = 0
    with open(output, "w", encoding="utf-8") as f:
        for length in range(minlen, maxlen + 1):
            for combo in product(alphabet, repeat=length):
                f.write("".join(combo) + "\n")
                total += 1

    print(f"DEBUG : wrote {total} words to {output}")
    return total

def enumerable_gen_random(minlen: int = 1,
                          maxlen: int = 2,
                          special: bool = True,
                          exclude: list[str] = [],
                          limit: int = 10000,
                          output: str = "output/generated.txt",
                          seed: int | None = None) -> int:
    """
    Writes up to `limit` random combinations of characters to a file.
    Character choice per position is randomized; length is chosen uniformly
    in [minlen, maxlen]. Duplicates are avoided.
    """
    if minlen < 1:
        raise ValueError("minlen must be >= 1")
    if maxlen < minlen:
        raise ValueError("maxlen must be >= minlen")
    if limit < 0:
        raise ValueError("limit must be >= 0")

    alphabet = regu_list + regu_list.upper()
    alphabet += numb_list
    if special:
        alphabet += spec_list

    excluded = set(exclude)
    alphabet = "".join(c for c in alphabet if c not in excluded)
    if not alphabet:
        raise ValueError("alphabet is empty after exclusions")

    n = len(alphabet)
    space = sum(n ** L for L in range(minlen, maxlen + 1))

    if limit >= space:
        print(f"DEBUG : limit >= search space ({space}); "
              f"delegating to exhaustive enumeration")
        return enumerable_gen(minlen, maxlen, special, exclude, output)

    rng = random.Random(seed)

    seen: set[str] = set()
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        while len(seen) < limit:
            length = rng.randint(minlen, maxlen)
            word = "".join(rng.choice(alphabet) for _ in range(length))
            if word in seen:
                continue
            seen.add(word)
            f.write(word + "\n")

    print(f"DEBUG : wrote {len(seen)} random words to {output}")
    return len(seen)

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write random (or exhaustive, if the space is small) "
                    "combinations of characters to a file."
    )
    parser.add_argument("output", help="path to the output file")
    parser.add_argument("--minlen", type=int, default=1,
                        help="minimum word length (default 1)")
    parser.add_argument("--maxlen", type=int, default=2,
                        help="maximum word length (default 2)")
    parser.add_argument("--no-special", action="store_true",
                        help="exclude special characters")
    parser.add_argument("--exclude", default="", metavar="CHARS",
                        help="characters to exclude, as one string")
    parser.add_argument("--limit", type=int, default=10000,
                        help="max number of words (default 10000)")
    parser.add_argument("--seed", type=int, default=None,
                        help="RNG seed for reproducibility")
    args = parser.parse_args()

    try:
        count = enumerable_gen_random(
            minlen=args.minlen,
            maxlen=args.maxlen,
            special=not args.no_special,
            exclude=list(args.exclude),
            limit=args.limit,
            output=args.output,
            seed=args.seed,
        )
    except ValueError as e:
        print(f"ERROR : {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"ERROR : {e}", file=sys.stderr)
        return 2

    return 0 if count is not None else 1


if __name__ == "__main__":
    sys.exit(main())