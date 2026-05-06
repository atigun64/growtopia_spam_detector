from .base import safe_user_name, safe_world_name, maybe_noisy_line
from text_mutator import TextMutator

OWNER_ROLES = [
    "owner",
    "admin",
    "builder",
    "mod",
    "host",
    "main",
    "leader",
    "access",
]

def generate_owner_info(rng):
    role = rng.choice(OWNER_ROLES)
    user = safe_user_name(rng)
    world = safe_world_name(rng)
    num = rng.randint(1, 9999)

    patterns = [
        "{role} is {user}",
        "{role}{sep}{user}",
        "{role} of {world} is {user}",
        "{world} owner is {user}",
        "world owner {user}",
        "{user} owns this",
        "door id is {num}",
        "password changed",
        "admin added {user}",
        "access given to {user}",
        "ban {user} from world",
        "pull {user} please",
        "kick {user}",
        "wrench {user}",
        "remove access from {user}",
        "rm {user} from access",      # hard negative: RM
    ]

    text = rng.choice(patterns).format(
        role=role,
        user=user,
        world=world,
        num=num,
        sep=rng.choice([" ", "=", ":", " = ", " : "]),
    )

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.09, p_word=0.09)

def install_owner_info(gen):
    gen.add_rule("OWNER_INFO", generate_owner_info)