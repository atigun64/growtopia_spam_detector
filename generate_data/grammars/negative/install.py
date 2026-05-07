from helper import weighted
from text_mutator import TextMutator
from .common import fake_sentence_safe, contains_strong_casino_term, safe_user_name, safe_world_name
from .scenarios.world_invites import install_world_invites, generate_world_invite
from .scenarios.trade_messages import install_trade_messages, generate_trade_message
from .scenarios.owner_info import install_owner_info, generate_owner_info
from .scenarios.help_social import install_help_social, generate_help_social
from .scenarios.hard_negatives import install_hard_negatives
from .scenarios.casino_discussion_negatives import install_casino_discussion_negatives
from .scenarios.aggressive_intent import install_aggressive_intent
from .scenarios.random_gibberish import install_random_gibberish
from .scenarios.gameplay_negative import install_gameplay_negative


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

def generate_noisy_normal(rng):
    """
    Rare noisy negatives.

    These are useful because real players sometimes type ugly messages.
    Keep this category small in the top-level distribution.
    """
    base = rng.choice(weighted([
        (generate_world_invite, 30),
        (generate_trade_message, 25),
        (generate_owner_info, 20),
        (generate_help_social, 15),
        (fake_sentence_safe, 10),
    ]))(rng)

    # Stronger styling than normal, but still no casino words.
    text = TextMutator.maybe_style_phrase(rng, base, p_word=0.22)
    text = TextMutator.clean_text(text)

    if contains_strong_casino_term(text):
        return fake_sentence_safe(rng)

    return text


def install_negative_spam_grammar(gen):
    """
    Negative casino-ad dataset generator for Growtopia-like messages.

    Goals:
    - Generate NON-casino messages.
    - Use Faker for variety, not only fixed word lists.
    - Include hard negatives that look ad-like/suspicious:
        - go my world WORLD
        - owner is USER
        - dl shop WORLD
        - gas mask 5wl
        - min price 3wl
        - repeated-world-invite style single messages
    - Include rare obfuscation/noise in normal messages.
    - Avoid accidental true casino/csn negatives.
    """

    install_base_rules(gen)
    install_world_invites(gen)
    install_trade_messages(gen)
    install_owner_info(gen)
    install_help_social(gen)
    install_hard_negatives(gen)
    install_casino_discussion_negatives(gen)
    install_aggressive_intent(gen)
    install_random_gibberish(gen)
    install_gameplay_negative(gen)

    gen.add_rule("NOISY_NORMAL", generate_noisy_normal)

    gen.add_rule("NONSPAM_MESSAGE", weighted([
        # Broad general negative chat
        ("{MSG}{FAKE_CHAT}{TAIL}", 15),
        ("{ME}{HELP_SOCIAL}{TAIL}", 15),

        # casino/csn mentioned, but not promotional
        ("{ME}{CASINO_DISCUSSION_NEGATIVE}{TAIL}", 8),
        ("{MSG}{CASINO_DISCUSSION_NEGATIVE}{TAIL}", 2),

        # One world invite should usually be negative.
        ("{ME}{WORLD_INVITE}{TAIL}", 18),
        ("{MSG}{WORLD_INVITE}{TAIL}", 5),

        # Trade/shop with WL/DL/BGL but not casino.
        ("{ME}{TRADE_MESSAGE}{TAIL}", 15),
        ("{MSG}{TRADE_MESSAGE}{TAIL}", 5),

        # Owner/world/admin info.
        ("{ME}{OWNER_INFO}{TAIL}", 10),
        ("{MSG}{OWNER_INFO}{TAIL}", 4),

        # Hard negatives with BASE_BIDS-looking tokens.
        ("{ME}{BASEBID_HARD_NEGATIVE}{TAIL}", 12),
        ("{MSG}{BASEBID_HARD_NEGATIVE}{TAIL}", 4),

        # New: aggressive urgency / repeated commands
        ("{ME}{AGGRESSIVE_INTENT}{TAIL}", 6),
        ("{MSG}{AGGRESSIVE_INTENT}{TAIL}", 2),

        # New: random gibberish / keyboard smash
        ("{ME}{RANDOM_GIBBERISH}{TAIL}", 3),
        ("{MSG}{RANDOM_GIBBERISH}{TAIL}", 1),

        # Rare obfuscated/noisy normal messages.
        ("{ME}{NOISY_NORMAL}{TAIL}", 4),
        ("{MSG}{NOISY_NORMAL}{TAIL}", 2),

        # Normal gameplay / social play
        ("{ME}{GAMEPLAY_NEGATIVE}{TAIL}", 18),
        ("{MSG}{GAMEPLAY_NEGATIVE}{TAIL}", 6),

    ]))