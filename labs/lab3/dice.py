from __future__ import annotations

import random


class Dice:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._random = random.Random()
        return cls._instance

    def reseed(self, seed: int) -> None:
        self._random.seed(seed)

    def roll(self, low: int, high: int) -> int:
        return self._random.randint(low, high)

    def chance(self, probability: float) -> bool:
        if not 0 <= probability <= 1:
            raise ValueError("Вероятность должна быть от 0 до 1")
        return self._random.random() < probability

    def pick(self, values):
        return self._random.choice(values)
