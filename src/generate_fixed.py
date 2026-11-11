from mdpgen import *
spec_list = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" 
# community.owasp.org/password-special-characters
regu_list = "abcdefghijklmnopqrstuvwxyz"
numb_list = "0123456789"

def enumerable_gen(minlen:int=1,
                   maxlen:int=2,
                   special:bool=True,
                   exclude:list[str]=[],
                   output:str="output/generated.txt"):
    """
    writes all combinations of characters possible in a file

    ARGS :
        minlen (int) : Minimum length of word (>= 1)
        maxlen (int) : Maximum length of word
        special (bool) : whether to include special characters (default True)
        exclude (list[str]) : characters to exclude from generation
        output : path to file.
    USAGE :
        enumerable_gen(4, 4, True, [], output/test.txt)
    """

    # sanity checks
    if minlen < 1:
        raise ValueError("minlen must be >= 1")
    if maxlen < minlen:
        raise ValueError("maxlen must be >= minlen")

    # build the alphabet
    # letters: lowercase + uppercase (a word can have capitals !)
    alphabet = regu_list + regu_list.upper()
    alphabet += numb_list
    if special:
        alphabet += spec_list  # assumed global

    # remove excluded characters
    excluded = set(exclude)
    alphabet = "".join(c for c in alphabet if c not in excluded)

    if not alphabet:
        raise ValueError("alphabet is empty after exclusions")

    # make sure the output directory exists
    import os
    out_dir = os.path.dirname(output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # stream combinations to file
    total = 0
    with open(output, "w", encoding="utf-8") as f:
        for length in range(minlen, maxlen + 1):
            for combo in product(alphabet, repeat=length):
                f.write("".join(combo) + "\n")
                total += 1

    print(f"DEBUG : wrote {total} words to {output}")
    return total