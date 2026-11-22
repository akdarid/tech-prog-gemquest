from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from .hero import Hero, HeroBuilder
from .items import Armor, Gem, Weapon, create_catalog


class HeroRepository(Protocol):
    def find_all(self) -> list[Hero]: ...

    def find_by_name(self, name: str) -> Hero | None: ...

    def save(self, hero: Hero) -> None: ...


def item_snapshot(item):
    return {"type": type(item).__name__, "fields": asdict(item)}


def restore_item(data):
    types = {"Gem": Gem, "Weapon": Weapon, "Armor": Armor}
    if data["type"] not in types:
        raise ValueError("Неизвестный тип предмета в сохранении")
    return types[data["type"]](**data["fields"])


def hero_snapshot(hero):
    return {
        "name": hero.name, "hero_class": hero.hero_class, "level": hero.level,
        "experience": hero.experience, "gold": hero.gold, "health": hero.health,
        "weapon": item_snapshot(hero.weapon), "armor": item_snapshot(hero.armor),
        "inventory": [item_snapshot(item) for item in hero.inventory],
        "achievements": list(hero.achievements),
    }


def restore_hero(data):
    hero = (HeroBuilder(create_catalog()).set_name(data["name"])
            .set_class(data["hero_class"]).set_level(data["level"]).build())
    hero.experience = data["experience"]
    hero.gold = data["gold"]
    hero.weapon = restore_item(data["weapon"])
    hero.armor = restore_item(data["armor"])
    hero.inventory = [restore_item(item) for item in data["inventory"]]
    hero.achievements = list(data["achievements"])
    hero.rest()
    hero.health = max(0, min(data["health"], hero.max_health))
    return hero


class FileHeroRepository:
    def __init__(self, path: Path):
        self.path = Path(path)

    def find_all(self) -> list[Hero]:
        if not self.path.exists():
            return []
        text = self.path.read_text(encoding="utf-8")
        if not text.strip():
            return []
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("Сохранение должно содержать список героев")
        return [restore_hero(row) for row in data]

    def find_by_name(self, name: str) -> Hero | None:
        return next((hero for hero in self.find_all() if hero.name == name), None)

    def save(self, hero: Hero) -> None:
        rows = [hero_snapshot(other) for other in self.find_all() if other.name != hero.name]
        rows.append(hero_snapshot(hero))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)


class CachingHeroRepository:
    def __init__(self, target: HeroRepository):
        self._target = target
        self._cache = None

    def _cached(self):
        if self._cache is None:
            self._cache = {hero.name: deepcopy(hero) for hero in self._target.find_all()}
        return self._cache

    def find_all(self) -> list[Hero]:
        return deepcopy(list(self._cached().values()))

    def find_by_name(self, name: str) -> Hero | None:
        return deepcopy(self._cached().get(name))

    def save(self, hero: Hero) -> None:
        self._target.save(hero)
        self._cached()[hero.name] = deepcopy(hero)
