import re
from collections.abc import Iterable

def normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))

def canonical(value: str, aliases: dict[str, list[str]]) -> str:
    norm=normalize(value)
    for key, values in aliases.items():
        if norm in {normalize(key), *(normalize(v) for v in values)}:
            return normalize(key)
    return norm

def matched_sets(predicted: Iterable[str], expected: Iterable[str], aliases: dict[str, list[str]] | None=None) -> tuple[set[str], set[str]]:
    aliases=aliases or {}
    return ({canonical(x, aliases) for x in predicted}, {canonical(x, aliases) for x in expected})
