import random
import os
import re
import string
from text_mutator import TextMutator
from helper import weighted

try:
    from faker import Faker
except Exception:
    Faker = None

try:
    from wordfreq import top_n_list
except Exception:
    top_n_list = None


# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------

ALPHA = "abcdefghijklmnopqrstuvwxyz"
ALNUM = "abcdefghijklmnopqrstuvwxyz0123456789"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"
VOWELS = "aeiou"

# Generic syllables only; not a tiny world-name list.
BASE_SYLLABLES = [
    "son", "dre", "wan", "flow", "lon", "van", "gap", "rud", "hey",
    "sha", "kar", "mir", "tok", "zen", "lok", "ran", "bel", "nor",
    "kam", "tur", "min", "rex", "ven", "dar", "lum", "pas", "zor",
    "fen", "cal", "mon", "gar", "yat", "pon", "ris", "tom", "mal",
    "he", "mo", "sa", "ter", "yo", "am", "af", "q", "x", "j",
    "neo", "lio", "mar", "sol", "arc", "vox", "val", "nim",
    "haze", "nova", "mira", "luma", "cyra", "kora", "nexa", "orin",
    "tora", "vexa", "daro", "sora", "zali", "riva", "keli", "faro",
    "hemo", "hes", "mosa", "tero", "yam", "melo", "zora", "xemo",
    "rivo", "nexo", "luno", "voro", "seno", "tavi", "lexo", "kimo",
]


def _weighted_choice(rng, items):
    values = [x[0] for x in items]
    weights = [x[1] for x in items]
    return rng.choices(values, weights=weights, k=1)[0]


def _safe_alnum(text):
    return re.sub(r"[^a-zA-Z0-9]+", "", str(text))


def _safe_lower_alnum(text):
    return _safe_alnum(text).lower()


def _trim(text, min_len=4, max_len=12):
    text = _safe_alnum(text)
    if len(text) < min_len:
        text += "x" * (min_len - len(text))
    if len(text) > max_len:
        text = text[:max_len]
    return text


# ----------------------------------------------------------------------
# Word / syllable bank building
# ----------------------------------------------------------------------

def _collect_seed_words():
    seeds = set()

    # system dictionaries
    for p in ("/usr/share/dict/words", "/usr/dict/words"):
        if os.path.exists(p):
            try:
                with open(p, encoding="utf8", errors="ignore") as fh:
                    for w in fh:
                        w = w.strip()
                        if w.isalpha() and 3 <= len(w) <= 12:
                            seeds.add(w.lower())
            except Exception:
                pass
            break

    # Faker words
    if Faker is not None:
        try:
            fake = Faker("en_US")
            for _ in range(500):
                w = fake.word()
                w = _safe_lower_alnum(w)
                if w.isalpha() and 3 <= len(w) <= 12:
                    seeds.add(w)
        except Exception:
            pass

    # wordfreq top words, if available
    if top_n_list is not None:
        try:
            for w in top_n_list("en", 2000):
                w = _safe_lower_alnum(w)
                if w.isalpha() and 3 <= len(w) <= 12:
                    seeds.add(w)
        except Exception:
            pass

    # fallback seeds
    if not seeds:
        seeds.update([
            "adventure", "mystic", "dragon", "ember", "crystal", "radiant",
            "shadow", "silver", "golden", "thunder", "storm", "sunrise",
            "moonlight", "forest", "island", "bridge", "portal", "tower",
            "nebula", "cosmic", "echo", "vortex", "atlas", "zenith",
            "falcon", "paradox", "signal", "vector", "horizon", "lattice",
        ])

    return sorted(seeds)


def _expand_syllables_with_pyphen(seed_words=None, max_syllables=1200):
    """
    Build a syllable bank from:
    - BASE_SYLLABLES
    - pyphen hyphenation
    - dictionary/Faker/wordfreq seed words
    """
    sylls = set(BASE_SYLLABLES)

    try:
        import pyphen
    except Exception:
        return sorted(sylls)

    dic = pyphen.Pyphen(lang="en")

    candidates = seed_words if seed_words is not None else _collect_seed_words()
    random.shuffle(candidates)

    for w in candidates:
        try:
            hy = dic.inserted(str(w))
        except Exception:
            continue

        parts = [p for p in re.split(r"[-\u2011\u2010]", hy) if p]
        for p in parts:
            p = p.lower().strip()
            if 2 <= len(p) <= 5 and p.isalpha():
                sylls.add(p)

        if len(sylls) >= max_syllables:
            break

    return sorted(sylls)


SYLLABLES = _expand_syllables_with_pyphen()


# ----------------------------------------------------------------------
# Base generators
# ----------------------------------------------------------------------

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
    Pronounceable-ish chunk, useful for world-like strings.
    """
    n = rng.randint(min_len, max_len)
    out = []
    for i in range(n):
        if i % 2 == 0:
            out.append(rng.choice(CONSONANTS))
        else:
            out.append(rng.choice(VOWELS + CONSONANTS[:12]))
    return "".join(out)


def _mutate_word(rng, word, max_ops=2):
    """
    Small typo-like mutations:
    - delete
    - swap
    - insert
    - replace
    - duplicate
    """
    s = list(_safe_alnum(word))
    if not s:
        return word

    ops = rng.randint(1, max_ops)
    for _ in range(ops):
        if not s:
            break

        op = rng.choice(["delete", "swap", "insert", "replace", "duplicate"])

        if op == "delete" and len(s) > 2:
            idx = rng.randrange(len(s))
            del s[idx]

        elif op == "swap" and len(s) > 3:
            idx = rng.randrange(len(s) - 1)
            s[idx], s[idx + 1] = s[idx + 1], s[idx]

        elif op == "insert":
            idx = rng.randrange(len(s) + 1)
            s.insert(idx, rng.choice(ALNUM))

        elif op == "replace":
            idx = rng.randrange(len(s))
            s[idx] = rng.choice(ALNUM)

        elif op == "duplicate" and len(s) > 2:
            idx = rng.randrange(len(s))
            s.insert(idx, s[idx])

    return "".join(s)


def _leetify(text):
    table = str.maketrans({
        "a": "4",
        "e": "3",
        "i": "1",
        "o": "0",
        "s": "5",
        "t": "7",
    })
    return str(text).translate(table)


def _insert_mid_digits(rng, text):
    text = _safe_alnum(text)
    if len(text) < 3:
        return text + random_digits(rng, 1, 3)
    pos = rng.randint(1, len(text) - 1)
    return text[:pos] + random_digits(rng, 1, 3) + text[pos:]


# ----------------------------------------------------------------------
# Root families
# ----------------------------------------------------------------------

def random_syllable_word(rng):
    """
    2-5 syllable-ish word.
    """
    syll_count = _weighted_choice(rng, [
        (2, 32),
        (3, 38),
        (4, 20),
        (5, 10),
    ])

    parts = []
    for _ in range(syll_count):
        if rng.random() < 0.78:
            parts.append(rng.choice(SYLLABLES))
        else:
            parts.append(random_cvc_chunk(rng, 2, 4))

    word = "".join(parts)
    word = _safe_lower_alnum(word)

    if len(word) > 12 and rng.random() < 0.6:
        word = word[:rng.randint(5, 12)]

    return word


def random_pronounceable_root(rng):
    """
    Root that looks like a word-ish world name, but not necessarily a real word.
    """
    mode = _weighted_choice(rng, [
        ("syllables", 35),
        ("cvc", 14),
        ("mixed", 18),
        ("fakerish", 14),
        ("mutated", 19),
    ])

    if mode == "syllables":
        root = random_syllable_word(rng)

    elif mode == "cvc":
        root = random_cvc_chunk(rng, 3, 6)

    elif mode == "mixed":
        a = random_syllable_word(rng)
        b = random_cvc_chunk(rng, 2, 4)
        root = (a + b)[:rng.randint(4, 10)]

    elif mode == "fakerish":
        if Faker is not None:
            try:
                fake = Faker("en_US")
                w = fake.word()
                w = _safe_lower_alnum(w)
                root = w[:rng.randint(3, 8)] if w else random_syllable_word(rng)
            except Exception:
                root = random_syllable_word(rng)
        else:
            root = random_syllable_word(rng)

    else:
        base = rng.choice([
            "hemo", "hemosa", "hesmosa", "teroyam", "worlaf", "xemo",
            "mosa", "nexa", "rivo", "melo", "zora", "luma", "cyra",
        ])
        root = _mutate_word(rng, base, max_ops=2)

    return _safe_lower_alnum(root)


def random_typo_root(rng):
    """
    Typo-heavy root family.
    """
    base = rng.choice([
        "hemosa", "hesmosa", "hemo", "hemsa", "teroyam",
        "tero", "worlaf", "worl", "world", "xemo",
        "mosa", "nexa", "rivo", "melo", "zora",
    ])

    if rng.random() < 0.85:
        base = _mutate_word(rng, base, max_ops=2)

    if rng.random() < 0.30:
        base = _leetify(base)

    return _safe_lower_alnum(base)


def random_compact_blob(rng):
    """
    Compact alnum blob. This is important because many world names are not
    clean dictionary-like words.
    """
    mode = _weighted_choice(rng, [
        ("letters_tail", 35),
        ("letters_digits", 25),
        ("split_digits", 20),
        ("mixed", 20),
    ])

    if mode == "letters_tail":
        word = random_letters(rng, 3, 8, alphabet=ALPHA)
        return word + random_digits(rng, 1, 4)

    elif mode == "letters_digits":
        return random_alnum(rng, 5, 10).lower()

    elif mode == "split_digits":
        left = random_letters(rng, 2, 5)
        mid = random_digits(rng, 1, 3)
        right = random_letters(rng, 1, 4)
        return f"{left}{mid}{right}".lower()

    else:
        left = random_pronounceable_root(rng)
        if rng.random() < 0.5:
            return _insert_mid_digits(rng, left)
        return left + random_digits(rng, 1, 4)


def random_faker_root(rng):
    """
    Root influenced by Faker or wordfreq words, then trimmed down.
    """
    if Faker is None:
        return random_pronounceable_root(rng)

    try:
        fake = Faker("en_US")
        base = fake.word()
        base = _safe_lower_alnum(base)
        if not base:
            base = random_pronounceable_root(rng)
        base = base[:rng.randint(3, 8)]
        if rng.random() < 0.6:
            base += random_digits(rng, 1, 4)
        return base
    except Exception:
        return random_pronounceable_root(rng)


def world_family_mutated(rng):
    """
    Family of typo-ish / mutated worlds.
    This is the main anti-overfitting family.
    """
    family = rng.choice([
        "hemosa", "hesmosa", "hemo", "hemsa", "teroyam",
        "tero", "worlaf", "worl", "world", "xemo", "mosa",
    ])

    if rng.random() < 0.8:
        family = _mutate_word(rng, family, max_ops=2)

    if rng.random() < 0.3:
        family = _leetify(family)

    family = _safe_lower_alnum(family)

    mode = rng.choice(["end", "mid", "end", "end", "mid"])
    if mode == "mid" and len(family) >= 4:
        family = _insert_mid_digits(rng, family)
    else:
        family = family + random_digits(rng, 1, 4)

    return family


# ----------------------------------------------------------------------
# Main API
# ----------------------------------------------------------------------

def random_world_name(rng):
    """
    Generate a broad set of world-like identifiers.

    Key points:
    - `WORLD...` is only a small family now.
    - Most names are world-like without the literal WORLD prefix.
    - This is a compositional generator, not a tiny example list.
    """
    roll = rng.randint(1, 100)

    if roll <= 5:
        # small minority: classic world prefix
        name = "WORLD" + random_digits(rng, 1, 4)

    elif roll <= 26:
        # typo / mutated family
        name = world_family_mutated(rng)

    elif roll <= 45:
        # pronounceable root + digits
        root = random_pronounceable_root(rng)
        if rng.random() < 0.45:
            root = _mutate_word(rng, root, max_ops=1)
        name = root + random_digits(rng, 1, 4)

    elif roll <= 60:
        # compact alnum blob
        name = random_compact_blob(rng)

    elif roll <= 72:
        # faker-ish trimmed root
        name = random_faker_root(rng)

    elif roll <= 84:
        # letters/digits with typo flavor
        name = random_typo_root(rng)
        if rng.random() < 0.7:
            name += random_digits(rng, 1, 3)

    elif roll <= 93:
        # fully random but still alnum
        name = completely_random_world_name(rng)

    else:
        # hybrid: two short roots + digits
        a = random_pronounceable_root(rng)[:rng.randint(2, 5)]
        b = random_pronounceable_root(rng)[:rng.randint(2, 5)]
        name = a + b + random_digits(rng, 1, 3)

    # optional extra mutation
    if rng.random() < 0.18:
        name = _mutate_word(rng, name, max_ops=1)

    if rng.random() < 0.12:
        name = _leetify(name)

    style = rng.randint(1, 100)
    if style <= 40:
        return name.upper()
    elif style <= 75:
        return name.lower()
    else:
        return TextMutator.random_case(rng, name)


def completely_random_world_name(rng):
    """
    Pure alnum junk, still world-like.
    """
    length = rng.randint(5, 11)
    return "".join(rng.choice(ALNUM) for _ in range(length))
