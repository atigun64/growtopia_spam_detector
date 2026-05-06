import re

class TextMutator:
    """
    Comprehensive text mutation library consolidating all mutations from positive and negative grammar files.
    Organized by mutation type and probability levels.
    """

    # Character-level obfuscation mappings
    LEET_OUT = {
        "a": ["4", "@", "a"],
        "e": ["3", "e"],
        "i": ["1", "i"],
        "o": ["0", "o"],
        "s": ["$", "5", "s"],
        "t": ["7", "t"],
        "g": ["9", "g"],
        "b": ["8", "b"],
        "l": ["1", "l"],
        "c": ["(", "c"],
    }

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

    NOISE_CHARS = ["", "", "", ".", "/", "//", "'", "-", "_", " ", "$"]
    SEPARATORS = [".", "/", "-", " ", "'", "_", ""]
    NOISE_SEPARATORS = [".", "/", "-", "'", "_", " ", "//", ":"]

    @staticmethod
    def weighted(items):
        """
        Convert:
            [("a", 3), ("b", 1)]
        into:
            ["a", "a", "a", "b"]
        """
        out = []
        for value, weight in items:
            out.extend([value] * weight)
        return out

    @staticmethod
    def random_case(rng, text: str) -> str:
        """
        Applies one of 5 case styles to text:
        1. UPPERCASE
        2. lowercase
        3. Title Case
        4. RaNdOm MiXeD cAsE
        5. Original
        """
        style = rng.randint(1, 5)
        if style == 1:
            return text.upper()
        if style == 2:
            return text.lower()
        if style == 3:
            return text.title()
        if style == 4:
            return "".join(ch.upper() if rng.random() < 0.5 else ch.lower() for ch in text)
        return text

    @staticmethod
    def obfuscate_word(rng, text: str, p=0.35) -> str:
        """
        Applies leet-speak obfuscation to text.
        Replaces characters with numbers/symbols (e.g., a->4, e->3, s->$).
        
        Args:
            rng: Random number generator
            text: Text to obfuscate
            p: Probability of obfuscating each character (default: 0.35)
        """
        out = []
        for ch in text:
            low = ch.lower()
            if low in TextMutator.LEET_OUT and rng.random() < p:
                repl = rng.choice(TextMutator.LEET_OUT[low])
                if ch.isupper():
                    repl = repl.upper()
                out.append(repl)
            else:
                out.append(ch)
        return "".join(out)

    @staticmethod
    def insert_noise_between_chars(rng, text: str, p=0.35) -> str:
        """
        Inserts random noise characters between letters.
        Examples: BJ -> B.J, CSN -> C/S//N
        
        Args:
            rng: Random number generator
            text: Text to add noise to
            p: Probability of inserting noise between chars (default: 0.35)
        """
        out = []
        for i, ch in enumerate(text):
            out.append(ch)
            if i != len(text) - 1 and rng.random() < p:
                out.append(rng.choice(TextMutator.NOISE_CHARS))
        return "".join(out)

    @staticmethod
    def add_suffix(rng, text: str) -> str:
        """
        Appends a small random suffix to text with 18% probability.
        Examples: BJ -> BJ1, CSN -> CSN9, REME -> REME.
        """
        if rng.random() >= 0.18:
            return text
        suffixes = ["1", "2", "3", "4", "5", "8", "9", ".", "!", "E"]
        return text + rng.choice(suffixes)

    @staticmethod
    def insert_one_noise_char(rng, text: str) -> str:
        """
        Inserts one random noise character at a random position in text.
        Examples: BJ -> B.J, CSN -> C/SN
        """
        if len(text) < 2:
            return text
        noise = rng.choice(TextMutator.NOISE_SEPARATORS)
        pos = rng.randint(1, len(text) - 1)
        return text[:pos] + noise + text[pos:]

    @staticmethod
    def space_out(rng, text: str) -> str:
        """
        Splits text into space-separated characters with 20% probability.
        Examples: BJ -> B J, CSN -> C S N
        """
        if rng.random() >= 0.20:
            return text
        return " ".join(list(text))

    @staticmethod
    def split_with_separators(rng, text: str) -> str:
        """
        Splits text with a random separator.
        Examples: BJ -> B.J, B/J, B J, B-J, B'J
                 CSN -> C.S.N, C/S/N, C S N, C-S-N
        """
        seps = TextMutator.SEPARATORS
        sep = rng.choice(seps)
        return sep.join(list(text))

    # =====================================================================
    # CATEGORY 2: WORD-LEVEL MUTATIONS (Low Probabilities)
    # =====================================================================

    @staticmethod
    def maybe_style_word(rng, word: str, obf_p=0.025, noise_p=0.018, case_p=0.12) -> str:
        """
        RARE/LIGHT word styling for negative examples.
        Teaches model that obfuscation can exist in normal messages too.
        
        Default probabilities are very low (2.5% obf, 1.8% noise, 12% case).
        """
        out = str(word)
        if rng.random() < case_p:
            out = TextMutator.random_case(rng, out)
        if rng.random() < obf_p:
            out = TextMutator.obfuscate_word(rng, out, p=0.10)
        if rng.random() < noise_p:
            out = TextMutator.insert_noise_between_chars(rng, out)
        return out

    @staticmethod
    def style_bid_token(rng, token: str, obf_p=0.08, noise_p=0.04, case_p=0.25) -> str:
        """
        LOW-probability styling for BASE_BIDS tokens (used in negative examples).
        Teaches model that token/noise alone ≠ casino ad.
        
        Default probabilities: 8% obf, 4% noise, 25% case.
        """
        out = token
        if rng.random() < case_p:
            out = TextMutator.random_case(rng, out)
        if rng.random() < obf_p:
            out = TextMutator.obfuscate_word(rng, out, p=0.12)
        if rng.random() < noise_p:
            out = TextMutator.insert_noise_between_chars(rng, out)
        return out

    @staticmethod
    def style_token(rng, token: str, obf_p=0.14, noise_p=0.08, case_p=0.30) -> str:
        """
        MEDIUM-probability combined styling (used in positive examples).
        Combines random_case, obfuscate_word, and insert_noise_between_chars.
        
        Default probabilities: 14% obf, 8% noise, 30% case.
        """
        out = str(token)
        if rng.random() < case_p:
            out = TextMutator.random_case(rng, out)
        if rng.random() < obf_p:
            out = TextMutator.obfuscate_word(rng, out, p=0.14)
        if rng.random() < noise_p:
            out = TextMutator.insert_noise_between_chars(rng, out)
        return out

    @staticmethod
    def style_bid_variants(rng, bid: str) -> str:
        """
        Apply one of 5 bid styling modes:
        - plain: No styling
        - case: Apply random_case
        - obf: Apply obfuscate_word
        - noise: Apply insert_noise_between_chars
        - comboish: Apply style_token with custom params
        """
        from helper import weighted
        b = str(bid)
        mode = rng.choice(weighted([
            ("plain", 45),
            ("case", 15),
            ("obf", 15),
            ("noise", 10),
            ("comboish", 15),
        ]))
        if mode == "case":
            b = TextMutator.random_case(rng, b)
        elif mode == "obf":
            b = TextMutator.obfuscate_word(rng, b, p=0.18)
        elif mode == "noise":
            b = TextMutator.insert_noise_between_chars(rng, b)
        elif mode == "comboish":
            b = TextMutator.style_token(rng, b, obf_p=0.12, noise_p=0.04, case_p=0.35)
        return b

    @staticmethod
    def style_bid_light(rng, bid: str) -> str:
        """
        Lighter version of bid styling.
        First applies style_bid_variants, then sometimes adds additional styling.
        """
        b = TextMutator.style_bid_variants(rng, bid)
        if rng.random() < 0.35:
            b = TextMutator.style_token(rng, b, obf_p=0.08, noise_p=0.04, case_p=0.22)
        return b

    @staticmethod
    def style_world(rng, world: str) -> str:
        """
        World name styling with rare obfuscation and case changes.
        - 18% chance of case change
        - 6% chance of obfuscation
        """
        w = str(world)
        if rng.random() < 0.18:
            w = TextMutator.random_case(rng, w)
        if rng.random() < 0.06:
            w = TextMutator.obfuscate_word(rng, w, p=0.10)
        return w

    @staticmethod
    def casino_word_variant(rng) -> str:
        """
        Casino/CSN word variants with light styling.
        Teaches model that obfuscated casino discussion ≠ automatically casino ad.
        
        Variants include: casino, casinos, csn, c s n, c-a-s-i-n-o, c4sino, cas1no, gamble, gambling
        """
        from helper import weighted
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

    @staticmethod
    def random_gibberish_word(rng, min_len=6, max_len=16) -> str:
        """
        Generates random gibberish words (negative examples for nonsense/keyboard smash).
        Three modes:
        - keyboard: Keyboard smash pattern (45% weight)
        - random: Random consonant-heavy strings (35% weight)
        - repeat: Repeated character (20% weight)
        """
        from helper import weighted
        length = rng.randint(min_len, max_len)
        QWERTY_CHARS = "qwertyuiopasdfghjklzxcvbnm"
        
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
        else:  # random
            letters = "abcdefghijklmnopqrstuvwxyz"
            out = []
            for i in range(length):
                if i % 3 == 0:
                    out.append(rng.choice(letters))
                else:
                    out.append(rng.choice(letters + "sjdkfghqwermn"))
            return "".join(out)

    # =====================================================================
    # CATEGORY 3: PHRASE/LINE-LEVEL MUTATIONS
    # =====================================================================

    @staticmethod
    def maybe_style_phrase(rng, text: str, p_word=0.06) -> str:
        """
        Applies word-level styling to individual words in a phrase.
        Each word has p_word probability of being styled.
        Default: 6% of words get styled.
        """
        parts = str(text).split(" ")
        out = []
        for part in parts:
            if rng.random() < p_word:
                out.append(TextMutator.maybe_style_word(rng, part))
            else:
                out.append(part)
        return " ".join(out)

    @staticmethod
    def maybe_noisy_line(rng, text: str, line_p=0.075, p_word=0.08) -> str:
        """
        Applies phrase-level styling to entire lines.
        ~7.5% of lines get some normal-user weirdness.
        
        Args:
            rng: Random number generator
            text: Text line to style
            line_p: Probability line gets styled (default: 7.5%)
            p_word: Probability each word gets styled if line is styled (default: 8%)
        """
        if rng.random() < line_p:
            text = TextMutator.maybe_style_phrase(rng, text, p_word=p_word)
        return text

    # =====================================================================
    # CATEGORY 4: UTILITY FUNCTIONS
    # =====================================================================

    @staticmethod
    def normalize_for_filter(text: str) -> str:
        """
        Normalizes text for contamination filtering.
        - Converts to lowercase
        - Applies leet table (0->o, 1->i, etc.)
        - Removes all non-alphanumeric characters
        """
        import re
        low = str(text).lower().translate(TextMutator.LEET_TABLE)
        compact = re.sub(r"[^a-z0-9]+", "", low)
        return compact

    @staticmethod
    def clean_text(text: str, max_len=140) -> str:
        """
        Cleans text by:
        - Converting to string
        - Replacing newlines/carriage returns with spaces
        - Collapsing multiple whitespace to single space
        - Trimming to max_len and stripping whitespace
        """
        import re
        text = str(text)
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_len].strip()

    @staticmethod
    def collapse_whitespace(text: str) -> str:
        """
        Collapses excessive whitespace (3+ spaces/tabs) to 2 spaces.
        """
        import re
        text = re.sub(r"[ \t]{3,}", "  ", text)
        return text.strip()
    
    def clean_generated_text(text: str) -> str:
      # Collapse excessive whitespace, but keep some weird spacing possible
      text = re.sub(r"[ \t]{3,}", "  ", text)
      return text.strip()