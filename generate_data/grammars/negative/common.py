from helper import weighted
from generate_data.generators.name_generator import random_name_generator
from faker import Faker
import re
from text_mutator import TextMutator
from generate_data.generators import random_user_name

FAKER = Faker("en_US")
STRONG_CASINO_CONTAMINATION_TERMS = [
    "casino",
    "c4sino",
    "cas1no",
    "casiino",
    "cazino",
    "csn",
    "c5n",
]

def fake_word_safe(rng):
    for _ in range(20):
        reseed_fake(rng, FAKER)
        w = FAKER.word()
        w = TextMutator.clean_text(w, 30)
        if w and not contains_strong_casino_term(w):
            return w
    return "item"

def reseed_fake(rng, FAKER):
    FAKER.seed_instance(rng.randint(1, 2**32 - 1))

def contains_strong_casino_term(text):
    compact = TextMutator.normalize_for_filter(text)
    return any(term in compact for term in STRONG_CASINO_CONTAMINATION_TERMS)

def safe_world_name(rng):
    for _ in range(30):
        w = random_name_generator(rng)
        if not contains_strong_casino_term(w):
            return w
    return "WORLD" + str(rng.randint(1000, 999999))

def safe_user_name(rng):
    for _ in range(30):
        u = random_user_name(rng)
        if not contains_strong_casino_term(u):
            return u
    return "player" + str(rng.randint(1000, 999999))

def fake_words_safe(rng, min_n=1, max_n=3):
    n = rng.randint(min_n, max_n)
    words = []

    for _ in range(n):
        words.append(fake_word_safe(rng))

    text = " ".join(words)
    return TextMutator.clean_text(text, 60)

def fake_sentence_safe(rng):
    """
    Faker-generated general chat.
    This adds broad linguistic variety.
    """
    for _ in range(20):
        reseed_fake(rng, FAKER)

        style = rng.choice(weighted([
            ("sentence", 45),
            ("question", 20),
            ("short_chat", 20),
            ("catch", 10),
            ("bs", 5),
        ]))

        if style == "sentence":
            text = FAKER.sentence(nb_words=rng.randint(3, 11)).rstrip(".")
        elif style == "question":
            topic = fake_words_safe(rng, 1, 3)
            text = rng.choice([
                f"can someone help with {topic}",
                f"does anyone know {topic}",
                f"where is {topic}",
                f"how much is {topic}",
                f"who owns this world",
                f"is the owner here",
                f"can someone open the door",
                f"why am i stuck",
                f"where is the white door",
            ])
        elif style == "catch":
            text = FAKER.catch_phrase()
        elif style == "bs":
            text = FAKER.bs()
        else:
            text = rng.choice([
                "hi",
                "hello",
                "yo",
                "wait",
                "brb",
                "come here",
                "follow me",
                "nice world",
                "cool farm",
                "thanks",
                "ty",
                "np",
                "lol",
                "lag",
                "relog",
                "where are you",
                "owner here",
            ])

        text = TextMutator.clean_text(text)

        if text and not contains_strong_casino_term(text):
            return TextMutator.maybe_noisy_line(rng, text, line_p=0.06, p_word=0.06)

    return "hello can someone help"
