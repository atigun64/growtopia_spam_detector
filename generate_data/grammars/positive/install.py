from helper import weighted

from .common import repeated_bid, slash_chain, style_bid_light, style_world, bid_cluster
from .common import generate_cta, generate_caller, generate_ad_word, compact_spam_line

from generators.bid_name_generator import random_single_bid, random_bid_combo
from generators.name_generator import random_name_generator
from generators.user_name_generator import random_user_name

from text_mutator import TextMutator

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
        # ------------------------------------------------------------------
    # Callable composite rules
    # ------------------------------------------------------------------

    def spam_compact(rng):
        return compact_spam_line(rng)

    def spam_slash(rng):
        return slash_chain(rng)

    def spam_repeat(rng):
        return repeated_bid(rng)

    gen.add_rule("SPAM_COMPACT", spam_compact)
    gen.add_rule("SPAM_SLASH", spam_slash)
    gen.add_rule("SPAM_REPEAT", spam_repeat)

    # Optional aliases if your generator benefits from them
    gen.add_rule("POSITIVE_SPAM_MESSAGE", "{SPAM_MESSAGE}")
    gen.add_rule("SPAM_PROMO", "{SPAM_MESSAGE}")
    gen.add_rule("SPAM_HARD_POSITIVE", "{SPAM_MESSAGE}")
