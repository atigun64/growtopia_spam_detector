import os
import re
import random

from .config import FAKER, PYPHEN_DICT, BASE_SYLLABLES

from .utils import safe_lower_alnum

from wordfreq import top_n_list

def collect_seed_words():
    seeds = set()

    # System dictionaries
    for path in ("/usr/share/dict/words", "/usr/dict/words"):
        if os.path.exists(path):
            try:
                with open(path, encoding="utf8", errors="ignore") as fh:
                    for line in fh:
                        w = line.strip()
                        if w.isalpha() and 3 <= len(w) <= 12:
                            seeds.add(w.lower())
            except Exception:
                pass
            break

    # Faker words
    if FAKER is not None:
        try:
            for _ in range(500):
                w = safe_lower_alnum(FAKER.word())
                if w.isalpha() and 3 <= len(w) <= 12:
                    seeds.add(w)
        except Exception:
            pass

    # wordfreq top words
    if top_n_list is not None:
        try:
            for w in top_n_list("en", 2000):
                w = safe_lower_alnum(w)
                if w.isalpha() and 3 <= len(w) <= 12:
                    seeds.add(w)
        except Exception:
            pass

    # fallback
    if not seeds:
        seeds.update([
            "adventure", "mystic", "dragon", "ember", "crystal", "radiant",
            "shadow", "silver", "golden", "thunder", "storm", "sunrise",
            "moonlight", "forest", "island", "bridge", "portal", "tower",
            "nebula", "cosmic", "echo", "vortex", "atlas", "zenith",
            "falcon", "paradox", "signal", "vector", "horizon", "lattice",
        ])

    return sorted(seeds)


def build_syllable_bank(seed_words=None, max_syllables=1200):
    """
    Build a syllable list from:
    - BASE_SYLLABLES
    - pyphen hyphenation
    - seed words
    """
    syllables = set(BASE_SYLLABLES)

    if PYPHEN_DICT is None:
        return sorted(syllables)

    candidates = list(seed_words if seed_words is not None else collect_seed_words())
    random.shuffle(candidates)

    for word in candidates:
        try:
            hyphenated = PYPHEN_DICT.inserted(str(word))
        except Exception:
            continue

        parts = [p for p in re.split(r"[-\u2011\u2010]", hyphenated) if p]
        for part in parts:
            part = part.lower().strip()
            if 2 <= len(part) <= 5 and part.isalpha():
                syllables.add(part)

        if len(syllables) >= max_syllables:
            break

    return sorted(syllables)


SYLLABLES = build_syllable_bank()
