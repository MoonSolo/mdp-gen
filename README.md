# mdpgen — password wordlist toolkit

A small toolkit to **generate** wordlists and **expand** them with common
"leet-speak" substitutions. Three standalone scripts, no external dependencies.

```
generate_fixed.py    exhaustive enumeration of all character combinations
generate_random.py   random (bounded, deduplicated) sampling of combinations
swapper.py           expand each word with @/4/3/1/0/$/5/! variants
```

---

## Requirements

- Python **3.10+** (uses `list[str]`, `int | None` type hints, `dict` ordering).
- No third-party packages. Everything is stdlib (`argparse`, `itertools`,
  `random`, `os`, `sys`).

Just clone the three `.py` files next to each other and you're set.

---

## 1. `generate_fixed.py` — exhaustive enumeration

Generates **every** possible combination of characters within a length range.

### Usage

```bash
python generate_fixed.py <output_file> \
    [--minlen N] [--maxlen N] \
    [--no-special] [--exclude CHARS]
```

### Arguments

| Flag | Default | Description |
|---|---|---|
| `output` (positional) | — | Path to the output file. Parent dirs are created. |
| `--minlen N` | `1` | Minimum word length (≥ 1). |
| `--maxlen N` | `2` | Maximum word length (≥ `minlen`). |
| `--no-special` | off | Exclude special characters. |
| `--exclude CHARS` | `""` | Characters to remove, given as a single string (e.g. `"lO0"`). |

### Examples

```bash
# Every 4-character word, letters + digits + specials
python generate_fixed.py out/pw4.txt --minlen 4 --maxlen 4

# 1–3 chars, no specials, ambiguous characters removed
python generate_fixed.py out/pw123.txt --minlen 1 --maxlen 3 \
    --no-special --exclude "lO0"

# Digits only, 6 chars (62^6 ≈ 56 billion — think twice!)
python generate_fixed.py out/digits6.txt --minlen 6 --maxlen 6 \
    --no-special --exclude "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
```

### ⚠️ Size warning

Growth is exponential: `|alphabet|^length`.

| Length | Alphabet size | Lines |
|---|---|---|
| 4 | 26+26+10+32 = 94 | ~78 million |
| 6 | 94 | ~690 billion |
| 8 | 94 | ~6 × 10¹⁵ |

Use `generate_random.py` for anything beyond length 4–5, or use `--exclude`
to shrink the alphabet.

---

## 2. `generate_random.py` — bounded random sampling

Writes **up to `limit`** random words. Character choice per position is
random; length is picked uniformly in `[minlen, maxlen]`. Duplicates are
avoided via a set, so you always get exactly `limit` distinct words
(unless the search space is smaller — see fallback below).

### Usage

```bash
python generate_random.py <output_file> \
    [--minlen N] [--maxlen N] \
    [--no-special] [--exclude CHARS] \
    [--limit N] [--seed S]
```

### Arguments

| Flag | Default | Description |
|---|---|---|
| `output` (positional) | — | Path to the output file. Parent dirs are created. |
| `--minlen N` | `1` | Minimum word length (≥ 1). |
| `--maxlen N` | `2` | Maximum word length (≥ `minlen`). |
| `--no-special` | off | Exclude special characters. |
| `--exclude CHARS` | `""` | Characters to remove. |
| `--limit N` | `10000` | Maximum number of distinct words written. |
| `--seed S` | `None` | RNG seed — set it for reproducible runs. |

### Automatic fallback

If `limit ≥ |search space|`, the script **delegates to exhaustive
enumeration** (`generate_fixed.py` logic) — because rejection sampling
can't reach more distinct words than exist, and would loop forever
otherwise.

```bash
python generate_random.py out.txt --minlen 1 --maxlen 2 --limit 999999
# -> "DEBUG : limit >= search space (3906); delegating to exhaustive enumeration"
```

### Examples

```bash
# 10 000 random words, lengths 4–6, letters+digits+specials
python generate_random.py out/rand.txt --minlen 4 --maxlen 6 --limit 10000

# 500 reproducible 8-char passwords
python generate_random.py out/pw8.txt --minlen 8 --maxlen 8 \
    --limit 500 --seed 42

# 2 000 short words, no specials, ambiguous chars excluded
python generate_random.py out/short.txt --minlen 1 --maxlen 3 \
    --no-special --exclude "lO0" --limit 2000
```

### Note on length distribution

Length is drawn **uniformly** in `[minlen, maxlen]` — short words are
over-represented relative to the true search space (which contains vastly
more long words). This is intentional: it produces lists that "look"
natural for password testing. If you want *mathematically uniform*
sampling over the whole space, weight lengths by `|alphabet|^L`:

```python
lengths = list(range(minlen, maxlen + 1))
weights = [n ** L for L in lengths]
length = rng.choices(lengths, weights=weights)[0]
```

---

## 3. `swapper.py` — leet-speak expansion

Reads a wordlist, and for each word writes **every variant** obtainable by
replacing swappable characters with common look-alikes.

### Swap table

| Char | Replacements |
|---|---|
| `a` | `@`, `4` |
| `e` | `3` |
| `i` | `1`, `!` |
| `o` | `0` |
| `s` | `$` |
| `b` | `5` |
| `l` | `1`, `!`, `7` |

Each swappable letter contributes `1 + len(replacements)` options per
position, and variants are the **Cartesian product** across positions.
So `"lol"` produces `4 × 2 × 4 = 32` variants.

### Usage

```bash
python swapper.py <input_file> <output_file> \
    [--skip N] [--dedup] [--strip-newline]
```

### Arguments

| Flag | Default | Description |
|---|---|---|
| `input` (positional) | — | Input wordlist, one word per line. |
| `output` (positional) | — | Output file, one variant per line. |
| `--skip N` | `0` | Skip the first `N` lines (e.g. headers). |
| `--dedup` | off | Don't write the same variant twice across the whole file. |
| `--strip-newline` | off | Also strip `\r` (Windows-formatted input). |

### Examples

```bash
# Expand every word in wordlist.txt
python swapper.py wordlist.txt out/expanded.txt

# Skip a 3-line header, deduplicate
python swapper.py wordlist.txt out/expanded.txt --skip 3 --dedup

# Full pipeline: generate then swap
python generate_random.py out/rand.txt --minlen 4 --maxlen 5 --limit 1000
python swapper.py out/rand.txt out/rand_swapped.txt
```

### Programmatic use

```python
from swapper import equivalents

print(equivalents("lol").find())
# ['lol', 'lo1', 'lo!', 'lo7', '1ol', '1o1', '1o!', '1o7', ...]  # 32 variants
```

### Caveat: spaces in `spec_list`

`spec_list` begins with a space. Words generated with specials enabled may
contain spaces at the start/end. `swapper.py` will preserve them (it only
strips `\n`). If you don't want that, either use `--no-special` when
generating, or edit the constant at the top of the scripts:

```python
spec_list = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"   # no leading space
```

---

## Typical workflows

### A. Exhaustive short list + leet expansion

```bash
# All 3-character words (94^3 ≈ 830k lines, ~7 MB)
python generate_fixed.py out/short.txt --minlen 3 --maxlen 3

# Expand with leet substitutions
python swapper.py out/short.txt out/short_leet.txt --dedup
```

### B. Random long passwords

```bash
# 10k random 8-char passwords, reproducible
python generate_random.py out/pw8.txt --minlen 8 --maxlen 8 \
    --limit 10000 --seed 2024

# Add leet variants on top
python swapper.py out/pw8.txt out/pw8_leet.txt --dedup
```

### C. Targeted list (no ambiguous chars, no specials)

```bash
python generate_fixed.py out/clean.txt --minlen 4 --maxlen 5 \
    --no-special --exclude "lIO0o1"
```

---

## Exit codes

All three scripts return:

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Bad argument (e.g. `minlen < 1`, empty alphabet) |
| `2` | Input file not found (`swapper.py`, `generate_random.py` fallback) |
| `3` | Generic `OSError` (disk full, permission denied, …) |

Errors and warnings go to `stderr`; progress/debug lines go to `stdout`.

---

## File structure

```
.
├── src/
|   ├── generate_fixed.py
|   ├── generate_random.py
|   ├── swapper.py
|   └── mdpgen.py
├── README.md
└── output/            # created automatically on demand
```

Each script is self-contained: constants (`spec_list`, `regu_list`,
`numb_list`) and the `swap` table are inlined at the top of each file. If
you later want a single source of truth, factor them into a
`constants.py` and import from there.