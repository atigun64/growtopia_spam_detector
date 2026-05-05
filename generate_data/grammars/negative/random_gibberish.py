from .base import weighted, random_case, insert_noise_between_chars, maybe_noisy_line

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

def install_random_gibberish(gen):
    gen.add_rule("RANDOM_GIBBERISH", generate_random_gibberish)