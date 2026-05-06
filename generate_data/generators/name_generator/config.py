from faker import Faker
import pyphen

ALPHA = "abcdefghijklmnopqrstuvwxyz"
ALNUM = "abcdefghijklmnopqrstuvwxyz0123456789"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"
VOWELS = "aeiou"

BASE_SYLLABLES = [
    "son", "dre", "wan", "flow", "lon", "van", "gap", "rud", "hey",
    "sha", "kar", "mir", "tok", "zen", "lok", "ran", "bel", "nor",
    "kam", "tur", "min", "rex", "ven", "dar", "lum", "pas", "zor",
    "fen", "cal", "mon", "gar", "yat", "pon", "ris", "tom", "mal",
    "he", "mo", "sa", "ter", "yo", "am", "af", "q", "x", "j",
    "neo", "lio", "mar", "sol", "arc", "vox", "val", "nim",
    "haze", "nova", "mira", "luma", "cyra", "kora", "nexa", "orin",
    "tora", "vexa", "daro", "sora", "zali", "riva", "keli", "faro",
    "hemo", "hes", "mosa", "tero", "yam", "melo", "zora", "xemo",
    "rivo", "nexo", "luno", "voro", "seno", "tavi", "lexo", "kimo",
]

FAKER = Faker("en_US")
PYPHEN_DICT = pyphen.Pyphen(lang="en")