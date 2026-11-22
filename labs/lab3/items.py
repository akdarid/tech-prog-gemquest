from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field

from .dice import Dice


@dataclass
class Item:
    code: str
    name: str
    price: int
    enchantments: list[str] = field(default_factory=list)

    def clone(self):
        return deepcopy(self)


@dataclass
class Gem(Item):
    carats: float = 1.0
    cut: str = "круг"

    def __str__(self):
        return f"{self.name}, {self.carats:.2f} ct, {self.cut}"


@dataclass
class Weapon(Item):
    damage: int = 10

    def roll_damage(self) -> int:
        base = self.damage + 2 * len(self.enchantments)
        return Dice().roll(max(1, base - 2), base + 2)


@dataclass
class Armor(Item):
    defense: float = 0.15


class ItemCatalog:
    def __init__(self):
        self._items = {}

    def register(self, item: Item) -> None:
        self._items[item.code] = item.clone()

    def create(self, code: str) -> Item:
        if code not in self._items:
            raise ValueError(f"Нет предмета: {code}")
        return self._items[code].clone()


def create_catalog() -> ItemCatalog:
    catalog = ItemCatalog()
    for item in (
        Weapon("sword", "Меч с гранатом", 80, damage=16),
        Weapon("bow", "Лук с турмалином", 80, damage=18),
        Weapon("staff", "Посох с лунным камнем", 80, damage=20),
        Armor("plate", "Доспех с ониксом", 60, defense=0.30),
        Armor("leather", "Кожаная броня", 60, defense=0.20),
        Armor("robe", "Мантия с сапфиром", 60, defense=0.10),
        Gem("garnet", "Гранат", 30, carats=2.85, cut="кушон"),
        Gem("moonstone", "Лунный камень", 35, carats=6.20, cut="кабошон"),
        Gem("sapphire", "Сапфир", 60, carats=1.80, cut="овал"),
        Gem("emerald", "Изумруд", 150, carats=6.00, cut="изумрудная"),
    ):
        catalog.register(item)
    return catalog


class StarterKitFactory(ABC):
    def __init__(self, catalog: ItemCatalog):
        self.catalog = catalog

    @abstractmethod
    def create_weapon(self) -> Weapon: ...

    @abstractmethod
    def create_armor(self) -> Armor: ...


class WarriorKitFactory(StarterKitFactory):
    def create_weapon(self) -> Weapon:
        return self.catalog.create("sword")

    def create_armor(self) -> Armor:
        return self.catalog.create("plate")


class RangerKitFactory(StarterKitFactory):
    def create_weapon(self) -> Weapon:
        return self.catalog.create("bow")

    def create_armor(self) -> Armor:
        return self.catalog.create("leather")


class MageKitFactory(StarterKitFactory):
    def create_weapon(self) -> Weapon:
        return self.catalog.create("staff")

    def create_armor(self) -> Armor:
        return self.catalog.create("robe")
