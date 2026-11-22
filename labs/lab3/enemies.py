from __future__ import annotations

from abc import ABC, abstractmethod

from .dice import Dice


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
        damage = max(1, int(amount * (1 - self.defense) + 0.5)) if amount > 0 else 0
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
