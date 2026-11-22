from __future__ import annotations

from abc import ABC, abstractmethod


class Pet(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_age(self) -> int: ...

    @abstractmethod
    def get_age_in_human_years(self) -> int: ...

    @abstractmethod
    def express(self) -> str: ...


class Animal(Pet):
    def __init__(self, name: str, age: int):
        if not name.strip() or age < 0:
            raise ValueError("Нужны кличка и неотрицательный возраст")
        self._name = name.strip()
        self._age = age

    def get_name(self) -> str:
        return self._name

    def get_age(self) -> int:
        return self._age

    def happy_birthday(self) -> None:
        self._age += 1


class Parrot(Animal):
    def get_age_in_human_years(self) -> int:
        return self.get_age() * 5

    def express(self) -> str:
        return f'{self.get_name()}: «Привет!»'


class Turtle(Animal):
    def get_age_in_human_years(self) -> int:
        return 0 if self.get_age() == 0 else 15 + (self.get_age() - 1) * 2

    def express(self) -> str:
        return f"{self.get_name()} прячет голову в панцирь."


class Person:
    def __init__(self, name: str, pet: Pet | None = None):
        self.name = name
        self.pet = pet

    def get_pet_info(self) -> str:
        if self.pet is None:
            return f"У {self.name} пока нет питомца."
        return (
            f"{self.name}: питомец {self.pet.get_name()}\n"
            f"Возраст: {self.pet.get_age()}, в человеческих годах: "
            f"{self.pet.get_age_in_human_years()}\n{self.pet.express()}"
        )
