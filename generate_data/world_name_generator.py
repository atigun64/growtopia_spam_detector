from helper import random_case, obfuscate_word
import random
import os
import re


# Base fallback syllables (kept small to ensure functionality without extras)
BASE_SYLLABLES = [
    "son", "dre", "wan", "flow", "lon", "van", "gap", "rud", "hey",
    "sha", "kar", "mir", "tok", "zen", "lok", "ran", "bel", "nor",
    "kam", "tur", "min", "rex", "ven", "dar", "lum", "pas", "zor",
    "fen", "cal", "mon", "gar", "yat", "pon", "ris", "tom", "mal"
]


def _expand_syllables_with_pyphen(seed_words=None, max_syllables=300):
    """Attempt to build a larger syllable list using pyphen hyphenation.

    If pyphen isn't installed or nothing useful is found, return BASE_SYLLABLES.
    """
    try:
        import pyphen
    except Exception:
        return list(BASE_SYLLABLES)

    dic = pyphen.Pyphen(lang='en')

    sylls = set(BASE_SYLLABLES)

    if seed_words is None:
        # Try to use a local wordlist if present; otherwise use a small embedded list
        candidates = []
        # common places for wordlists on Unix-like systems
        for p in ("/usr/share/dict/words", "/usr/dict/words"):
            if os.path.exists(p):
                try:
                    with open(p, encoding='utf8', errors='ignore') as fh:
                        candidates = [w.strip() for w in fh if w.strip()]
                except Exception:
                    candidates = []
                break

        if not candidates:
            # fallback small list
            candidates = [
                'adventure', 'mystic', 'dragon', 'ember', 'crystal', 'radiant', 'shadow',
                'silver', 'golden', 'thunder', 'storm', 'sunrise', 'moonlight', 'oak', 'pine'
            ]
    else:
        candidates = seed_words

    # shuffle to get variety and avoid always taking the same words
    random.shuffle(candidates)

    for w in candidates:
        hy = dic.inserted(w)
        parts = [p for p in re.split('[-\u2011\u2010]', hy) if p]
        for p in parts:
            p = p.lower()
            # keep short-ish syllables (2-5 chars) and avoid non-alpha
            if 2 <= len(p) <= 5 and p.isalpha():
                sylls.add(p)
        if len(sylls) >= max_syllables:
            break

    return sorted(sylls)


# Build the SYLLABLES list at import time (best-effort)
SYLLABLES = _expand_syllables_with_pyphen()


def random_digits(rng, min_len=1, max_len=4):
    length = rng.randint(min_len, max_len)
    return "".join(rng.choice("0123456789") for _ in range(length))

def random_syllable_word(rng):
    syll_count = rng.choice([2, 2, 2, 3])
    return "".join(rng.choice(SYLLABLES) for _ in range(syll_count))

def random_syllable_world(rng):
    base = random_syllable_word(rng)

    if len(base) > 10:
        base = base[:10]

    suffix = random_digits(rng, 1, 4)
    return base + suffix

def random_randomletters_world(rng):
    len_word = rng.randint(3, 10)
    len_suffix = rng.randint(max(1, 4 - len_word), 6)

    word = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(len_word))
    suffix = "".join(rng.choice("0123456789") for _ in range(len_suffix))

    return f"{word}{suffix}"


def completely_random_world_name(rng):
    len_word = rng.randint(6, 9)
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(len_word))


def random_world_name(rng):
    roll = rng.randint(1, 100)

    if roll <= 45:
        name = random_syllable_world(rng)
    elif roll <= 90:
        name = random_randomletters_world(rng)
    else:
        name = completely_random_world_name(rng)

    # Mostly uppercase, because Growtopia worlds are often displayed that way
    style = rng.randint(1, 100)

    if style <= 55:
        return name.upper()
    elif style <= 75:
        return name.lower()
    else:
        return random_case(rng, name)