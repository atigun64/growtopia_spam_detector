import random
from text_mutator import TextMutator
from helper import weighted

# ----------------------------------------------------------------------
# Vocab / config
# ----------------------------------------------------------------------

BASE_BIDS = [
    "BJ", "RM", "QQ", "CSN", "REME", "CASINO",
    "MIN", "GAS", "DL", "WL", "BEJE", "TURK", "BGL",
]

CURRENCY_BIDS = ["DL", "WL", "BGL"]
NORMAL_MEANING_BIDS = ["RM", "MIN", "GAS", "TURK", "QQ"]
STRONG_CASINO_BIDS = ["CSN", "CASINO", "BJ", "REME", "BEJE"]

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

FILLER_WORDS = weighted([
    ("", 56),
    ("NOW", 12),
    ("FAST", 8),
    ("OPEN", 8),
    ("FREE", 6),
    ("GAS", 6),
    ("HOT", 4),
])

# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def maybe_style(rng, token, p, obf_p, noise_p, case_p):
    if rng.random() < p:
        return TextMutator.style_token(rng, token, obf_p=obf_p, noise_p=noise_p, case_p=case_p)
    return token

# ----------------------------------------------------------------------
# Generators
# ----------------------------------------------------------------------

def random_base_bid_token(rng):
    return rng.choice(BASE_BIDS)

def random_currency_bid(rng):
    return rng.choice(CURRENCY_BIDS)

def random_normal_meaning_bid(rng):
    return rng.choice(NORMAL_MEANING_BIDS)

def random_strong_casino_bid(rng):
    return rng.choice(STRONG_CASINO_BIDS)

def generate_extra_filler(rng) -> str:
    extra = rng.choice(FILLER_WORDS)
    return maybe_style(rng, extra, p=0.12, obf_p=0.10, noise_p=0.04, case_p=0.30) if extra else ""
