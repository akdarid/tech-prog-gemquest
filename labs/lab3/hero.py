from __future__ import annotations

from .items import Item, MageKitFactory, RangerKitFactory, WarriorKitFactory, create_catalog
from .defense import ArmorHandler, BarrierHandler, EvasionHandler


HERO_CLASSES = {
    "warrior": ("Воин", 120, WarriorKitFactory),
    "ranger": ("Следопыт", 100, RangerKitFactory),
    "mage": ("Маг", 85, MageKitFactory),
}


class Hero:
    def __init__(self, name: str, hero_class: str, level: int, kit):
        self.name = name
        self.hero_class = hero_class
        self.level = level
        self.experience = 0
        self.gold = 50
        self.weapon = kit.create_weapon()
        self.armor = kit.create_armor()
        self.inventory: list[Item] = []
        self.achievements: list[str] = []
        self.rest()

    @property
    def max_health(self) -> int:
        return HERO_CLASSES[self.hero_class][1] + (self.level - 1) * 15

    def is_alive(self) -> bool:
        return self.health > 0

    def roll_damage(self) -> int:
        return self.weapon.roll_damage() + (self.level - 1) * 3

    def receive_hit(self, amount: int) -> int:
        damage = self._defense.handle(amount)
        taken = min(self.health, damage)
        self.health -= taken
        return taken

    def rest(self) -> None:
        self.health = self.max_health
        armor = ArmorHandler(self.armor.defense)
        self._defense = armor
        if self.hero_class == "ranger" or (self.hero_class == "mage" and self.level >= 3):
            self._defense = EvasionHandler(0.15 if self.hero_class == "ranger" else 0.10)
            self._defense.set_next(armor)
        if self.hero_class == "mage":
            armor.set_next(BarrierHandler(30))
        elif self.hero_class == "warrior" and self.level >= 3:
            armor.set_next(BarrierHandler(20))
        elif self.hero_class == "ranger" and self.level >= 5:
            armor.set_next(BarrierHandler(15))

    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1


class HeroBuilder:
    def __init__(self, catalog=None):
        self._catalog = catalog or create_catalog()
        self._name = "Мастер"
        self._hero_class = "warrior"
        self._level = 1

    def set_name(self, name: str):
        self._name = name.strip()
        return self

    def set_class(self, hero_class: str):
        self._hero_class = hero_class
        return self

    def set_level(self, level: int):
        self._level = level
        return self

    def build(self) -> Hero:
        if not 1 <= len(self._name) <= 20:
            raise ValueError("Имя должно содержать от 1 до 20 символов")
        if self._hero_class not in HERO_CLASSES:
            raise ValueError("Неизвестный класс героя")
        if self._level < 1:
            raise ValueError("Уровень должен быть положительным")
        kit = HERO_CLASSES[self._hero_class][2](self._catalog)
        return Hero(self._name, self._hero_class, self._level, kit)
