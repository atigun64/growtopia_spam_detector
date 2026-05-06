import random
from text_mutator import TextMutator
from helper import weighted


BASE_BIDS = [
  "BJ", "RM", "QQ", "CSN", "REME", "CASINO",
  "MIN", "GAS", "DL", "WL", "BEJE", "TURK", "BGL",
]

# Tokens split by how they can safely appear in negative examples.
CURRENCY_BIDS = ["DL", "WL", "BGL"]
NORMAL_MEANING_BIDS = ["RM", "MIN", "GAS", "TURK", "QQ"]
STRONG_CASINO_BIDS = ["CSN", "CASINO", "BJ", "REME", "BEJE"]

def random_base_bid_token(rng):
    return rng.choice(BASE_BIDS)

def random_currency_bid(rng):
    return rng.choice(CURRENCY_BIDS)

def random_normal_meaning_bid(rng):
    return rng.choice(NORMAL_MEANING_BIDS)

def random_strong_casino_bid(rng):
    return rng.choice(STRONG_CASINO_BIDS)

def generate_extra_filler(rng) -> str:
    """
    Generates optional extra filler words (NOW, FAST, OPEN, FREE, GAS, HOT).
    56% chance of empty string, rest distributed among filler words.
    """
    extra = rng.choice(weighted([
        ("", 56),
        ("NOW", 12),
        ("FAST", 8),
        ("OPEN", 8),
        ("FREE", 6),
        ("GAS", 6),
        ("HOT", 4),
    ]))
    if not extra:
        return ""
    if rng.random() < 0.12:
        extra = TextMutator.style_token(rng, extra, obf_p=0.10, noise_p=0.04, case_p=0.30)
    return extra

def generate_cta_word(rng) -> str:
    """
    Generates Call-To-Action words: GO, JOIN, PLAY, NOW, FAST, OPEN, FREE, GAS, BUY, SELL, WIN, BET.
    Sometimes applies style_token (15% chance).
    """
    CTA_WORDS = weighted([
        ("GO", 18),
        ("JOIN", 16),
        ("PLAY", 14),
        ("NOW", 12),
        ("FAST", 8),
        ("OPEN", 8),
        ("FREE", 8),
        ("GAS", 8),
        ("BUY", 4),
        ("SELL", 4),
        ("WIN", 4),
        ("BET", 4),
    ])
    c = rng.choice(CTA_WORDS)
    if rng.random() < 0.15:
        c = TextMutator.style_token(rng, c, obf_p=0.10, noise_p=0.04, case_p=0.35)
    return c

def generate_ad_word(rng) -> str:
    """
    Generates advertising words: CSN, CASINO, QQ, REME, BJ, DL, BGL, BET.
    Sometimes applies style_token (20% chance).
    """
    AD_WORDS = weighted([
        ("CSN", 34),
        ("CASINO", 24),
        ("QQ", 12),
        ("REME", 8),
        ("BJ", 8),
        ("DL", 8),
        ("BGL", 4),
        ("BET", 2),
    ])
    w = rng.choice(AD_WORDS)
    if rng.random() < 0.20:
        w = TextMutator.style_token(rng, w, obf_p=0.14, noise_p=0.05, case_p=0.40)
    return w

def generate_caller_word(rng) -> str:
    """
    Generates caller/emphasis words with individual mutations.
    Applies obfuscate_word, insert_noise_between_chars, and random_case independently.
    """
    CTA_WORDS = weighted([
        ("GO", 18),
        ("JOIN", 16),
        ("PLAY", 14),
        ("NOW", 12),
        ("FAST", 8),
        ("OPEN", 8),
        ("FREE", 8),
        ("GAS", 8),
        ("BUY", 4),
        ("SELL", 4),
        ("WIN", 4),
        ("BET", 4),
    ])
    c = rng.choice(CTA_WORDS)
    if rng.random() < 0.12:
        c = TextMutator.obfuscate_word(rng, c, p=0.12)
    if rng.random() < 0.08:
        c = TextMutator.insert_noise_between_chars(rng, c)
    if rng.random() < 0.22:
        c = TextMutator.random_case(rng, c)
    return c
