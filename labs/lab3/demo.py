from .dice import Dice
from .hero import HeroBuilder
from .items import MageKitFactory, WarriorKitFactory, create_catalog
from .main import print_report
from .world import Crypt, Forest


def main():
    catalog = create_catalog()
    print("Singleton: Dice() is Dice() ->", Dice() is Dice())
    hero = HeroBuilder(catalog).set_name("Матвей").set_class("warrior").build()
    print(f"Builder: {hero.name}, {hero.hero_class}, уровень {hero.level}")
    for factory in (WarriorKitFactory(catalog), MageKitFactory(catalog)):
        print(f"Abstract Factory: {factory.create_weapon().name} + {factory.create_armor().name}")
    for location in (Forest(), Crypt()):
        print(f"Factory Method: {location.name} -> {location.create_enemy().name}")
    first = catalog.create("garnet")
    second = first.clone()
    second.enchantments.append("Огранка мастера")
    print(f"Prototype: {first}; разные объекты -> {first is not second}")
    print(f"Зачарования оригинала: {first.enchantments}, копии: {second.enchantments}")
    print_report(Forest().explore(hero, catalog, 2026))


if __name__ == "__main__":
    main()
