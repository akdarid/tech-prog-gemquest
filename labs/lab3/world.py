from abc import ABC, abstractmethod
from dataclasses import dataclass

from .battle import BattleReport, fight
from .dice import Dice
from .enemies import (ArmoredEnemy, Dragon, Enemy, Goblin, HauntedWeapon,
                      LegendaryEnemy, Skeleton, WindfuryEnemy)
from .items import create_catalog


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

    def explore(self, hero, catalog, seed: int, tactic=None, elite=False) -> ExpeditionReport:
        Dice().reseed(seed)
        hero.rest()
        enemy = self.create_enemy()
        if elite:
            for decorator in (LegendaryEnemy, ArmoredEnemy, WindfuryEnemy):
                if Dice().chance(0.25):
                    enemy = decorator(enemy)
        enemy_name = enemy.name
        result = fight(hero, enemy, tactic)
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


class HauntedManor(Location):
    name = "Заброшенная мастерская"
    gold, experience = 50, 100
    loot_codes = ("moonstone", "sapphire")

    def create_enemy(self) -> Enemy:
        return HauntedWeapon(create_catalog().create("sword"))


def locations():
    return {"forest": Forest(), "crypt": Crypt(), "manor": HauntedManor(), "dragon": DragonLair()}
