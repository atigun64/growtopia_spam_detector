from .base import weighted, maybe_noisy_line

URGENT_ACTIONS = [
    "go",
    "gas",
    "move",
    "push",
    "rush",
    "hurry",
    "come on",
    "lets go",
    "go now",
    "do it",
    "jump",
    "run",
    "charge",
]

URGENT_ENDINGS = [
    "",
    " now",
    " bro",
    " pls",
    " fast",
    " quick",
    "!!",
    "!!!",
]

def generate_aggressive_intent(rng):
    """
    Negative examples with urgency/aggressive repetition.

    These should NOT be treated as spam just because they are repetitive.
    Examples:
        go go go
        gas gas gas
        move move move
        gogogogogo
        gas gas gas now
    """
    action = rng.choice(URGENT_ACTIONS)

    mode = rng.choice(weighted([
        ("repeat_word", 45),
        ("repeat_phrase", 20),
        ("stutter", 15),
        ("burst", 20),
    ]))

    if mode == "repeat_word":
        n = rng.randint(2, 6)
        text = " ".join([action] * n)

    elif mode == "repeat_phrase":
        n = rng.randint(2, 5)
        phrase = rng.choice([
            f"{action} now",
            f"{action} fast",
            f"{action} quickly",
            f"{action} please",
            f"{action} bro",
        ])
        text = " ".join([phrase] * n)

    elif mode == "stutter":
        # gogogogogo / gasgasgas
        repeat = rng.randint(3, 8)
        text = (action.replace(" ", "") * repeat)

    else:
        # "go go go!!!", "gas gas gas now"
        n = rng.randint(2, 5)
        text = " ".join([action] * n) + rng.choice(URGENT_ENDINGS)

    return maybe_noisy_line(rng, text, line_p=0.06, p_word=0.04)

def install_aggressive_intent(gen):
    gen.add_rule("AGGRESSIVE_INTENT", generate_aggressive_intent)