"""
MoodEngine – computes a mood_score, mood_label, and color_code for a country
based on aggregated audio features and optional news sentiment.

The algorithm is intentionally rule-based so it works without a trained model,
but is structured so you can drop in an sklearn classifier later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


# ── Mood definitions ──────────────────────────────────────────────────────────

MOOD_MAP: dict[str, dict] = {
    "Happy":   {"range": (0.5, 1.0),   "color": "#22c55e", "emoji": "😊"},
    "Calm":    {"range": (0.15, 0.5),   "color": "#38bdf8", "emoji": "😌"},
    "Sad":     {"range": (-0.5, -0.15), "color": "#8b5cf6", "emoji": "😢"},
    "Angry":   {"range": (-1.0, -0.5),  "color": "#ef4444", "emoji": "😠"},
    "Anxious": {"range": (-0.5, 0.15),  "color": "#f97316", "emoji": "😰"},
}


@dataclass
class MoodResult:
    mood_score: float      # -1.0 … 1.0
    mood_label: str        # Happy | Calm | Sad | Angry | Anxious
    color_code: str        # hex
    emoji: str


def compute_mood(
    valence: float,
    energy: float,
    danceability: float = 0.5,
    acousticness: float = 0.5,
    news_sentiment: Optional[float] = None,
) -> MoodResult:
    """Return a ``MoodResult`` from audio features (0-1 scale) and optional
    news sentiment (-1 … 1).

    Scoring formula (weights sum to 1.0):
        base = 0.40 * valence
             + 0.20 * energy_component
             + 0.15 * danceability
             - 0.10 * acousticness
        If news_sentiment is provided it contributes 0.15 weight.
    """

    # Energy is bimodal: high energy + low valence → anger, otherwise positive
    energy_component = energy if valence >= 0.45 else -energy

    base = (
        0.40 * (valence * 2 - 1)           # remap 0-1 → -1…1
        + 0.20 * (energy_component * 2 - 1)
        + 0.15 * (danceability * 2 - 1)
        - 0.10 * (acousticness * 2 - 1)
    )

    if news_sentiment is not None:
        base = base * 0.85 + news_sentiment * 0.15

    mood_score = float(np.clip(base, -1.0, 1.0))

    label, color, emoji = _classify(mood_score, energy, valence)

    return MoodResult(
        mood_score=round(mood_score, 4),
        mood_label=label,
        color_code=color,
        emoji=emoji,
    )


def _classify(score: float, energy: float, valence: float) -> tuple[str, str, str]:
    """Map score to a mood label with energy-based disambiguation."""

    if score >= 0.5:
        key = "Happy"
    elif score >= 0.15:
        key = "Calm"
    elif score <= -0.5:
        key = "Angry"
    elif score <= -0.15:
        # Distinguish Sad vs Anxious by energy
        key = "Anxious" if energy > 0.55 else "Sad"
    else:
        # Neutral zone – lean on valence
        key = "Calm" if valence >= 0.45 else "Anxious"

    meta = MOOD_MAP[key]
    return key, meta["color"], meta["emoji"]


def batch_compute(rows: list[dict]) -> list[MoodResult]:
    """Vectorised convenience wrapper.  Each dict must contain at least
    ``valence`` and ``energy`` keys."""
    return [
        compute_mood(
            valence=r["valence"],
            energy=r["energy"],
            danceability=r.get("danceability", 0.5),
            acousticness=r.get("acousticness", 0.5),
            news_sentiment=r.get("news_sentiment"),
        )
        for r in rows
    ]
