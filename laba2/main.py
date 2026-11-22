"""Лаба 2. Тетевин Матвей Вадимович, БИВТ-25-4-4.

Запуск: python main.py
"""

from abc import ABC, abstractmethod
from typing import Optional


class Pet(ABC):
    @abstractmethod
    def express(self) -> None:
        pass

    @abstractmethod
    def getName(self) -> str:
        pass

    @abstractmethod
    def getAge(self) -> int:
        pass

    @abstractmethod
    def getAgeInHumanYears(self) -> int:
        pass


class Animal(Pet):
    def __init__(self, name: str, age: int) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Кличка не должна быть пустой")
        if type(age) is not int or age < 0:
            raise ValueError("Возраст должен быть целым неотрицательным числом")
        self.__name = name
        self.__age = age

    def getName(self) -> str:
        return self.__name

    def getAge(self) -> int:
        return self.__age

    def happyBirthday(self) -> None:
        self.__age += 1


class Parrot(Animal):
    def getAgeInHumanYears(self) -> int:
        return self.getAge() * 5

    def express(self) -> None:
        print(f'{self.getName()}: "Hello!"')
        print("   \\\n   (o>\n\\\\_//)\n \\_/_)\n  _|_")


class Turtle(Animal):
    def getAgeInHumanYears(self) -> int:
        age = self.getAge()
        if age == 0:
            return 0
        return 15 + (age - 1) * 2

    def express(self) -> None:
        print("  _____     ____\n /      \\  |  o |\n|        |/ ___\\|\n|_________/\n|_|_| |_|_|")


class Person:
    def __init__(self, name: str, pet: Optional[Pet] = None) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Имя не должно быть пустым")
        self.__name = name
        self.__pet = pet

    def setPet(self, pet: Optional[Pet]) -> None:
        self.__pet = pet

    def getPetInfo(self) -> None:
        print("--------------------")
        pet = self.__pet
        if pet is None:
            print(f"{self.__name} has no pet yet")
        else:
            print(f"Pet for {self.__name} is named {pet.getName()}")
            print(f"Age: {pet.getAge()} year(s), about {pet.getAgeInHumanYears()} human years")
            print("And it expresses itself like this:")
            pet.express()
        print("--------------------")


def main() -> None:
    kesha = Parrot("Kesha", 2)
    zavala = Turtle("Zavala", 4)
    kesha.happyBirthday()

    jack = Person("Jack", kesha)
    john = Person("John")
    jack.getPetInfo()
    john.getPetInfo()
    john.setPet(zavala)
    john.getPetInfo()


if __name__ == "__main__":
    main()
