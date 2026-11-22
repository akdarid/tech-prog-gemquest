from __future__ import annotations

from abc import ABC, abstractmethod

from .dice import Dice


class DamageHandler(ABC):
    def __init__(self):
        self._next = None

    def set_next(self, handler):
        self._next = handler
        return handler

    def handle(self, amount: int) -> int:
        remaining = self.reduce(max(0, amount))
        if remaining > 0 and self._next is not None:
            return self._next.handle(remaining)
        return remaining

    @abstractmethod
    def reduce(self, amount: int) -> int: ...


class EvasionHandler(DamageHandler):
    def __init__(self, probability: float):
        super().__init__()
        if not 0 <= probability <= 1:
            raise ValueError("Вероятность должна быть от 0 до 1")
        self.probability = probability

    def reduce(self, amount: int) -> int:
        return 0 if amount == 0 or Dice().chance(self.probability) else amount


class ArmorHandler(DamageHandler):
    def __init__(self, defense: float):
        super().__init__()
        if not 0 <= defense <= 0.8:
            raise ValueError("Броня поглощает от 0 до 80% урона")
        self.defense = defense

    def reduce(self, amount: int) -> int:
        return max(1, int(amount * (1 - self.defense) + 0.5)) if amount > 0 else 0


class BarrierHandler(DamageHandler):
    def __init__(self, strength: int):
        super().__init__()
        if strength < 0:
            raise ValueError("Прочность барьера не может быть отрицательной")
        self.strength = strength

    def reduce(self, amount: int) -> int:
        absorbed = min(self.strength, amount)
        self.strength -= absorbed
        return amount - absorbed
