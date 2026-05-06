from helper import weighted
from generate_data.generators.name_generator.utils import leetify, mutate_word, random_case
from generate_data.generators.name_generator.utils import random_cvc_chunk
from generate_data.generators.name_generator.utils import random_digits, random_letters, random_alnum, insert_mid_digits, safe_alnum, safe_lower_alnum
from generate_data.generators.name_generator.config import ALNUM, ALPHA
from generate_data.generators.name_generator.config import FAKER
from generate_data.generators.name_generator.sources import SYLLABLES

def random_syllable_word(rng, syllables=SYLLABLES):
    syll_count = weighted(rng, [
        (2, 32),
        (3, 38),
        (4, 20),
        (5, 10),
    ])

    parts = []
    for _ in range(syll_count):
        if rng.random() < 0.78:
            parts.append(rng.choice(syllables))
        else:
            parts.append(random_cvc_chunk(rng, 2, 4))

    word = safe_lower_alnum("".join(parts))

    if len(word) > 12 and rng.random() < 0.6:
        word = word[:rng.randint(5, 12)]

    return word


def random_pronounceable_root(rng):
    mode = weighted(rng, [
        ("syllables", 35),
        ("cvc", 14),
        ("mixed", 18),
        ("fakerish", 14),
        ("mutated", 19),
    ])

    if mode == "syllables":
        return random_syllable_word(rng)

    if mode == "cvc":
        return random_cvc_chunk(rng, 3, 6)

    if mode == "mixed":
        a = random_syllable_word(rng)
        b = random_cvc_chunk(rng, 2, 4)
        return safe_lower_alnum((a + b)[:rng.randint(4, 10)])

    if mode == "fakerish":
        if FAKER is not None:
            try:
                w = safe_lower_alnum(FAKER.word())
                return w[:rng.randint(3, 8)] if w else random_syllable_word(rng)
            except Exception:
                pass
        return random_syllable_word(rng)

    # mutated
    base = rng.choice([
        "hemo", "hemosa", "hesmosa", "teroyam", "worlaf", "xemo",
        "mosa", "nexa", "rivo", "melo", "zora", "luma", "cyra",
    ])
    return safe_lower_alnum(mutate_word(rng, base, max_ops=2))


def random_mutated_root(rng, base_pool):
    base = rng.choice(base_pool)

    if rng.random() < 0.85:
        base = mutate_word(rng, base, max_ops=2)

    if rng.random() < 0.30:
        base = leetify(base)

    base = safe_lower_alnum(base)

    if rng.random() < 0.65:
        base = insert_mid_digits(rng, base)
    else:
        base = base + random_digits(rng, 1, 4)

    return base


def random_compact_blob(rng):
    mode = weighted(rng, [
        ("letters_tail", 35),
        ("letters_digits", 25),
        ("split_digits", 20),
        ("mixed", 20),
    ])

    if mode == "letters_tail":
        return random_letters(rng, 3, 8, alphabet=ALPHA) + random_digits(rng, 1, 4)

    if mode == "letters_digits":
        return random_alnum(rng, 5, 10).lower()

    if mode == "split_digits":
        left = random_letters(rng, 2, 5)
        mid = random_digits(rng, 1, 3)
        right = random_letters(rng, 1, 4)
        return f"{left}{mid}{right}".lower()

    left = random_pronounceable_root(rng)
    if rng.random() < 0.5:
        return insert_mid_digits(rng, left)
    return left + random_digits(rng, 1, 4)


def random_faker_root(rng):
    if FAKER is None:
        return random_pronounceable_root(rng)

    try:
        base = safe_lower_alnum(FAKER.word())
        if not base:
            base = random_pronounceable_root(rng)
        base = base[:rng.randint(3, 8)]
        if rng.random() < 0.6:
            base += random_digits(rng, 1, 4)
        return base
    except Exception:
        return random_pronounceable_root(rng)


def completely_random_world_name(rng):
    length = rng.randint(5, 11)
    return "".join(rng.choice(ALNUM) for _ in range(length))


# ----------------------------------------------------------------------
# Finalization
# ----------------------------------------------------------------------

def finalize_name(rng, name):
    if rng.random() < 0.18:
        name = mutate_word(rng, name, max_ops=1)

    if rng.random() < 0.12:
        name = leetify(name)

    style = rng.randint(1, 100)
    if style <= 40:
        return name.upper()
    if style <= 75:
        return name.lower()
    return random_case(rng, name)


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def random_name(rng):
    """
    Generate a broad set of world-like identifiers.
    """
    roll = rng.randint(1, 100)

    if roll <= 26:
        name = random_mutated_root(rng, [
            "hemosa", "hesmosa", "hemo", "hemsa", "teroyam",
            "tero", "worlaf", "worl", "world", "xemo", "mosa",
        ])

    elif roll <= 45:
        root = random_pronounceable_root(rng)
        if rng.random() < 0.45:
            root = mutate_word(rng, root, max_ops=1)
        name = root + random_digits(rng, 1, 4)

    elif roll <= 60:
        name = random_compact_blob(rng)

    elif roll <= 72:
        name = random_faker_root(rng)

    elif roll <= 84:
        name = random_mutated_root(rng, [
            "hemosa", "hesmosa", "hemo", "hemsa", "teroyam",
            "tero", "worlaf", "worl", "world", "xemo",
            "mosa", "nexa", "rivo", "melo", "zora",
        ])

    elif roll <= 93:
        name = completely_random_world_name(rng)

    else:
        a = random_pronounceable_root(rng)[:rng.randint(2, 5)]
        b = random_pronounceable_root(rng)[:rng.randint(2, 5)]
        name = a + b + random_digits(rng, 1, 3)

    return finalize_name(rng, name)
