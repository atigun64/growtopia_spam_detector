from .base import safe_world_name, maybe_noisy_line
from text_mutator import TextMutator

INVITE_VERBS = [
    "go",
    "come",
    "join",
    "visit",
    "check",
    "see",
    "rate",
    "enter",
    "look at",
    "try",
    "follow to",
]

INVITE_TARGETS = [
    "my world",
    "our world",
    "this world",
    "the world",
    "my farm",
    "my shop",
    "my vend",
    "my storage",
    "the farm",
    "the shop",
    "my parkour",
    "my maze",
]

POLITE_BITS = [
    "",
    "pls",
    "please",
    "if you want",
    "when free",
    "now",
    "ty",
    "bro",
    "guys",
    "need help",
    "it is open",
]

def generate_world_invite(rng):
    world = safe_world_name(rng)
    verb = rng.choice(INVITE_VERBS)
    target = rng.choice(INVITE_TARGETS)
    polite = rng.choice(POLITE_BITS)

    patterns = [
        "{verb} to {target} {world}",
        "{verb} {world}",
        "{verb} my world {world}",
        "{verb} {target} called {world}",
        "{verb} {target}{sep}{world}",
        "can you {verb} {world}",
        "hey {verb} {world}",
        "{world} is open",
        "{world} open now",
        "world {world} is open",
        "my world is {world}",
        "new world {world}",
        "rate world {world}",
        "help me in {world}",
        "come help at {world}",
    ]

    text = rng.choice(patterns).format(
        verb=verb,
        target=target,
        world=world,
        sep=rng.choice([" ", "=", ":", " - "]),
    )

    if polite:
        text += " " + polite

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.08, p_word=0.08)

def install_world_invites(gen):
    gen.add_rule("WORLD_INVITE", generate_world_invite)