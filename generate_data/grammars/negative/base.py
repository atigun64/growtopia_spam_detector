from helper import weighted, obfuscate_word, insert_noise_between_chars, random_case
from world_name_generator import random_world_name
from faker import Faker
import re

fake = Faker("en_US")

def random_user_name(rng):
    len = rng.choice(weighted([
        (4, 6),
        (5, 7),
        (6, 10),
        (7, 15),
        (8, 20),
        (9, 20),
        (10, 20),
        (11, 15),
        (12, 15),
        (13, 15),
        (14, 10),
        (15, 5),
        (16, 2),
        (17, 1),
    ]))
    return random_case(rng, "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") + rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(len)))


# ------------------------------------------------------------------
# Important:
# These are NOT all positive casino bid tokens.
#
# This filter is only to prevent accidental label contamination from
# random Faker/world/user generation.
#
# Do NOT put all BASE_BIDS here, because many are valid negatives:
# WL/DL/BGL = normal currency
# GAS = gas mask / grass
# MIN = minimum price
# TURK = social/nationality context
# RM = remove
# QQ = random/social noise
# ------------------------------------------------------------------

STRONG_CASINO_CONTAMINATION_TERMS = [
    "casino",
    "c4sino",
    "cas1no",
    "casiino",
    "cazino",
    "csn",
    "c5n",
]

LEET_TABLE = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
})

BASE_BIDS = [
    "BJ", "RM", "QQ", "CSN", "REME", "CASINO",
    "MIN", "GAS", "DL", "WL", "BEJE", "TURK", "BGL",
]

# Tokens split by how they can safely appear in negative examples.
CURRENCY_BIDS = ["DL", "WL", "BGL"]
NORMAL_MEANING_BIDS = ["RM", "MIN", "GAS", "TURK", "QQ"]
STRONG_CASINO_BIDS = ["CSN", "CASINO", "BJ", "REME", "BEJE"]

def style_bid_token(rng, token, obf_p=0.08, noise_p=0.04, case_p=0.25):
    """
    Style a BASE_BIDS token in negative examples.

    Low/moderate noise so model learns:
        token/noise alone != casino ad.
    """
    out = token

    if rng.random() < case_p:
        out = random_case(rng, out)

    if rng.random() < obf_p:
        out = obfuscate_word(rng, out, p=0.12)

    if rng.random() < noise_p:
        out = insert_noise_between_chars(rng, out)

    return out

def random_base_bid_token(rng):
    return rng.choice(BASE_BIDS)

def random_currency_bid(rng):
    return rng.choice(CURRENCY_BIDS)

def random_normal_meaning_bid(rng):
    return rng.choice(NORMAL_MEANING_BIDS)

def random_strong_casino_bid(rng):
    return rng.choice(STRONG_CASINO_BIDS)

def normalize_for_filter(text):
    low = str(text).lower().translate(LEET_TABLE)
    compact = re.sub(r"[^a-z0-9]+", "", low)
    return compact

def contains_strong_casino_term(text):
    compact = normalize_for_filter(text)
    return any(term in compact for term in STRONG_CASINO_CONTAMINATION_TERMS)

def clean_text(text, max_len=140):
    text = str(text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len].strip()

def safe_world_name(rng):
    for _ in range(30):
        w = random_world_name(rng)
        if not contains_strong_casino_term(w):
            return w
    return "WORLD" + str(rng.randint(1000, 999999))

def safe_user_name(rng):
    for _ in range(30):
        u = random_user_name(rng)
        if not contains_strong_casino_term(u):
            return u
    return "player" + str(rng.randint(1000, 999999))

def maybe_style_word(rng, word, obf_p=0.025, noise_p=0.018, case_p=0.12):
    """
    Rare styling for normal messages.

    Keep low. The point is to teach:
        obfuscation can exist in negative messages too.
    Not:
        obfuscation means negative/positive by itself.
    """
    out = str(word)

    if rng.random() < case_p:
        out = random_case(rng, out)

    if rng.random() < obf_p:
        out = obfuscate_word(rng, out, p=0.10)

    if rng.random() < noise_p:
        out = insert_noise_between_chars(rng, out)

    return out

def maybe_style_phrase(rng, text, p_word=0.06):
    parts = str(text).split(" ")
    out = []

    for part in parts:
        if rng.random() < p_word:
            out.append(maybe_style_word(rng, part))
        else:
            out.append(part)

    return " ".join(out)

def maybe_noisy_line(rng, text, line_p=0.075, p_word=0.08):
    """
    Around 7.5% of negative lines get some normal-user weirdness.
    """
    if rng.random() < line_p:
        text = maybe_style_phrase(rng, text, p_word=p_word)
    return clean_text(text)

def reseed_fake(rng):
    fake.seed_instance(rng.randint(1, 2**32 - 1))

def fake_word_safe(rng):
    for _ in range(20):
        reseed_fake(rng)
        w = fake.word()
        w = clean_text(w, 30)
        if w and not contains_strong_casino_term(w):
            return w
    return "item"

def fake_words_safe(rng, min_n=1, max_n=3):
    n = rng.randint(min_n, max_n)
    words = []

    for _ in range(n):
        words.append(fake_word_safe(rng))

    text = " ".join(words)
    return clean_text(text, 60)

def fake_sentence_safe(rng):
    """
    Faker-generated general chat.
    This adds broad linguistic variety.
    """
    for _ in range(20):
        reseed_fake(rng)

        style = rng.choice(weighted([
            ("sentence", 45),
            ("question", 20),
            ("short_chat", 20),
            ("catch", 10),
            ("bs", 5),
        ]))

        if style == "sentence":
            text = fake.sentence(nb_words=rng.randint(3, 11)).rstrip(".")
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
            text = fake.catch_phrase()
        elif style == "bs":
            text = fake.bs()
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

        text = clean_text(text)

        if text and not contains_strong_casino_term(text):
            return maybe_noisy_line(rng, text, line_p=0.06, p_word=0.06)

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
        reseed_fake(rng)
        item = fake.color_name().lower() + " " + root
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

    item = clean_text(item, 80)

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