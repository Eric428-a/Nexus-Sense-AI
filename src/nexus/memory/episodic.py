"""
Episodic memory.

Episodes represent completed investigations, agent runs,
decisions, observations, and significant system events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


@dataclass(slots=True)
class MemoryEpisode:
    """A completed experience or event."""

    id: str = field(default_factory=generate_id)
    episode_type: str = "generic"
    title: str = ""
    summary: str = ""
    outcome: str | None = None

    started_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None

    participants: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    context: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)

    def complete(self, outcome: str | None = None) -> None:
        self.completed_at = utc_now()

        if outcome is not None:
            self.outcome = outcome


class EpisodicMemory:
    """
    Stores historical system experiences.
    """

    def __init__(self) -> None:
        self._episodes: dict[str, MemoryEpisode] = {}

    async def record(
        self,
        *,
        episode_type: str,
        title: str,
        summary: str,
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEpisode:

        episode = MemoryEpisode(
            episode_type=episode_type,
            title=title,
            summary=summary,
            context=context or {},
            tags=tags or [],
        )

        self._episodes[episode.id] = episode
        return episode

    async def get(
        self,
        episode_id: str,
    ) -> MemoryEpisode | None:

        return self._episodes.get(episode_id)

    async def complete(
        self,
        episode_id: str,
        *,
        outcome: str | None = None,
    ) -> MemoryEpisode | None:

        episode = self._episodes.get(episode_id)

        if episode is None:
            return None

        episode.complete(outcome)
        return episode

    async def recent(
        self,
        limit: int = 20,
    ) -> list[MemoryEpisode]:

        episodes = list(self._episodes.values())

        episodes.sort(
            key=lambda item: item.started_at,
            reverse=True,
        )

        return episodes[:limit]

    async def count(self) -> int:
        return len(self._episodes)