import re
from typing import Pattern

COLOR_TAG_RE: Pattern = re.compile(r"`[0-9!@#$^&wopbqertasc]")
BRACKETS_MAP = {
    '[': '(',
    ']': ')',
    '{': '(',
    '}': ')',
    '<': '(',
    '>': ')'
}


def _replace_brackets(match: re.Match) -> str:
    ch = match.group(0)
    return BRACKETS_MAP.get(ch, ch)

def color_tag_remover(text: str) -> str:
    """Remove Growtopia-style color tags from text.

    Color tags are a backtick followed by a single character (digit or letter).
    We remove those sequences entirely. Also remove any stray backticks.
    """
    if not text:
        return text
    # First remove explicit tags like `0 `a etc.
    text = COLOR_TAG_RE.sub('', text)
    # Remove any remaining backticks
    text = text.replace('`', '')
    return text


def text_normalize(text: str) -> str:
    """Normalize text:

    Steps:
    1. Lowercase and strip
    2. Remove color tags
    3. Replace bracket variants with standard parentheses
    4. Remove a small set of 'useless' symbols (like '=') but keep common punctuation
    5. Collapse multiple spaces to one
    """
    if text is None:
        return ''
    # 1. Lowercase and strip
    s = text.lower().strip()

    # 2. Remove color tags
    s = color_tag_remover(s)

    # 4. Replace bracket-like chars with parentheses
    s = re.sub(r"[][{}<>]", _replace_brackets, s)

    # 5. Remove useless symbols. Keep alphanum, whitespace, basic punctuation and parentheses and hyphen/underscore/colon/slash
    # We'll remove equal signs and backslashes, plus sequences of unexpected punctuation
    s = re.sub(r"[=\\]", ' ', s)

    # Remove any characters that are not allowed (keep a conservative set)
    s = re.sub(r"[^a-z0-9\s\-_:/.(),()\(]", '', s)

    # 6. Collapse whitespace
    s = re.sub(r"\s+", ' ', s).strip()

    # 7. Remove word until whitespace if s starts with /
    if s.startswith('/'):
        s = s.split(' ', 1)[1] if ' ' in s else ''

    # (no link masking/restore step — links are left as-found)
    return s
