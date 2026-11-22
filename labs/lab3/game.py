from __future__ import annotations

from pathlib import Path

from .events import AchievementTracker, EventPublisher, ExpeditionJournal, GameEvent
from .hero import HeroBuilder
from .items import Gem, create_catalog
from .storage import CachingHeroRepository, FileHeroRepository
from .tactics import TACTICS
from .world import locations


class GameFacade:
    def __init__(self, path=Path("data/heroes.json"), repository=None):
        self.catalog = create_catalog()
        self.repository = repository if repository is not None else CachingHeroRepository(FileHeroRepository(path))
        self.hero = None
        self.events = EventPublisher()
        self.journal = ExpeditionJournal()
        self.events.subscribe(AchievementTracker())
        self.events.subscribe(self.journal)

    def active_hero(self):
        if self.hero is None:
            raise ValueError("Сначала создайте или загрузите героя")
        return self.hero

    def new_hero(self, name: str, hero_class: str):
        if self.repository.find_by_name(name.strip()) is not None:
            raise ValueError("Такой герой уже сохранён. Загрузите его или выберите другое имя")
        self.hero = HeroBuilder(self.catalog).set_name(name).set_class(hero_class).build()
        self.journal.entries.clear()
        return self.hero

    def explore(self, location: str, tactic="balanced", seed=2026):
        if location not in locations() or tactic not in TACTICS:
            raise ValueError("Неизвестная локация или тактика")
        hero = self.active_hero()
        report = locations()[location].explore(hero, self.catalog, seed, TACTICS[tactic](), elite=True)
        self.events.publish(GameEvent(hero, report))
        return report

    def sell_gems(self) -> int:
        hero = self.active_hero()
        gems = [item for item in hero.inventory if isinstance(item, Gem)]
        total = sum(gem.price for gem in gems)
        hero.inventory = [item for item in hero.inventory if not isinstance(item, Gem)]
        hero.gold += total
        return total

    def enchant_weapon(self, index: int) -> str:
        hero = self.active_hero()
        if not 0 <= index < len(hero.inventory):
            raise ValueError("Нет предмета с таким номером")
        gem = hero.inventory[index]
        if not isinstance(gem, Gem):
            raise ValueError("Для зачарования нужен камень")
        if len(hero.weapon.enchantments) >= 3:
            raise ValueError("В оружии уже три камня")
        hero.weapon.enchantments.append(gem.name)
        hero.inventory.pop(index)
        return f"{gem.name} закреплён в оружии. Урон вырос на 2."

    def save(self) -> None:
        self.repository.save(self.active_hero())

    def load(self, name: str):
        hero = self.repository.find_by_name(name)
        if hero is None:
            raise ValueError("Нет такого сохранения")
        self.hero = hero
        self.journal.entries.clear()
        return hero
