from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GameEvent:
    hero: object
    report: object


class Listener(Protocol):
    def on_event(self, event: GameEvent) -> None: ...


class EventPublisher:
    def __init__(self):
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def publish(self, event: GameEvent) -> None:
        for listener in tuple(self._listeners):
            listener.on_event(event)


class AchievementTracker:
    def on_event(self, event: GameEvent) -> None:
        if not event.report.battle.won:
            return
        unlocked = ["Первая находка"]
        if event.report.location == "Изумрудная жила":
            unlocked.append("Хозяин изумрудной жилы")
        for title in unlocked:
            if title not in event.hero.achievements:
                event.hero.achievements.append(title)


class ExpeditionJournal:
    def __init__(self):
        self.entries: list[str] = []

    def on_event(self, event: GameEvent) -> None:
        result = "победа" if event.report.battle.won else "отступление"
        self.entries.append(
            f"{event.hero.name}: {event.report.location}, {result}, сид {event.report.seed}"
        )
