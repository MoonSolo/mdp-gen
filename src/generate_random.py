from mdpgen import *
from generate_fixed import enumerable_gen

def enumerable_gen_random(minlen: int = 1,
                          maxlen: int = 2,
                          special: bool = True,
                          exclude: list[str] = [],
                          limit: int = 10000,
                          output: str = "output/generated.txt",
                          seed: int | None = None):
    """
    Writes up to `limit` random combinations of characters to a file.
    Character choice per position is randomized; length is chosen uniformly
    in [minlen, maxlen]. Duplicates are avoided.

    ARGS :
        minlen (int) : Minimum length of word (>= 1)
        maxlen (int) : Maximum length of word
        special (bool) : whether to include special characters (default True)
        exclude (list[str]) : characters to exclude from generation
        limit (int) : maximum number of words written
        output : path to file.
        seed (int|None) : optional RNG seed for reproducibility.
    USAGE :
        enumerable_gen_random(4, 6, True, [], 10000, "output/test.txt")
    """
    # sanity checks
    if minlen < 1:
        raise ValueError("minlen must be >= 1")
    if maxlen < minlen:
        raise ValueError("maxlen must be >= minlen")
    if limit < 0:
        raise ValueError("limit must be >= 0")

    # build the alphabet
    alphabet = regu_list + regu_list.upper()
    alphabet += numb_list
    if special:
        alphabet += spec_list

    excluded = set(exclude)
    alphabet = "".join(c for c in alphabet if c not in excluded)
    if not alphabet:
        raise ValueError("alphabet is empty after exclusions")

    # total search space size (to know if limit is even reachable)
    # sum over lengths of |alphabet|^length
    n = len(alphabet)
    space = sum(n ** L for L in range(minlen, maxlen + 1))

    # if limit >= space, better to just enumerate exhaustively (no dup risk)
    if limit >= space:
        print(f"DEBUG : limit >= search space ({space}); "
              f"delegating to exhaustive enumeration")
        # note: previous function, unchanged behavior
        return enumerable_gen(minlen, maxlen, special, exclude, output)

    rng = random.Random(seed)

    # we need `limit` distinct words.
    # Strategy: draw random (length, chars), keep in a set until we hit limit.
    # Rejection can get slow if limit is close to `space`, hence the check 
    # above.
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