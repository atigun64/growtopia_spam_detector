from .base import weighted, fake_sentence_safe, maybe_noisy_line
from text_mutator import TextMutator

HELP_TOPICS = [
    "how to farm",
    "how to splice",
    "how to make wl",
    "how to get gems",
    "where is exit",
    "where is white door",
    "where is vend",
    "where is owner",
    "can someone wrench me",
    "can someone pull me",
    "can you open door",
    "can you donate dirt",
    "need help with farm",
    "need help breaking blocks",
    "how much is this item",
    "price check please",
    "what is the price",
    "is this world public",
    "who has access",
    "why am i banned",
    "lagging so hard",
    "relog wait",
    "i need a door",
    "where can i farm",
    "how many wls is this",
    "can i buy this",
    "is vend empty",
]

SOCIAL_BITS = [
    "hi",
    "hello",
    "yo",
    "sup",
    "thanks",
    "ty",
    "np",
    "brb",
    "wait",
    "come",
    "come here",
    "follow me",
    "nice world",
    "cool farm",
    "good shop",
    "where are you",
    "i am back",
    "sorry",
    "lol",
    "lmao",
    "xd",
    "lag",
    "relog",
    "owner?",
    "admin?",
]

def generate_help_social(rng):
    mode = rng.choice(weighted([
        ("fixed_help", 45),
        ("social_combo", 30),
        ("faker_chat", 25),
    ]))

    if mode == "fixed_help":
        text = rng.choice(HELP_TOPICS)
    elif mode == "social_combo":
        n = rng.choice(weighted([
            (1, 55),
            (2, 30),
            (3, 12),
            (4, 3),
        ]))
        text = " ".join(rng.choice(SOCIAL_BITS) for _ in range(n))
    else:
        text = fake_sentence_safe(rng)

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.075, p_word=0.075)

def install_help_social(gen):
    gen.add_rule("HELP_SOCIAL", generate_help_social)