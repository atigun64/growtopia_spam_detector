from text_mutator import TextMutator
from helper import weighted
from .common import fake_word_safe, fake_words_safe, contains_strong_casino_term, FAKER

# ------------------------------------------------------------------
# Dynamic item / price generation
# ------------------------------------------------------------------

# Some GT-ish fixed roots are okay. The variety comes from Faker modifiers,
# random prices, random worlds, random verbs, and multiple templates.
# You do not want 100% Faker items because it creates too much nonsense.
GT_ITEM_ROOTS = [
    "seed",
    "seeds",
    "block",
    "blocks",
    "door",
    "doors",
    "sign",
    "platform",
    "wall",
    "background",
    "wrench",
    "lock",
    "fossil",
    "geiger",
    "crystal",
    "chair",
    "table",
    "display block",
    "vend",
    "vending machine",
    "farmable",
    "pepper",
    "chand",
    "laser grid",
    "surg tool",
    "pack",
    "bait",
    "fish tank",
    "weather machine",
    "song",
    "hair",
    "shirt",
    "pants",
    "wing",
    "cape",
    "mask",
    "gas mask",       # hard negative: GAS but normal
    "grass block",    # hard negative: GAS-ish substring but normal
    "sugar cane",
    "lava",
    "water",
    "dirt",
    "rock",
    "platform",
    "checkpoint",
    "portal",
    "world key",
]

NORMAL_CURRENCIES = [
    "wl",
    "wls",
    "dl",
    "dls",
    "bgl",
    "gems",
    "/wl",
    "per wl",
]

def random_price(rng):
    amount = rng.choice(weighted([
        (str(rng.randint(1, 20)), 55),
        (str(rng.randint(21, 100)), 25),
        (str(rng.randint(101, 999)), 10),
        (str(rng.randint(1, 5)) + "/" + str(rng.randint(1, 20)), 10),
    ]))

    currency = rng.choice(NORMAL_CURRENCIES)

    if rng.random() < 0.25:
        return amount + " " + currency
    return amount + currency

def fake_item_name(rng):
    """
    Semi-dynamic item names.

    Mostly GT-ish, sometimes Faker-extended.
    Avoids repeating only stuff like 'sell weather'.
    """
    root = rng.choice(GT_ITEM_ROOTS)

    mode = rng.choice(weighted([
        ("plain", 45),
        ("color", 18),
        ("fake_prefix", 18),
        ("fake_two_prefix", 8),
        ("condition", 11),
    ]))

    if mode == "plain":
        item = root
    elif mode == "color":
        item = FAKER.color_name().lower() + " " + root
    elif mode == "fake_prefix":
        item = fake_word_safe(rng) + " " + root
    elif mode == "fake_two_prefix":
        item = fake_words_safe(rng, 1, 2) + " " + root
    else:
        item = rng.choice([
            "cheap",
            "rare",
            "clean",
            "fresh",
            "old",
            "new",
            "small",
            "big",
            "full",
            "empty",
            "public",
            "private",
        ]) + " " + root

    item = TextMutator.clean_text(item, 80)

    if contains_strong_casino_term(item):
        return root

    return item
