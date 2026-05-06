from text_mutator import TextMutator
from helper import weighted
import random

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
    return TextMutator.random_case(rng, "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") + rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(len)))
