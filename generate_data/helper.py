import random
import re
import csv


def weighted(items):
    """
    Convert:
        [("a", 3), ("b", 1)]
    into:
        ["a", "a", "a", "b"]
    """
    out = []
    for value, weight in items:
        out.extend([value] * weight)
    return out

def clean_generated_text(text: str) -> str:
    # Collapse excessive whitespace, but keep some weird spacing possible
    text = re.sub(r"[ \t]{3,}", "  ", text)
    return text.strip()


LEET_OUT = {
    "a": ["4", "@", "a"],
    "e": ["3", "e"],
    "i": ["1", "i"],
    "o": ["0", "o"],
    "s": ["$", "5", "s"],
    "t": ["7", "t"],
    "g": ["9", "g"],
    "b": ["8", "b"],
    "l": ["1", "l"],
    "c": ["(", "c"],
}

def random_case(rng, text: str) -> str:
    style = rng.randint(1, 5)

    if style == 1:
        return text.upper()
    if style == 2:
        return text.lower()
    if style == 3:
        return text.title()
    if style == 4:
        return "".join(ch.upper() if rng.random() < 0.5 else ch.lower() for ch in text)

    return text


def obfuscate_word(rng, text: str, p=0.35) -> str:
    out = []

    for ch in text:
        low = ch.lower()

        if low in LEET_OUT and rng.random() < p:
            repl = rng.choice(LEET_OUT[low])
            if ch.isupper():
                repl = repl.upper()
            out.append(repl)
        else:
            out.append(ch)

    return "".join(out)


def space_out(rng, text):
    """
    Examples:
      BJ -> B J
      CSN -> C S N
    """
    if rng.random() >= 0.20:
        return text
    return " ".join(list(text))

def add_suffix(rng, text):
    """
    Append a small suffix sometimes:
      BJ -> BJ1, BJ9, BJ.
      CSN -> CSN9, CSNE, CSN3
    """
    if rng.random() >= 0.18:
        return text

    suffixes = ["1", "2", "3", "4", "5", "8", "9", ".", "!", "E"]
    return text + rng.choice(suffixes)

def insert_one_noise_char(rng, text):
    """
    Insert one noisy separator somewhere.
    """
    if len(text) < 2:
        return text

    noise = rng.choice([".", "/", "-", "'", "_", " ", "//", ":"])
    pos = rng.randint(1, len(text) - 1)
    return text[:pos] + noise + text[pos:]


def split_with_separators(rng, text):
    """
    Examples:
      BJ -> B.J, B/J, B J, B-J, B'J
      CSN -> C.S.N, C/S/N, C S N, C-S-N
    """
    seps = [".", "/", "-", " ", "'", "_", ""]
    sep = rng.choice(seps)
    return sep.join(list(text))

def insert_noise_between_chars(rng, text: str, p=0.35) -> str:
    noises = ["", "", "", ".", "/", "//", "'", "-", "_", " ", "$"]

    out = []
    for i, ch in enumerate(text):
        out.append(ch)
        if i != len(text) - 1 and rng.random() < p:
            out.append(rng.choice(noises))

    return "".join(out)