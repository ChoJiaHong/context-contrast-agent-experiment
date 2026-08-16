import re
from collections.abc import Iterable
from typing import Protocol


class SecondaryMatcher(Protocol):
    """Optional embedding or external-judge matcher used only as a secondary score."""

    def similarity(self, predicted: str, expected: str) -> float: ...

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


def secondary_matches(
    predicted: Iterable[str],
    expected: Iterable[str],
    matcher: SecondaryMatcher,
    threshold: float = 0.8,
) -> list[tuple[str, str, float]]:
    """Return best above-threshold semantic pairs without changing primary scoring."""
    available = list(expected)
    matches: list[tuple[str, str, float]] = []
    for candidate in predicted:
        scored = [(target, matcher.similarity(candidate, target)) for target in available]
        if not scored:
            continue
        target, score = max(scored, key=lambda item: item[1])
        if score >= threshold:
            matches.append((candidate, target, score))
            available.remove(target)
    return matches
