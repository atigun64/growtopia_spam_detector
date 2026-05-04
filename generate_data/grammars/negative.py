from helper import weighted, obfuscate_word, insert_noise_between_chars, random_case
from world_name_generator import random_world_name
from faker import Faker
import re

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
    return random_case(rng, "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") + rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(len)))


def install_negative_spam_grammar(gen):
    """
    Negative casino-ad dataset generator for Growtopia-like messages.

    Goals:
    - Generate NON-casino messages.
    - Use Faker for variety, not only fixed word lists.
    - Include hard negatives that look ad-like/suspicious:
        - go my world WORLD
        - owner is USER
        - dl shop WORLD
        - gas mask 5wl
        - min price 3wl
        - repeated-world-invite style single messages
    - Include rare obfuscation/noise in normal messages.
    - Avoid accidental true casino/csn negatives.
    """

    fake = Faker("en_US")

    # ------------------------------------------------------------------
    # Important:
    # These are NOT all positive casino bid tokens.
    #
    # This filter is only to prevent accidental label contamination from
    # random Faker/world/user generation.
    #
    # Do NOT put all BASE_BIDS here, because many are valid negatives:
    # WL/DL/BGL = normal currency
    # GAS = gas mask / grass
    # MIN = minimum price
    # TURK = social/nationality context
    # RM = remove
    # QQ = random/social noise
    # ------------------------------------------------------------------

    STRONG_CASINO_CONTAMINATION_TERMS = [
        "casino",
        "c4sino",
        "cas1no",
        "casiino",
        "cazino",
        "csn",
        "c5n",
    ]

    LEET_TABLE = str.maketrans({
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
    })
    
		    # ------------------------------------------------------------------
    # Shared casino-ad tokens used as controlled hard negatives
    # ------------------------------------------------------------------

    BASE_BIDS = [
        "BJ", "RM", "QQ", "CSN", "REME", "CASINO",
        "MIN", "GAS", "DL", "WL", "BEJE", "TURK", "BGL",
    ]

    # Tokens split by how they can safely appear in negative examples.
    CURRENCY_BIDS = ["DL", "WL", "BGL"]
    NORMAL_MEANING_BIDS = ["RM", "MIN", "GAS", "TURK", "QQ"]
    STRONG_CASINO_BIDS = ["CSN", "CASINO", "BJ", "REME", "BEJE"]

    def style_bid_token(rng, token, obf_p=0.08, noise_p=0.04, case_p=0.25):
        """
        Style a BASE_BIDS token in negative examples.

        Low/moderate noise so model learns:
            token/noise alone != casino ad.
        """
        out = token

        if rng.random() < case_p:
            out = random_case(rng, out)

        if rng.random() < obf_p:
            out = obfuscate_word(rng, out, p=0.12)

        if rng.random() < noise_p:
            out = insert_noise_between_chars(rng, out)

        return out

    def random_base_bid_token(rng):
        return rng.choice(BASE_BIDS)

    def random_currency_bid(rng):
        return rng.choice(CURRENCY_BIDS)

    def random_normal_meaning_bid(rng):
        return rng.choice(NORMAL_MEANING_BIDS)

    def random_strong_casino_bid(rng):
        return rng.choice(STRONG_CASINO_BIDS)


    def normalize_for_filter(text):
        low = str(text).lower().translate(LEET_TABLE)
        compact = re.sub(r"[^a-z0-9]+", "", low)
        return compact

    def contains_strong_casino_term(text):
        compact = normalize_for_filter(text)
        return any(term in compact for term in STRONG_CASINO_CONTAMINATION_TERMS)

    def clean_text(text, max_len=140):
        text = str(text)
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_len].strip()

    def safe_world_name(rng):
        for _ in range(30):
            w = random_world_name(rng)
            if not contains_strong_casino_term(w):
                return w
        return "WORLD" + str(rng.randint(1000, 999999))

    def safe_user_name(rng):
        for _ in range(30):
            u = random_user_name(rng)
            if not contains_strong_casino_term(u):
                return u
        return "player" + str(rng.randint(1000, 999999))

    gen.add_rule("WORLD_NAME", safe_world_name)
    gen.add_rule("USER_NAME", safe_user_name)

    gen.add_rule("SPACE", [" "])
    gen.add_rule("OPT_SPACE", ["", " "])

    gen.add_rule("ME", weighted([
        ("/me ", 18),
        ("", 82),
    ]))

    gen.add_rule("MSG", weighted([
        ("/msg {USER_NAME} ", 10),
        ("", 90),
    ]))

    gen.add_rule("TAIL", weighted([
        ("", 62),
        (".", 10),
        ("!", 10),
        ("!!", 4),
        ("?", 8),
        (" :)", 2),
        (" xD", 2),
        (" lol", 2),
    ]))

    gen.add_rule("SEPARATOR", weighted([
        (" ", 45),
        ("=", 10),
        (" = ", 8),
        (":", 10),
        (" : ", 5),
        ("-", 7),
        ("/", 5),
        ("//", 3),
        (" | ", 3),
        (" -> ", 4),
    ]))

    # ------------------------------------------------------------------
    # Styling / rare obfuscation
    # ------------------------------------------------------------------

    def maybe_style_word(rng, word, obf_p=0.025, noise_p=0.018, case_p=0.12):
        """
        Rare styling for normal messages.

        Keep low. The point is to teach:
            obfuscation can exist in negative messages too.
        Not:
            obfuscation means negative/positive by itself.
        """
        out = str(word)

        if rng.random() < case_p:
            out = random_case(rng, out)

        if rng.random() < obf_p:
            out = obfuscate_word(rng, out, p=0.10)

        if rng.random() < noise_p:
            out = insert_noise_between_chars(rng, out)

        return out

    def maybe_style_phrase(rng, text, p_word=0.06):
        parts = str(text).split(" ")
        out = []

        for part in parts:
            if rng.random() < p_word:
                out.append(maybe_style_word(rng, part))
            else:
                out.append(part)

        return " ".join(out)

    def maybe_noisy_line(rng, text, line_p=0.075, p_word=0.08):
        """
        Around 7.5% of negative lines get some normal-user weirdness.
        """
        if rng.random() < line_p:
            text = maybe_style_phrase(rng, text, p_word=p_word)
        return clean_text(text)

    # ------------------------------------------------------------------
    # Faker helpers
    # ------------------------------------------------------------------

    def reseed_fake(rng):
        fake.seed_instance(rng.randint(1, 2**32 - 1))

    def fake_word_safe(rng):
        for _ in range(20):
            reseed_fake(rng)
            w = fake.word()
            w = clean_text(w, 30)
            if w and not contains_strong_casino_term(w):
                return w
        return "item"

    def fake_words_safe(rng, min_n=1, max_n=3):
        n = rng.randint(min_n, max_n)
        words = []

        for _ in range(n):
            words.append(fake_word_safe(rng))

        text = " ".join(words)
        return clean_text(text, 60)

    def fake_sentence_safe(rng):
        """
        Faker-generated general chat.
        This adds broad linguistic variety.
        """
        for _ in range(20):
            reseed_fake(rng)

            style = rng.choice(weighted([
                ("sentence", 45),
                ("question", 20),
                ("short_chat", 20),
                ("catch", 10),
                ("bs", 5),
            ]))

            if style == "sentence":
                text = fake.sentence(nb_words=rng.randint(3, 11)).rstrip(".")
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
                text = fake.catch_phrase()
            elif style == "bs":
                text = fake.bs()
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

            text = clean_text(text)

            if text and not contains_strong_casino_term(text):
                return maybe_noisy_line(rng, text, line_p=0.06, p_word=0.06)

        return "hello can someone help"

    gen.add_rule("FAKE_CHAT", fake_sentence_safe)

    # ------------------------------------------------------------------
    # Dynamic item / price generation
    # ------------------------------------------------------------------

    # Some GT-ish fixed roots are okay. The variety comes from Faker modifiers,
    # random prices, random worlds, random verbs, and multiple templates.
    # You do not want 100% Faker items because it creates too much nonsense.
    GT_ITEM_ROOTS = [
        "seed",
        "seeds",
        "block",
        "blocks",
        "door",
        "doors",
        "sign",
        "platform",
        "wall",
        "background",
        "wrench",
        "lock",
        "fossil",
        "geiger",
        "crystal",
        "chair",
        "table",
        "display block",
        "vend",
        "vending machine",
        "farmable",
        "pepper",
        "chand",
        "laser grid",
        "surg tool",
        "pack",
        "bait",
        "fish tank",
        "weather machine",
        "song",
        "hair",
        "shirt",
        "pants",
        "wing",
        "cape",
        "mask",
        "gas mask",       # hard negative: GAS but normal
        "grass block",    # hard negative: GAS-ish substring but normal
        "sugar cane",
        "lava",
        "water",
        "dirt",
        "rock",
        "platform",
        "checkpoint",
        "portal",
        "world key",
    ]

    NORMAL_CURRENCIES = [
        "wl",
        "wls",
        "dl",
        "dls",
        "bgl",
        "gems",
        "/wl",
        "per wl",
    ]

    def random_price(rng):
        amount = rng.choice(weighted([
            (str(rng.randint(1, 20)), 55),
            (str(rng.randint(21, 100)), 25),
            (str(rng.randint(101, 999)), 10),
            (str(rng.randint(1, 5)) + "/" + str(rng.randint(1, 20)), 10),
        ]))

        currency = rng.choice(NORMAL_CURRENCIES)

        if rng.random() < 0.25:
            return amount + " " + currency
        return amount + currency

    def fake_item_name(rng):
        """
        Semi-dynamic item names.

        Mostly GT-ish, sometimes Faker-extended.
        Avoids repeating only stuff like 'sell weather'.
        """
        root = rng.choice(GT_ITEM_ROOTS)

        mode = rng.choice(weighted([
            ("plain", 45),
            ("color", 18),
            ("fake_prefix", 18),
            ("fake_two_prefix", 8),
            ("condition", 11),
        ]))

        if mode == "plain":
            item = root
        elif mode == "color":
            reseed_fake(rng)
            item = fake.color_name().lower() + " " + root
        elif mode == "fake_prefix":
            item = fake_word_safe(rng) + " " + root
        elif mode == "fake_two_prefix":
            item = fake_words_safe(rng, 1, 2) + " " + root
        else:
            item = rng.choice([
                "cheap",
                "rare",
                "clean",
                "fresh",
                "old",
                "new",
                "small",
                "big",
                "full",
                "empty",
                "public",
                "private",
            ]) + " " + root

        item = clean_text(item, 80)

        if contains_strong_casino_term(item):
            return root

        return item

    # ------------------------------------------------------------------
    # Normal world invites
    # ------------------------------------------------------------------

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

        return maybe_noisy_line(rng, text, line_p=0.08, p_word=0.08)

    gen.add_rule("WORLD_INVITE", generate_world_invite)

    # ------------------------------------------------------------------
    # Trade/shop/vend messages
    # ------------------------------------------------------------------

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
            sep=rng.choice(["=", ":", " = ", " : ", " - "]),
        )

        return maybe_noisy_line(rng, text, line_p=0.075, p_word=0.075)

    gen.add_rule("TRADE_MESSAGE", generate_trade_message)

    # ------------------------------------------------------------------
    # Owner/world info messages
    # ------------------------------------------------------------------

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

        return maybe_noisy_line(rng, text, line_p=0.09, p_word=0.09)

    gen.add_rule("OWNER_INFO", generate_owner_info)

    # ------------------------------------------------------------------
    # Help/social/gameplay
    # ------------------------------------------------------------------

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

        return maybe_noisy_line(rng, text, line_p=0.075, p_word=0.075)

    gen.add_rule("HELP_SOCIAL", generate_help_social)

    # ------------------------------------------------------------------
    # Explicit hard negatives with BASE_BIDS-looking tokens
    # ------------------------------------------------------------------

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
            bid = style_bid_token(rng, random_currency_bid(rng))

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
            bid = style_bid_token(rng, raw_bid)

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
            bid = style_bid_token(rng, raw_bid, obf_p=0.10, noise_p=0.05, case_p=0.30)

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
            bid = style_bid_token(rng, raw_bid, obf_p=0.12, noise_p=0.06, case_p=0.35)

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

        return maybe_noisy_line(rng, text, line_p=0.14, p_word=0.12)

    gen.add_rule("BASEBID_HARD_NEGATIVE", generate_basebid_hard_negative)


    gen.add_rule("BASEBID_HARD_NEGATIVE", generate_basebid_hard_negative)

    # ------------------------------------------------------------------
    # Very noisy but still normal messages
    # ------------------------------------------------------------------

    def generate_noisy_normal(rng):
        """
        Rare noisy negatives.

        These are useful because real players sometimes type ugly messages.
        Keep this category small in the top-level distribution.
        """
        base = rng.choice(weighted([
            (generate_world_invite, 30),
            (generate_trade_message, 25),
            (generate_owner_info, 20),
            (generate_help_social, 15),
            (fake_sentence_safe, 10),
        ]))(rng)

        # Stronger styling than normal, but still no casino words.
        text = maybe_style_phrase(rng, base, p_word=0.22)
        text = clean_text(text)

        if contains_strong_casino_term(text):
            return "hello can someone help"

        return text

    gen.add_rule("NOISY_NORMAL", generate_noisy_normal)


    # ------------------------------------------------------------------
    # Casino/Csn discussion negatives
    # ------------------------------------------------------------------

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
            word = obfuscate_word(rng, word, p=0.12)

        if rng.random() < 0.06:
            word = insert_noise_between_chars(rng, word)

        if rng.random() < 0.18:
            word = random_case(rng, word)

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
        return maybe_noisy_line(rng, text, line_p=0.10, p_word=0.08)

    gen.add_rule("CASINO_DISCUSSION_NEGATIVE", generate_casino_discussion_negative)


    # ------------------------------------------------------------------
    # Aggressive / urgent repetition
    # ------------------------------------------------------------------

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

    gen.add_rule("AGGRESSIVE_INTENT", generate_aggressive_intent)


    # ------------------------------------------------------------------
    # Random gibberish / keyboard smash
    # ------------------------------------------------------------------

    QWERTY_CHARS = "qwertyuiopasdfghjklzxcvbnm"

    def random_gibberish_word(rng, min_len=6, max_len=16):
        length = rng.randint(min_len, max_len)

        # Mix of keyboard-smash and random consonant-heavy strings
        mode = rng.choice(weighted([
            ("keyboard", 45),
            ("random", 35),
            ("repeat", 20),
        ]))

        if mode == "keyboard":
            start = rng.randint(0, len(QWERTY_CHARS) - 1)
            step = rng.choice([-2, -1, 1, 2, 3])
            out = []
            idx = start
            for _ in range(length):
                out.append(QWERTY_CHARS[idx % len(QWERTY_CHARS)])
                idx += step
            return "".join(out)

        elif mode == "repeat":
            ch = rng.choice(QWERTY_CHARS)
            return ch * length

        else:
            letters = "abcdefghijklmnopqrstuvwxyz"
            out = []
            for i in range(length):
                if i % 3 == 0:
                    out.append(rng.choice(letters))
                else:
                    out.append(rng.choice(letters + "sjdkfghqwermn"))
            return "".join(out)

    def generate_random_gibberish(rng):
        """
        Negative examples for nonsense / keyboard smash.

        Important:
        These should not be considered spam just because they are random-looking.
        Examples:
            dsgoijadsgjasg
            xjskdksjd
            qweqweqwe
            asdfghjkl
        """
        n_words = rng.choice(weighted([
            (1, 70),
            (2, 20),
            (3, 10),
        ]))

        words = []
        for _ in range(n_words):
            w = random_gibberish_word(rng)

            # small chance to make it look like a human typo burst
            if rng.random() < 0.15:
                w = random_case(rng, w)

            if rng.random() < 0.08:
                w = insert_noise_between_chars(rng, w)

            words.append(w)

        text = " ".join(words)

        # occasionally add punctuation so it resembles actual chat noise
        if rng.random() < 0.25:
            text += rng.choice(["", "!", "!!", "?", "???", " lol", " idk", " omg"])

        return maybe_noisy_line(rng, text, line_p=0.03, p_word=0.03)

    gen.add_rule("RANDOM_GIBBERISH", generate_random_gibberish)


    gen.add_rule("NONSPAM_MESSAGE", weighted([
        # Broad general negative chat
        ("{MSG}{FAKE_CHAT}{TAIL}", 15),
        ("{ME}{HELP_SOCIAL}{TAIL}", 15),

        # casino/csn mentioned, but not promotional
        ("{ME}{CASINO_DISCUSSION_NEGATIVE}{TAIL}", 8),
        ("{MSG}{CASINO_DISCUSSION_NEGATIVE}{TAIL}", 2),

        # One world invite should usually be negative.
        ("{ME}{WORLD_INVITE}{TAIL}", 18),
        ("{MSG}{WORLD_INVITE}{TAIL}", 5),

        # Trade/shop with WL/DL/BGL but not casino.
        ("{ME}{TRADE_MESSAGE}{TAIL}", 15),
        ("{MSG}{TRADE_MESSAGE}{TAIL}", 5),

        # Owner/world/admin info.
        ("{ME}{OWNER_INFO}{TAIL}", 10),
        ("{MSG}{OWNER_INFO}{TAIL}", 4),

        # Hard negatives with BASE_BIDS-looking tokens.
        ("{ME}{BASEBID_HARD_NEGATIVE}{TAIL}", 12),
        ("{MSG}{BASEBID_HARD_NEGATIVE}{TAIL}", 4),

        # New: aggressive urgency / repeated commands
        ("{ME}{AGGRESSIVE_INTENT}{TAIL}", 6),
        ("{MSG}{AGGRESSIVE_INTENT}{TAIL}", 2),

        # New: random gibberish / keyboard smash
        ("{ME}{RANDOM_GIBBERISH}{TAIL}", 3),
        ("{MSG}{RANDOM_GIBBERISH}{TAIL}", 1),

        # Rare obfuscated/noisy normal messages.
        ("{ME}{NOISY_NORMAL}{TAIL}", 4),
        ("{MSG}{NOISY_NORMAL}{TAIL}", 2),
    ]))
