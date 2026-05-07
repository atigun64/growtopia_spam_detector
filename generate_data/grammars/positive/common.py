from generators.bid_name_generator import random_single_bid
from generators.name_generator import random_name_generator
from text_mutator import TextMutator
from helper import weighted

def style_bid(rng):
    """
    Bid variants are a big part of the positive class.
    We want to cover exact and obfuscated variants.
    """
    b = random_single_bid(rng)

    mode = rng.choice(weighted([
        ("plain", 45),
        ("case", 15),
        ("obf", 15),
        ("noise", 10),
        ("comboish", 15),
    ]))

    if mode == "case":
        b = TextMutator.random_case(rng, b)
    elif mode == "obf":
        b = TextMutator.obfuscate_word(rng, b, p=0.18)
    elif mode == "noise":
        b = TextMutator.insert_noise_between_chars(rng, b)
    elif mode == "comboish":
        b = TextMutator.style_token(rng, b, obf_p=0.12, noise_p=0.04, case_p=0.35)

    return b

def style_bid_light(rng):
    b = style_bid(rng)
    if rng.random() < 0.35:
        b = TextMutator.style_token(rng, b, obf_p=0.08, noise_p=0.04, case_p=0.22)
    return b

def style_world(rng):
    w = rng.choice([random_name_generator(rng), random_name_generator(rng)])
    if rng.random() < 0.18:
        w = TextMutator.random_case(rng, w)
    if rng.random() < 0.06:
        w = TextMutator.obfuscate_word(rng, w, p=0.10)
    return w

def bid_cluster(rng):
    """
    Examples:
        QQ/CSN
        C$N//QQ
        REME=DL
        CSN/BJ/QQ
        QQ:CSN
    """
    n = rng.choice(weighted([
        (2, 60),
        (3, 28),
        (4, 12),
    ]))
    parts = [style_bid_light(rng) for _ in range(n)]
    sep = rng.choice(["/", "//", "=", ":", "-", "|", " "])
    return sep.join(parts)


# ------------------------------------------------------------------
# CTA / promo words
# ------------------------------------------------------------------

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

def generate_cta(rng):
    c = rng.choice(CTA_WORDS)
    if rng.random() < 0.15:
        c = TextMutator.style_token(rng, c, obf_p=0.10, noise_p=0.04, case_p=0.35)
    return c

def generate_caller(rng):
    c = rng.choice(CTA_WORDS)
    if rng.random() < 0.12:
        c = TextMutator.obfuscate_word(rng, c, p=0.12)
    if rng.random() < 0.08:
        c = TextMutator.insert_noise_between_chars(rng, c)
    if rng.random() < 0.22:
        c = TextMutator.random_case(rng, c)
    return c

def generate_ad_word(rng):
    w = rng.choice(AD_WORDS)
    if rng.random() < 0.20:
        w = TextMutator.style_token(rng, w, obf_p=0.14, noise_p=0.05, case_p=0.40)
    return w

# ------------------------------------------------------------------
# Useful sub-patterns
# ------------------------------------------------------------------

def repeated_bid(rng):
    b = style_bid(rng)
    n = rng.choice(weighted([
        (2, 45),
        (3, 30),
        (4, 15),
        (5, 10),
    ]))
    sep = rng.choice([" ", "/", "//", "=", ":", "|"])
    return sep.join([b] * n)

def compact_spam_line(rng):
    """
    Compact weird forms:
        C$N//QQ=World5253
        QQ=WORLD52
        CSN//WORLD52
        REME=WORLD52
    """
    left = rng.choice([
        style_bid(rng),
        style_bid_light(rng),
        bid_cluster(rng),
        repeated_bid(rng),
    ])
    right = rng.choice([
        style_world(rng),
        random_name_generator(rng),
        "WORLD" + str(rng.randint(1, 99999)),
    ])
    sep1 = rng.choice(["=", "//", "/", ":", "-", "|"])
    if rng.random() < 0.35:
        mid = style_bid_light(rng)
        sep2 = rng.choice(["=", "/", "//", ":", "-"])
        return f"{left}{sep1}{mid}{sep2}{right}"
    return f"{left}{sep1}{right}"

def slash_chain(rng):
    """
    Extra slash-heavy variants, because many spam lines are dense and compact.
    """
    parts = []
    n = rng.choice(weighted([
        (2, 45),
        (3, 35),
        (4, 20),
    ]))
    for _ in range(n):
        parts.append(rng.choice([
            style_bid_light(rng),
            style_world(rng),
            generate_ad_word(rng),
        ]))
    sep = rng.choice(["/", "//", "///", "=", ":", " | "])
    return sep.join(parts)