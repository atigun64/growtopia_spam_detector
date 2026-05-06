import re
from .config import ALNUM, CONSONANTS, VOWELS, ALPHA
from text_mutator import TextMutator

def weighted_choice(rng, items):
    values = [value for value, _ in items]
    weights = [weight for _, weight in items]
    return rng.choices(values, weights=weights, k=1)[0]


def safe_alnum(text):
    return re.sub(r"[^a-zA-Z0-9]+", "", str(text))

def safe_lower_alnum(text):
    return safe_alnum(text).lower()


def random_case(rng, text):
    if TextMutator is not None and hasattr(TextMutator, "random_case"):
        return TextMutator.random_case(rng, text)

    # fallback
    return "".join(ch.upper() if rng.random() < 0.5 else ch.lower() for ch in text)


def random_digits(rng, min_len=1, max_len=4):
    n = rng.randint(min_len, max_len)
    return "".join(rng.choice("0123456789") for _ in range(n))


def random_letters(rng, min_len=3, max_len=10, alphabet=ALPHA):
    n = rng.randint(min_len, max_len)
    return "".join(rng.choice(alphabet) for _ in range(n))


def random_alnum(rng, min_len=4, max_len=12):
    n = rng.randint(min_len, max_len)
    return "".join(rng.choice(ALNUM) for _ in range(n))


def random_cvc_chunk(rng, min_len=2, max_len=5):
    """
    Pronounceable-ish chunk.
    """
    n = rng.randint(min_len, max_len)
    out = []

    for i in range(n):
        if i % 2 == 0:
            out.append(rng.choice(CONSONANTS))
        else:
            out.append(rng.choice(VOWELS + CONSONANTS[:12]))

    return "".join(out)


def mutate_word(rng, word, max_ops=2):
    """
    Small typo-like mutations:
    - delete
    - swap
    - insert
    - replace
    - duplicate
    """
    chars = list(safe_alnum(word))
    if not chars:
        return ""

    for _ in range(rng.randint(1, max_ops)):
        if not chars:
            break

        op = rng.choice(["delete", "swap", "insert", "replace", "duplicate"])

        if op == "delete" and len(chars) > 2:
            del chars[rng.randrange(len(chars))]

        elif op == "swap" and len(chars) > 3:
            idx = rng.randrange(len(chars) - 1)
            chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]

        elif op == "insert":
            idx = rng.randrange(len(chars) + 1)
            chars.insert(idx, rng.choice(ALNUM))

        elif op == "replace":
            idx = rng.randrange(len(chars))
            chars[idx] = rng.choice(ALNUM)

        elif op == "duplicate" and len(chars) > 2:
            idx = rng.randrange(len(chars))
            chars.insert(idx, chars[idx])

    return "".join(chars)


def leetify(text):
    table = str.maketrans({
        "a": "4",
        "e": "3",
        "i": "1",
        "o": "0",
        "s": "5",
        "t": "7",
    })
    return str(text).translate(table)


def insert_mid_digits(rng, text):
    text = safe_alnum(text)
    if len(text) < 3:
        return text + random_digits(rng, 1, 3)

    pos = rng.randint(1, len(text) - 1)
    return text[:pos] + random_digits(rng, 1, 3) + text[pos:]
