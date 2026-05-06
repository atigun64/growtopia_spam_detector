from text_mutator import TextMutator
from .base import safe_world_name, safe_user_name, fake_item_name, random_price
from word_generation.extra_words import random_currency_bid, random_normal_meaning_bid, random_strong_casino_bid, random_base_bid_token
from helper import weighted

def generate_basebid_hard_negative(rng):
    """
    Negative examples that explicitly use BASE_BIDS tokens.

    Purpose:
    Teach model that seeing BJ/RM/QQ/CSN/REME/CASINO/MIN/GAS/DL/WL/BEJE/TURK/BGL
    is not automatically positive.

    But:
    - CASINO=WORLD
    - CSN WORLD
    - BJ/WL/DL style direct promo

    should still be positive in your positive dataset, not here.
    """
    world = safe_world_name(rng)
    user = safe_user_name(rng)
    price = random_price(rng)
    item = fake_item_name(rng)

    mode = rng.choice(weighted([
        ("currency", 35),
        ("normal_meaning", 30),
        ("casino_discussion", 25),
        ("token_meta", 10),
    ]))

    if mode == "currency":
        bid = TextMutator.style_bid_token(rng, random_currency_bid(rng))

        patterns = [
            "{bid} shop{sep}{world}",
            "{bid} price check",
            "how much is 1 {bid}",
            "change {bid} to wls",
            "change wls to {bid}",
            "need 1 {bid} change",
            "selling item for {price}",
            "buy {item} with {bid}",
            "{item} costs {price}",
            "cheap shop accepts {bid}",
            "owner takes {bid} or wls",
            "vend has {item} for {price}",
            "is {price} fair",
        ]

        text = rng.choice(patterns).format(
            bid=bid,
            sep=rng.choice(["=", ":", " ", " - ", "/"]),
            world=world,
            price=price,
            item=item,
        )

    elif mode == "normal_meaning":
        raw_bid = random_normal_meaning_bid(rng)
        bid = TextMutator.style_bid_token(rng, raw_bid)

        if raw_bid == "RM":
            patterns = [
                "{bid} me from access",
                "{bid} {user} from door",
                "owner {bid} {user}",
                "please {bid} access",
                "{bid} access from {user}",
                "can admin {bid} me",
            ]
        elif raw_bid == "MIN":
            patterns = [
                "{bid} price {price}",
                "{bid} offer {price}",
                "minimum price is {price}",
                "{bid} {price} for {item}",
                "what is {bid} price",
                "{item} has {bid} price",
            ]
        elif raw_bid == "GAS":
            patterns = [
                "{bid} mask {price}",
                "selling {bid} mask",
                "buy {bid} mask {price}",
                "grass block {price}",
                "grass seed shop {world}",
                "need grass for farm",
            ]
        elif raw_bid == "TURK":
            patterns = [
                "any {bid} here",
                "{bid} friend {user}",
                "{bid} owner is {user}",
                "turkish world {world}",
                "i speak turkish",
                "looking for turk friends",
            ]
        else:  # QQ
            patterns = [
                "{bid} bro wait",
                "{bid} my friend {user}",
                "{bid} why door closed",
                "someone named {bid}{num}",
                "my friend says {bid}",
                "{bid} is just random text",
            ]

        text = rng.choice(patterns).format(
            bid=bid,
            user=user,
            world=world,
            price=price,
            item=item,
            num=rng.randint(1, 999),
        )

    elif mode == "casino_discussion":
        raw_bid = random_strong_casino_bid(rng)
        bid = TextMutator.style_bid_token(rng, raw_bid, obf_p=0.10, noise_p=0.05, case_p=0.30)

        patterns = [
            "i hate {bid}",
            "stop saying {bid}",
            "{bid} spam is annoying",
            "report {bid} spam",
            "too many {bid} bots",
            "why people type {bid}",
            "what does {bid} mean",
            "is {bid} illegal",
            "is {bid} banned",
            "dont advertise {bid}",
            "do not join {bid}",
            "avoid {bid} worlds",
            "someone said {bid} here",
            "{user} keeps saying {bid}",
            "{user} is talking about {bid}",
            "i saw {bid} spam in {world}",
            "dont go to {world} they spam {bid}",
            "talking about {bid} is not advertising",
        ]

        text = rng.choice(patterns).format(
            bid=bid,
            user=user,
            world=world,
        )

    else:  # token_meta
        raw_bid = random_base_bid_token(rng)
        bid = TextMutator.style_bid_token(rng, raw_bid, obf_p=0.12, noise_p=0.06, case_p=0.35)

        patterns = [
            "what means {bid}",
            "why people say {bid}",
            "{bid} is just a word",
            "someone named world {world} said {bid}",
            "does {bid} mean anything",
            "i dont understand {bid}",
            "not every {bid} is spam",
            "can {bid} be a name",
            "{bid} looks like random letters",
            "my friend typed {bid}",
        ]

        text = rng.choice(patterns).format(
            bid=bid,
            world=world,
        )

    return TextMutator.maybe_noisy_line(rng, text, line_p=0.14, p_word=0.12)

def install_hard_negatives(gen):
    gen.add_rule("BASEBID_HARD_NEGATIVE", generate_basebid_hard_negative)