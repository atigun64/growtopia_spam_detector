from .base import weighted, reseed_fake, safe_world_name, FAKER
from text_mutator import TextMutator

def generate_gameplay_negative(rng):
    """
    Normal gameplay / social chat that is NOT spam.

    Important examples:
    - play games in world52
    - lets play in world52
    - come play with friends
    - join us for minigames
    - testing a maze in world52
    """
    reseed_fake(rng, FAKER)

    world = safe_world_name(rng)

    # Faker-driven normal activities, then mix with GT-like words.
    activity = rng.choice(weighted([
        (FAKER.word(), 18),
        (FAKER.catch_phrase(), 10),
        (FAKER.bs(), 8),
        ("games", 12),
        ("minigames", 12),
        ("parkour", 10),
        ("maze", 10),
        ("puzzle", 8),
        ("race", 8),
        ("event", 8),
        ("challenge", 6),
        ("map", 6),
        ("quest", 4),
    ]))

    # Clean up faker output a bit
    activity = TextMutator.clean_text(activity, 40).lower()
    if not activity:
        activity = "games"

    # Human-like actions around gameplay
    action = rng.choice(weighted([
        ("play", 18),
        ("join", 12),
        ("come play", 12),
        ("try", 10),
        ("test", 10),
        ("run", 8),
        ("race", 8),
        ("build", 8),
        ("farm", 6),
        ("help with", 6),
        ("watch", 4),
        ("hang out in", 4),
    ]))

    # Context from faker plus normal chat phrases
    context = rng.choice(weighted([
        (FAKER.sentence(nb_words=rng.randint(3, 7)).rstrip("."), 12),
        (FAKER.catch_phrase(), 8),
        (FAKER.bs(), 6),
        ("for fun", 15),
        ("with friends", 15),
        ("right now", 10),
        ("if you want", 10),
        ("when free", 10),
        ("for a minute", 8),
        ("this round", 8),
        ("after farm", 6),
        ("before we leave", 6),
        ("in this world", 10),
    ]))

    context = TextMutator.clean_text(context, 60)
    if not context:
        context = "for fun"

    # A few direct non-spam gameplay patterns
    patterns = [
        "play {activity} in {world}",
        "lets {action} {activity} in {world}",
        "come {action} {activity} at {world}",
        "join us for {activity} in {world}",
        "testing {activity} in {world}",
        "fun {activity} in {world}",
        "new {activity} open in {world}",
        "we are doing {activity} {context}",
        "going to {activity} {context}",
        "anyone want to {action} {activity} {context}",
        "who wants to {action} {activity}",
        "come {action} {activity} {context}",
        "help with {activity} in {world}",
        "rate the {activity} in {world}",
        "we play {activity} {context}",
        "playing {activity} {context}",
        "join {activity} {context}",
        "come here and {action} {activity}",
        "meet at {world} for {activity}",
        "doing {activity} at {world}",
    ]

    text = rng.choice(patterns).format(
        action=action,
        activity=activity,
        context=context,
        world=world,
    )

    # Occasionally make it look more like real chat
    if rng.random() < 0.20:
        text = rng.choice([
            f"{text} please",
            f"{text} lol",
            f"{text} bro",
            f"{text} guys",
            f"{text} anyone?",
            f"{text} ty",
        ])

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.07, p_word=0.06)

def install_gameplay_negative(gen):
    gen.add_rule("GAMEPLAY_NEGATIVE", generate_gameplay_negative)