from helper import weighted

from generators.bid_name_generator import random_single_bid, random_bid_combo
from generators.name_generator import random_name_generator
from generators.user_name_generator import random_user_name

from text_mutator import TextMutator


# ------------------------------------------------------------------
# Small generators / token builders
# ------------------------------------------------------------------

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
    w = random_name_generator(rng)
    if rng.random() < 0.18:
        w = TextMutator.random_case(rng, w)
    if rng.random() < 0.06:
        w = TextMutator.obfuscate_word(rng, w, p=0.10)
    return w


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


# ------------------------------------------------------------------
# Install grammar
# ------------------------------------------------------------------

def install_positive_spam_grammar(gen):
    # ------------------------------------------------------------------
    # Core tokens
    # ------------------------------------------------------------------
    gen.add_rule("USER_NAME", random_user_name)
    gen.add_rule("BID", random_single_bid)
    gen.add_rule("BID_COMBO", random_bid_combo)

    # ------------------------------------------------------------------
    # World-like generators
    # ------------------------------------------------------------------
    gen.add_rule("WORLD_NAME", random_name_generator)

    # ------------------------------------------------------------------
    # Styling helpers
    # ------------------------------------------------------------------
    gen.add_rule("BID_LIGHT", style_bid_light)
    gen.add_rule("WORLD_LIKE", style_world)
    gen.add_rule("BID_CLUSTER", bid_cluster)

    gen.add_rule("SPACE", [" "])
    gen.add_rule("OPT_SPACE", ["", " "])

    gen.add_rule("MSG", weighted([
        ("/msg {USER_NAME} ", 100),
    ]))

    gen.add_rule("ME", weighted([
        ("/me ", 92),
        ("", 8),
    ]))

    gen.add_rule("SEPARATOR", weighted([
        ("=", 34),
        ("==", 6),
        (":", 18),
        ("::", 5),
        (" ", 14),
        ("/", 8),
        ("//", 8),
        ("-", 4),
        ("|", 3),
        (" -> ", 2),
    ]))

    gen.add_rule("CONNECTOR", weighted([
        ("", 22),
        (" in ", 14),
        (" at ", 16),
        (" on ", 10),
        (" to ", 8),
        (" for ", 8),
        (" open ", 10),
        (" now ", 6),
        (" join ", 6),
    ]))

    gen.add_rule("TAIL", weighted([
        ("", 68),
        ("!", 10),
        ("!!", 5),
        (".", 5),
        ("?", 4),
        ("??", 2),
        (" pls", 4),
        (" lol", 1),
        (" xD", 1),
    ]))

    gen.add_rule("DECOR_L", weighted([
        ("", 94),
        ("[", 3),
        ("(", 3),
    ]))

    gen.add_rule("DECOR_R", weighted([
        ("", 94),
        ("]", 3),
        (")", 3),
    ]))

    # ------------------------------------------------------------------
    # CTA / ad words
    # ------------------------------------------------------------------
    gen.add_rule("CTA", generate_cta)
    gen.add_rule("CALLER", generate_caller)
    gen.add_rule("AD_WORD", generate_ad_word)

    def generate_extra(rng):
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

    gen.add_rule("EXTRA", generate_extra)

    # ------------------------------------------------------------------
    # Callable composite rules
    # ------------------------------------------------------------------
    gen.add_rule("SPAM_COMPACT", compact_spam_line)
    gen.add_rule("SPAM_SLASH", slash_chain)
    gen.add_rule("SPAM_REPEAT", repeated_bid)

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------
    gen.add_rule("SPAM_MESSAGE", weighted([
        # Canonical forms
        ("{ME}{BID}{SEPARATOR}{WORLD_NAME}", 42),
        ("{ME}{BID} {WORLD_NAME}", 16),
        ("{ME}{BID}{CONNECTOR}{WORLD_NAME}", 12),
        ("{ME}{BID}{SEPARATOR}{WORLD_NAME}{TAIL}", 10),

        # Strong hard positives: token-only / minimal
        ("{ME}{BID}", 14),
        ("{ME}{AD_WORD}", 12),
        ("{ME}{BID_LIGHT}", 14),
        ("{ME}{AD_WORD}{TAIL}", 10),

        # Very important exact-like false negatives
        ("{ME}{BID}{SEPARATOR}{WORLD_LIKE}", 18),
        ("{ME}{AD_WORD}{SEPARATOR}{WORLD_LIKE}", 16),
        ("{ME}{BID_LIGHT}{SEPARATOR}{WORLD_LIKE}", 16),
        ("{ME}{AD_WORD}{SEPARATOR}{WORLD_NAME}", 14),

        # Compact and weird
        ("{ME}{BID}//{WORLD_NAME}", 12),
        ("{ME}{BID}/{WORLD_NAME}", 10),
        ("{ME}{BID}:{WORLD_NAME}", 10),
        ("{ME}{BID}={WORLD_NAME}", 18),
        ("{ME}{AD_WORD}={WORLD_NAME}", 16),
        ("{ME}{BID_LIGHT}//{WORLD_NAME}", 14),

        # Multi-token / cluster spam
        ("{ME}{BID}/{BID} {WORLD_NAME}", 12),
        ("{ME}{BID}//{BID} {WORLD_NAME}", 12),
        ("{ME}{BID_CLUSTER}{SEPARATOR}{WORLD_NAME}", 18),
        ("{ME}{BID_CLUSTER}{SEPARATOR}{WORLD_LIKE}", 14),
        ("{ME}{BID_CLUSTER} {WORLD_NAME}", 10),
        ("{ME}{BID_CLUSTER}", 10),

        # Repetition spam
        ("{ME}{BID} {BID} {WORLD_NAME}", 12),
        ("{ME}{AD_WORD} {AD_WORD} {WORLD_NAME}", 12),
        ("{ME}{BID_LIGHT} {BID_LIGHT} {WORLD_NAME}", 12),
        ("{ME}{BID} {BID}", 10),
        ("{ME}{AD_WORD} {AD_WORD}", 10),
        ("{ME}{BID}{SEPARATOR}{BID}{SEPARATOR}{WORLD_NAME}", 16),
        ("{ME}{BID}{SEPARATOR}{BID}{SEPARATOR}{WORLD_LIKE}", 14),

        # Slash / equals / mixed separator chains
        ("{ME}{BID}/{BID}={WORLD_NAME}", 12),
        ("{ME}{BID}//{BID}={WORLD_LIKE}", 12),
        ("{ME}{BID_LIGHT}//{AD_WORD}={WORLD_NAME}", 14),
        ("{ME}{AD_WORD}//{BID_LIGHT}={WORLD_LIKE}", 14),
        ("{ME}{BID_LIGHT}/{BID_LIGHT} {WORLD_NAME}", 12),
        ("{ME}{AD_WORD}/{AD_WORD} {WORLD_NAME}", 10),
        ("{ME}{BID_LIGHT}|{BID_LIGHT}|{WORLD_NAME}", 8),

        # CTA-driven spam
        ("{ME}{CTA} {BID}{SEPARATOR}{WORLD_NAME}", 14),
        ("{ME}{CTA} {AD_WORD}{SEPARATOR}{WORLD_NAME}", 12),
        ("{ME}{CALLER} {BID}{SEPARATOR}{WORLD_LIKE}", 12),
        ("{ME}{CTA} {WORLD_NAME} {BID}", 10),
        ("{ME}{CALLER} {WORLD_LIKE} {AD_WORD}", 10),

        # /msg variants
        ("{MSG}{BID}{SEPARATOR}{WORLD_NAME}", 14),
        ("{MSG}{BID}{CONNECTOR}{WORLD_NAME}", 12),
        ("{MSG}{AD_WORD}{SEPARATOR}{WORLD_NAME}", 12),
        ("{MSG}{BID_CLUSTER}{SEPARATOR}{WORLD_NAME}", 14),
        ("{MSG}{BID} {WORLD_NAME}", 10),
        ("{MSG}{BID_LIGHT}={WORLD_LIKE}", 16),
        ("{MSG}{AD_WORD}={WORLD_NAME}", 14),

        # /me emphasis spam
        ("{ME}{AD_WORD} {WORLD_NAME}", 14),
        ("{ME}{BID} {WORLD_LIKE}", 12),
        ("{ME}{BID_LIGHT} {WORLD_LIKE}", 12),
        ("{ME}{AD_WORD} {WORLD_LIKE}", 10),
        ("{ME}{BID} {AD_WORD} {WORLD_NAME}", 10),

        # Decorations / style
        ("{DECOR_L}{BID}{DECOR_R}{SEPARATOR}{WORLD_NAME}", 10),
        ("{DECOR_L}{AD_WORD}{DECOR_R}{SEPARATOR}{WORLD_NAME}", 8),
        ("{DECOR_L}{BID_CLUSTER}{DECOR_R}{SEPARATOR}{WORLD_NAME}", 8),

        # Ultra-hard positives matching common false negatives
        ("{ME}{BID_CLUSTER}={WORLD_LIKE}", 18),
        ("{ME}{BID_CLUSTER}//{WORLD_LIKE}", 18),
        ("{ME}{BID_LIGHT}={WORLD_LIKE}", 20),
        ("{ME}{BID_LIGHT}//{WORLD_LIKE}", 20),
        ("{ME}{AD_WORD}//{WORLD_LIKE}", 18),
        ("{ME}{AD_WORD}:{WORLD_LIKE}", 16),
        ("{ME}{BID_LIGHT}:{WORLD_LIKE}", 16),

        # Minimal but spammy
        ("{ME}{BID}{TAIL}", 8),
        ("{ME}{AD_WORD}{TAIL}", 8),
        ("{ME}{BID_LIGHT}{TAIL}", 8),
        ("{ME}{BID_CLUSTER}{TAIL}", 8),

        # Loud repeated format
        ("{ME}{BID} {BID} {BID}", 8),
        ("{ME}{AD_WORD} {AD_WORD} {AD_WORD}", 8),
        ("{ME}{BID_CLUSTER} {BID_LIGHT}", 8),
        ("{ME}{BID_LIGHT} {BID_CLUSTER}", 8),

        # Explicit noisy compact chains
        ("{ME}{BID_CLUSTER}{SEPARATOR}{BID_LIGHT}{SEPARATOR}{WORLD_NAME}", 16),
        ("{ME}{BID_LIGHT}{SEPARATOR}{BID_CLUSTER}{SEPARATOR}{WORLD_LIKE}", 16),
        ("{ME}{BID_LIGHT}{SEPARATOR}{AD_WORD}{SEPARATOR}{WORLD_NAME}", 14),
        ("{ME}{AD_WORD}{SEPARATOR}{BID_LIGHT}{SEPARATOR}{WORLD_NAME}", 14),

        # Strange world-bid ordering
        ("{ME}{WORLD_NAME}{SEPARATOR}{BID}", 12),
        ("{ME}{WORLD_LIKE}{SEPARATOR}{AD_WORD}", 12),
        ("{ME}{WORLD_NAME} {BID}", 8),
        ("{ME}{WORLD_LIKE} {AD_WORD}", 8),

        # Combined callable-based rules
        ("{ME}{SPAM_COMPACT}", 18),
        ("{ME}{SPAM_SLASH}", 14),
        ("{ME}{SPAM_REPEAT}", 12),
    ]))

    # Optional aliases if your generator benefits from them
    gen.add_rule("POSITIVE_SPAM_MESSAGE", "{SPAM_MESSAGE}")
    gen.add_rule("SPAM_PROMO", "{SPAM_MESSAGE}")
    gen.add_rule("SPAM_HARD_POSITIVE", "{SPAM_MESSAGE}")
