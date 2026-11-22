from __future__ import annotations

from abc import ABC, abstractmethod

from .dice import Dice
from .defense import ArmorHandler


class Enemy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def health(self) -> int: ...

    @abstractmethod
    def roll_damage(self) -> int: ...

    @abstractmethod
    def receive_hit(self, amount: int) -> int: ...

    def is_alive(self) -> bool:
        return self.health > 0


class BasicEnemy(Enemy):
    def __init__(self, name: str, health: int, damage: int, defense=0.0):
        self._name = name
        self._health = health
        self.damage = damage
        self.defense = defense

    @property
    def name(self) -> str:
        return self._name

    @property
    def health(self) -> int:
        return self._health

    def roll_damage(self) -> int:
        return Dice().roll(max(1, self.damage - 2), self.damage + 2)

    def receive_hit(self, amount: int) -> int:
        damage = ArmorHandler(self.defense).handle(amount)
        taken = min(self._health, damage)
        self._health -= taken
        return taken


class Goblin(BasicEnemy):
    def __init__(self):
        super().__init__("Гоблин-старатель", 40, 8)


class Skeleton(BasicEnemy):
    def __init__(self):
        super().__init__("Скелет хранителя", 65, 12, 0.15)


class Dragon(BasicEnemy):
    def __init__(self):
        super().__init__("Дракон изумрудной жилы", 170, 24, 0.25)


class EnemyDecorator(Enemy):
    def __init__(self, wrapped: Enemy):
        self.wrapped = wrapped

    @property
    def name(self) -> str:
        return self.wrapped.name

    @property
    def health(self) -> int:
        return self.wrapped.health

    def roll_damage(self) -> int:
        return self.wrapped.roll_damage()

    def receive_hit(self, amount: int) -> int:
        return self.wrapped.receive_hit(amount)


class LegendaryEnemy(EnemyDecorator):
    @property
    def name(self) -> str:
        return "Легендарный " + self.wrapped.name

    def roll_damage(self) -> int:
        return int(self.wrapped.roll_damage() * 1.5)


class ArmoredEnemy(EnemyDecorator):
    @property
    def name(self) -> str:
        return "Бронированный " + self.wrapped.name

    def receive_hit(self, amount: int) -> int:
        return self.wrapped.receive_hit(ArmorHandler(0.20).handle(amount))


class WindfuryEnemy(EnemyDecorator):
    @property
    def name(self) -> str:
        return "Стремительный " + self.wrapped.name

    def roll_damage(self) -> int:
        first = self.wrapped.roll_damage()
        return first + self.wrapped.roll_damage() if Dice().chance(0.25) else first


class HauntedWeapon(Enemy):
    # У оружия нет здоровья и receive_hit: адаптер добавляет контракт противника.
    def __init__(self, weapon):
        self.weapon = weapon
        self._health = 70

    @property
    def name(self) -> str:
        return "Одержимый " + self.weapon.name

    @property
    def health(self) -> int:
        return self._health

    def roll_damage(self) -> int:
        return self.weapon.roll_damage()

    def receive_hit(self, amount: int) -> int:
        taken = min(self._health, max(0, amount))
        self._health -= taken
        return taken
