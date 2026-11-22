from abc import ABC, abstractmethod
from dataclasses import dataclass

from .battle import BattleReport, fight
from .dice import Dice
from .enemies import Dragon, Enemy, Goblin, Skeleton


@dataclass
class ExpeditionReport:
    location: str
    enemy: str
    battle: BattleReport
    gold: int
    loot: str
    seed: int


class Location(ABC):
    name = ""
    gold = 0
    experience = 0
    loot_codes = ()

    @abstractmethod
    def create_enemy(self) -> Enemy: ...

    def explore(self, hero, catalog, seed: int) -> ExpeditionReport:
        Dice().reseed(seed)
        hero.rest()
        enemy = self.create_enemy()
        enemy_name = enemy.name
        result = fight(hero, enemy)
        loot_name = ""
        gold = self.gold if result.won else -min(hero.gold, 10)
        hero.gold += gold
        if result.won:
            hero.gain_experience(self.experience)
            loot = catalog.create(Dice().pick(self.loot_codes))
            hero.inventory.append(loot)
            loot_name = str(loot)
        return ExpeditionReport(self.name, enemy_name, result, gold, loot_name, seed)


class Forest(Location):
    name = "Гранатовый лес"
    gold, experience = 20, 50
    loot_codes = ("garnet", "moonstone")

    def create_enemy(self) -> Enemy:
        return Goblin()


class Crypt(Location):
    name = "Сапфировая шахта"
    gold, experience = 35, 90
    loot_codes = ("sapphire", "garnet")

    def create_enemy(self) -> Enemy:
        return Skeleton()


class DragonLair(Location):
    name = "Изумрудная жила"
    gold, experience = 120, 200
    loot_codes = ("emerald",)

    def create_enemy(self) -> Enemy:
        return Dragon()


def locations():
    return {"forest": Forest(), "crypt": Crypt(), "dragon": DragonLair()}
