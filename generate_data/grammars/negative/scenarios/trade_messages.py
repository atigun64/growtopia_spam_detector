from ..common import safe_world_name
from ..domain import fake_item_name, random_price
from text_mutator import TextMutator

TRADE_VERBS = [
    "buy",
    "sell",
    "trade",
    "need",
    "looking for",
    "lf",
    "selling",
    "buying",
    "price check",
    "pc",
]

SHOP_WORDS = [
    "shop",
    "vend",
    "vends",
    "store",
    "market",
    "cheap shop",
    "farm shop",
    "seed shop",
    "block shop",
    "surg shop",
    "fish shop",
    "geiger shop",
    "clothes shop",
    "weather shop",
]

def generate_trade_message(rng):
    item = fake_item_name(rng)
    price = random_price(rng)
    world = safe_world_name(rng)
    verb = rng.choice(TRADE_VERBS)
    shop = rng.choice(SHOP_WORDS)

    patterns = [
        "{verb} {item} {price}",
        "{verb} {item} for {price}",
        "{item} {price}",
        "{item}{sep}{price}",
        "{shop} at {world}",
        "{shop} {world}",
        "{shop} open {world}",
        "go {world} for {item}",
        "vend at {world} {item}",
        "cheap {item} at {world}",
        "selling {item} in {world}",
        "buying {item} msg me",
        "need {item} paying {price}",
        "{world} has {item}",
        "{item} in vend {world}",
        "restocked {shop} {world}",
    ]

    text = rng.choice(patterns).format(
        verb=verb,
        item=item,
        price=price,
        world=world,
        shop=shop,
        sep=rng.choice(["=", ":", " = ", " : ", " - ", " at ", " for ", " in "]),
    )

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.075, p_word=0.075)

def install_trade_messages(gen):
    gen.add_rule("TRADE_MESSAGE", generate_trade_message)