import re
import random

class GrammarGenerator:
    TOKEN_RE = re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")

    def __init__(self, rules=None, seed=None):
        self.rules = rules or {}
        self.rng = random.Random(seed)

    def add_rule(self, name, values):
        self.rules[name] = values

    def _pick(self, rule):
        # rule can be a list/tuple or a function
        if callable(rule):
            return rule(self.rng)
        return self.rng.choice(rule)

    def expand(self, template):
        def repl(match):
            token = match.group(1)
            if token not in self.rules:
                raise KeyError(f"Unknown token: {token}")

            value = self._pick(self.rules[token])

            # support recursive expansion
            if isinstance(value, str) and self.TOKEN_RE.search(value):
                return self.expand(value)

            return str(value)

        return self.TOKEN_RE.sub(repl, template)

    def generate(self, template, n=1):
        return [self.expand(template) for _ in range(n)]
