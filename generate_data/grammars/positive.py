from bid_name_generator import random_bid_combo, random_single_bid
from helper import weighted, obfuscate_word, insert_noise_between_chars, random_case
from world_name_generator import random_world_name

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


def install_positive_spam_grammar(gen):
    # Keep core tokens
    gen.add_rule("WORLD_NAME", random_world_name)
    gen.add_rule("USER_NAME", random_user_name)
    gen.add_rule("BID", random_single_bid)
    gen.add_rule("BID_COMBO", random_bid_combo)

    # Simple spacing tokens
    gen.add_rule("SPACE", [" "])
    gen.add_rule("OPT_SPACE", ["", " "])

    gen.add_rule("MSG", weighted([
        ("/msg {USER_NAME} ", 100),
    ]))

    gen.add_rule("ME", weighted([
        ("/me ", 90),
        ("", 10),
    ]))

    # Reduce noisy separators; bias to =, :, and space
    gen.add_rule("SEPARATOR", weighted([
        ("=", 50),
        ("==", 10),
        (":", 20),
        ("::", 5),
        (" ", 20),
        ("//", 5),
        ("/", 5),
    ]))

    # CTA / caller words (light, optional)
    CALLER_ELEMENTS = weighted([
        ("GO", 30),
        ("PLAY", 25),
        ("JOIN", 20),
        ("NOW", 15),
        ("GAS", 10),
        ("", 10),
    ])

    def generate_caller(rng):
        element = rng.choice(CALLER_ELEMENTS)
        if not element:
            return ""
        # Rare light obfuscation and rare noise insertion
        if rng.random() < 0.12:
            element = obfuscate_word(rng, element, p=0.12)
        if rng.random() < 0.08:
            element = insert_noise_between_chars(rng, element)
        # Occasionally apply casing
        if rng.random() < 0.25:
            element = random_case(rng, element)
        return element

    gen.add_rule("CALLER", generate_caller)

    # CTA token (lightweight alias of CALLER but guaranteed short)
    def generate_cta(rng):
        c = rng.choice(CALLER_ELEMENTS)
        if not c:
            return ""
        # Slightly lower chance of obfuscation for CTA
        if rng.random() < 0.08:
            c = obfuscate_word(rng, c, p=0.1)
        if rng.random() < 0.06:
            c = insert_noise_between_chars(rng, c)
        if rng.random() < 0.2:
            c = random_case(rng, c)
        return c

    gen.add_rule("CTA", generate_cta)

    # Extra words are uncommon
    EXTRA_ELEMENTS = weighted([
        ("", 80),
        ("NOW", 6),
        ("FAST", 4),
        ("OPEN", 4),
        ("FREE", 6),
        ("GAS", 10),
        ("FREE", 6),
    ])

    def generate_extra(rng):
        element = rng.choice(EXTRA_ELEMENTS)
        if not element:
            return ""
        if rng.random() < 0.12:
            element = obfuscate_word(rng, element, p=0.12)
        if rng.random() < 0.08:
            element = insert_noise_between_chars(rng, element)
        if rng.random() < 0.25:
            element = random_case(rng, element)
        return element

    gen.add_rule("EXTRA", generate_extra)

    # Tail punctuation - mostly empty
    gen.add_rule("TAIL", weighted([
        ("", 80),
        ("!", 8),
        ("!!", 6),
        (".", 6),
        ("?", 2),
    ]))

    # Decorations are rare
    gen.add_rule("DECOR_L", weighted([("", 95), ("[", 3), ("(", 2)]))
    gen.add_rule("DECOR_R", weighted([("", 95), ("]", 3), (")", 2)]))

    # Preferred ad words (use sparingly)
    gen.add_rule("AD_WORD", weighted([
        ("CSN", 40),
        ("CASINO", 30),
        ("DL", 10),
        ("BET", 10),
        ("WIN", 10),
    ]))

    # Light obfuscated BID token (rare)
    def bid_light(rng):
        b = random_single_bid(rng)
        if rng.random() < 0.15:
            b = obfuscate_word(rng, b, p=0.15)
        return b

    gen.add_rule("BID_LIGHT", bid_light)

    # Templates biased toward realistic messages (distribution roughly matches requested shares)
    gen.add_rule("SPAM_MESSAGE", weighted([
        ("{ME}{BID}{SEPARATOR}{WORLD_NAME}", 50),           # canonical (50%)
        ("{ME}{BID} {WORLD_NAME}", 20),                    # space-separated / slight variation (20%)
        ("{ME}{BID}{SEPARATOR}{WORLD_NAME}{TAIL}", 15),    # canonical with tail (added mixture)
        ("{ME}{CTA} {BID}{SEPARATOR}{WORLD_NAME}", 10),    # CTA first (10%)
        ("{ME}{BID_LIGHT}{SEPARATOR}{WORLD_NAME}", 15),    # slight obfuscation (15%)
        ("{ME}{BID}/{BID} {WORLD_NAME}", 5),               # rare combo (5%)
        # keep a few reversed forms but rare
        ("{ME}{WORLD_NAME}{SEPARATOR}{BID}", 5),

        ("{MSG}{BID_COMBO}{SEPARATOR}{WORLD_NAME}", 20)
    ]))
