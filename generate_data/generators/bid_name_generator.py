import random
import re

from text_mutator import TextMutator
from helper import weighted
from generate_data.generators.user_name_generator import random_user_name
from generate_data.generators.name_generator import random_name_generator

BASE_BIDS = [
    "BJ", "RM", "QQ", "CSN", "REME", "CASINO",
    "MIN", "GAS", "DL", "WL", "BEJE", "TURK", "BGL",
]

def mutate_bid(rng, base, t=1.0):
    """
    Dynamically generate a BID-like token.
    """
    token = base

    # choose one main mutation style
    roll = rng.randint(1, 100)

    if roll <= 45*t:
        # mostly clean, maybe slight case change
        token = token
    elif roll <= 65*t:
        # dotted/slashed/spaced form
        token = TextMutator.split_with_separators(rng, token)
    elif roll <= 80*t:
        # one inserted noise char
        token = TextMutator.insert_one_noise_char(rng, token)
    elif roll <= 92*t:
        # leetspeak
        token = TextMutator.obfuscate_word(rng, token, p=0.45*t)
    else:
        # spaced out
        token = TextMutator.space_out(rng, token)

    # maybe apply a second *small* mutation
    if rng.random() < 0.25*t:
        token = TextMutator.obfuscate_word(rng, token, p=0.15*t)

    if rng.random() < 0.20*t:
        token = TextMutator.add_suffix(rng, token)

    token = TextMutator.random_case(rng, token)
    return token


def random_single_bid(rng, t=1.0):
    base = rng.choice(BASE_BIDS)
    return mutate_bid(rng, base, t)


def random_bid_combo(rng):
    count = rng.choice([2, 2, 3, 3, 4])
    sep = rng.choice(["/", "//", "///", ".", " ", " - ", " + "])
    parts = [random_single_bid(rng, t=0.4) for _ in range(count)]
    return sep.join(parts)
