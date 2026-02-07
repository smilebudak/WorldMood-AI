"""
SpikeDetector – identifies sudden mood shifts for a country by comparing the
latest mood_score against a rolling window.  Uses a simple z-score approach
that can later be replaced with an sklearn IsolationForest or similar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


SPIKE_Z_THRESHOLD = 2.0  # standard-deviations from rolling mean


@dataclass
class SpikeEvent:
    country_code: str
    previous_label: str
    new_label: str
    delta: float
    reason: str


def detect_spike(
    country_code: str,
    history_scores: list[float],
    history_labels: list[str],
    current_score: float,
    current_label: str,
    window: int = 7,
) -> Optional[SpikeEvent]:
    """Compare *current_score* against the last *window* scores.

    Returns a ``SpikeEvent`` if the change is statistically significant,
    otherwise ``None``.
    """

    if len(history_scores) < 3:
        return None  # not enough data

    recent = np.array(history_scores[-window:])
    mean = float(np.mean(recent))
    std = float(np.std(recent))

    if std == 0:
        return None

    z = abs(current_score - mean) / std
    delta = current_score - mean

    if z >= SPIKE_Z_THRESHOLD and current_label != history_labels[-1]:
        return SpikeEvent(
            country_code=country_code,
            previous_label=history_labels[-1],
            new_label=current_label,
            delta=round(delta, 4),
            reason=f"z-score {z:.2f} exceeds threshold {SPIKE_Z_THRESHOLD}",
        )

    return None


def detect_spikes_batch(
    country_histories: dict[str, list[dict]],
    current_moods: dict[str, dict],
) -> list[SpikeEvent]:
    """Run spike detection across all countries.

    Parameters
    ----------
    country_histories:
        ``{country_code: [{date, mood_score, mood_label}, ...]}``
    current_moods:
        ``{country_code: {mood_score, mood_label}}``
    """
    events: list[SpikeEvent] = []
    for cc, current in current_moods.items():
        hist = country_histories.get(cc, [])
        if not hist:
            continue
        scores = [h["mood_score"] for h in hist]
        labels = [h["mood_label"] for h in hist]
        evt = detect_spike(
            country_code=cc,
            history_scores=scores,
            history_labels=labels,
            current_score=current["mood_score"],
            current_label=current["mood_label"],
        )
        if evt:
            events.append(evt)
    return events
