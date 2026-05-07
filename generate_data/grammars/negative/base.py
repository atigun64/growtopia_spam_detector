from helper import weighted
from generate_data.generators.name_generator import random_name_generator
from faker import Faker
import re
from text_mutator import TextMutator
from generate_data.generators import random_user_name

FAKER = Faker("en_US")
STRONG_CASINO_CONTAMINATION_TERMS = [
    "casino",
    "c4sino",
    "cas1no",
    "casiino",
    "cazino",
    "csn",
    "c5n",
]

def fake_word_safe(rng):
    for _ in range(20):
        reseed_fake(rng, FAKER)
        w = FAKER.word()
        w = TextMutator.clean_text(w, 30)
        if w and not contains_strong_casino_term(w):
            return w
    return "item"

def reseed_fake(rng, FAKER):
    FAKER.seed_instance(rng.randint(1, 2**32 - 1))

def contains_strong_casino_term(text):
    compact = TextMutator.normalize_for_filter(text)
    return any(term in compact for term in STRONG_CASINO_CONTAMINATION_TERMS)

def safe_world_name(rng):
    for _ in range(30):
        w = random_name_generator(rng)
        if not contains_strong_casino_term(w):
            return w
    return "WORLD" + str(rng.randint(1000, 999999))

def safe_user_name(rng):
    for _ in range(30):
        u = random_user_name(rng)
        if not contains_strong_casino_term(u):
            return u
    return "player" + str(rng.randint(1000, 999999))

def fake_words_safe(rng, min_n=1, max_n=3):
    n = rng.randint(min_n, max_n)
    words = []

    for _ in range(n):
        words.append(fake_word_safe(rng))

    text = " ".join(words)
    return TextMutator.clean_text(text, 60)

def fake_sentence_safe(rng):
    """
    Faker-generated general chat.
    This adds broad linguistic variety.
    """
    for _ in range(20):
        reseed_fake(rng, FAKER)

        style = rng.choice(weighted([
            ("sentence", 45),
            ("question", 20),
            ("short_chat", 20),
            ("catch", 10),
            ("bs", 5),
        ]))

        if style == "sentence":
            text = FAKER.sentence(nb_words=rng.randint(3, 11)).rstrip(".")
        elif style == "question":
            topic = fake_words_safe(rng, 1, 3)
            text = rng.choice([
                f"can someone help with {topic}",
                f"does anyone know {topic}",
                f"where is {topic}",
                f"how much is {topic}",
                f"who owns this world",
                f"is the owner here",
                f"can someone open the door",
                f"why am i stuck",
                f"where is the white door",
            ])
        elif style == "catch":
            text = FAKER.catch_phrase()
        elif style == "bs":
            text = FAKER.bs()
        else:
            text = rng.choice([
                "hi",
                "hello",
                "yo",
                "wait",
                "brb",
                "come here",
                "follow me",
                "nice world",
                "cool farm",
                "thanks",
                "ty",
                "np",
                "lol",
                "lag",
                "relog",
                "where are you",
                "owner here",
            ])

        text = TextMutator.clean_text(text)

        if text and not contains_strong_casino_term(text):
            return TextMutator.maybe_noisy_line(rng, text, line_p=0.06, p_word=0.06)

    return "hello can someone help"

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



def install_base_rules(gen):
    gen.add_rule("WORLD_NAME", safe_world_name)
    gen.add_rule("USER_NAME", safe_user_name)

    gen.add_rule("SPACE", [" "])
    gen.add_rule("OPT_SPACE", ["", " "])

    gen.add_rule("ME", weighted([
        ("/me ", 18),
        ("", 82),
    ]))

    gen.add_rule("MSG", weighted([
        ("/msg {USER_NAME} ", 10),
        ("", 90),
    ]))

    gen.add_rule("TAIL", weighted([
        ("", 62),
        (".", 10),
        ("!", 10),
        ("!!", 4),
        ("?", 8),
        (" :)", 2),
        (" xD", 2),
        (" lol", 2),
    ]))

    gen.add_rule("SEPARATOR", weighted([
        (" ", 45),
        ("=", 10),
        (" = ", 8),
        (":", 10),
        (" : ", 5),
        ("-", 7),
        ("/", 5),
        ("//", 3),
        (" | ", 3),
        (" -> ", 4),
    ]))

    gen.add_rule("FAKE_CHAT", fake_sentence_safe)