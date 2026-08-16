from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..schemas import MethodOutput


LIST_FIELDS = (
    "relevant_context_differences",
    "constraints",
    "resources",
    "assumption_changes",
    "cost_structure_changes",
    "essential_context_conditions",
)


def ordered_union(values: Iterable[Iterable[str]]) -> list[str]:
    """Return a stable union so loop aggregation is reproducible."""
    seen: set[str] = set()
    merged: list[str] = []
    for group in values:
        for item in group:
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged


def merge_outputs(outputs: list[MethodOutput], **updates: Any) -> MethodOutput:
    """Keep accumulated discoveries while taking scalar fields from the latest call."""
    if not outputs:
        raise ValueError("at least one method output is required")
    merged = {
        field: ordered_union(getattr(output, field) for output in outputs)
        for field in LIST_FIELDS
    }
    merged.update(updates)
    return outputs[-1].model_copy(update=merged)
