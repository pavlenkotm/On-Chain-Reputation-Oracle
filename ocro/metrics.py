"""Metric abstractions for OCRO scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class MetricResult:
    """Represents a single metric contributing to a score."""

    name: str
    value: float
    weight: float
    normalized_value: float


def normalize_value(value: float, max_value: float) -> float:
    """Normalize a raw value to the range [0, 1]."""

    if max_value <= 0:
        raise ValueError("max_value must be positive")
    normalized = max(0.0, min(1.0, value / max_value))
    return normalized


def aggregate_metrics(metrics: Iterable[MetricResult]) -> float:
    """Aggregate metrics into a weighted normalized score between 0 and 1."""

    metric_list: List[MetricResult] = list(metrics)
    total = 0.0
    for metric in metric_list:
        total += metric.normalized_value * metric.weight
    return max(0.0, min(1.0, total))


__all__ = ["MetricResult", "normalize_value", "aggregate_metrics"]
