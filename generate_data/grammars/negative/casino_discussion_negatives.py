from .base import weighted, safe_user_name, safe_world_name, fake_words_safe, maybe_noisy_line
from text_mutator import TextMutator

def casino_word_variant(rng):
    """
    Explicit casino/csn mentions that are NOT ads.
    Small chance of obfuscation so the model learns:
        obfuscated casino discussion != automatically casino ad.
    """
    word = rng.choice(weighted([
        ("casino", 45),
        ("casinos", 10),
        ("csn", 25),
        ("c s n", 5),
        ("c-a-s-i-n-o", 4),
        ("c4sino", 3),
        ("cas1no", 3),
        ("gamble", 3),
        ("gambling", 2),
    ]))

    if rng.random() < 0.10:
        word = TextMutator.obfuscate_word(rng, word, p=0.12)

    if rng.random() < 0.06:
        word = TextMutator.insert_noise_between_chars(rng, word)

    if rng.random() < 0.18:
        word = TextMutator.random_case(rng, word)

    return word

def generate_casino_discussion_negative(rng):
    """
    Negative examples that mention casino/csn but are not promotional.

    These are extremely important so the model does not learn:
        casino token == positive

    Avoid making too many of these look like direct ads:
        casino=WORLD
        go casino WORLD
        join csn WORLD

    But include some anti-promotion/reporting examples with world/user names.
    """
    cw = casino_word_variant(rng)
    user = safe_user_name(rng)
    world = safe_world_name(rng)

    # Some dynamic filler from Faker, but controlled.
    topic = fake_words_safe(rng, 1, 3)

    patterns = [
        # Opinions / complaints
        "i hate {cw}",
        "i dont like {cw}",
        "{cw} is annoying",
        "{cw} spam is everywhere",
        "too many {cw} spammers",
        "stop talking about {cw}",
        "why people still do {cw}",
        "{cw} ruined this game",
        "i am tired of {cw} ads",
        "these {cw} bots are annoying",

        # Questions / education
        "what does {cw} mean",
        "is {cw} illegal",
        "is {cw} banned",
        "why is {cw} not allowed",
        "can you get banned for {cw}",
        "what is {cw}",
        "someone explain {cw}",
        "why do people say {cw}",
        "does {cw} mean gambling",
        "is {cw} against rules",

        # Reporting / moderation
        "report {cw} spam",
        "reported {cw} spammer",
        "ban {cw} bots",
        "mod please check {cw} spam",
        "there is a {cw} spammer here",
        "{user} keeps saying {cw}",
        "{user} is spamming {cw}",
        "someone report {user} for {cw}",
        "i saw {cw} spam in {world}",
        "dont go to {world} they spam {cw}",
        "avoid {world} it has {cw} spam",
        "{world} has {cw} spammer",

        # Non-ad mentions with suspicious tokens
        "they play something like qq",
        "someone said qq is like {cw}",
        "qq is not always {cw}",
        "csn means {topic} maybe",
        "why people type csn",
        "not every csn word is an ad",
        "he said casino but not advertising",
        "talking about {cw} is not same as advertising",

        # Anti-invite forms, useful hard negatives
        "dont join {cw}",
        "dont play {cw}",
        "dont advertise {cw}",
        "stop advertising {cw}",
        "do not go to {cw}",
        "never trust {cw} worlds",
        "avoid {cw} worlds",
        "report worlds that advertise {cw}",
    ]

    text = rng.choice(patterns).format(
        cw=cw,
        user=user,
        world=world,
        topic=topic,
    )

    # Discussion negatives can have mild normal-user weirdness.
    # Keep it rare/moderate.
    return TextMutator.maybe_noisy_line(rng, text, line_p=0.10, p_word=0.08)

def install_casino_discussion_negatives(gen):
    gen.add_rule("CASINO_DISCUSSION_NEGATIVE", generate_casino_discussion_negative)