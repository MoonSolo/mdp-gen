from random import randint # only used in special occasions, like generating a limited set of 9 char passwords

# Generate all passwords for chosen total chars

spec_list = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" # community.owasp.org/password-special-characters

def print_spec():
    """
    DEBUG function, lists all accepted special characters
    """
    print("DEBUG : printing special characters :")
    for c in spec_list:
        print("char\t\t", c)

# print_spec()

regu_list = "abcdefghijklmnopqrstuvwxyz"
numb_list = "0123456789"

from itertools import product # read line 49

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
        # For each character, build the list of possible outputs at that position.
        # If the char has no swap, only one option: itself.
        options_per_char = []
        for char in self.string:
            if char in swap:
                # keep the original AND all replacements
                options_per_char.append([char] + swap[char])
            else:
                options_per_char.append([char])

        # Cartesian product: one choice per position -> every variant
        variants = ["".join(combo) for combo in product(*options_per_char)]
        return variants

# example of usage : e = equivalents("lol")
#                    print(e.find())
# RETURNS :           ['lol', 'lo1', 'lo!', 'lo7', 'l0l', 'l01', 'l0!', 'l07', 
#                     '1ol', '1o1', '1o!', '1o7', '10l', '101', '10!', '107', 
#                     '!ol', '!o1', '!o!', '!o7', '!0l', '!01', '!0!', '!07', 
#                     '7ol', '7o1', '7o!', '7o7', '70l', '701', '70!', '707']


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
