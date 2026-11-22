from .hero import HERO_CLASSES, HeroBuilder
from .items import Gem, create_catalog
from .world import locations


def print_report(report):
    print(f"\n{report.location}. Враг: {report.enemy}. Сид: {report.seed}")
    print("\n".join(report.battle.log))
    print("Победа!" if report.battle.won else "Пришлось отступить.")
    print(f"Золото: {report.gold:+}")
    if report.loot:
        print(f"Добыча: {report.loot}")


def main():
    catalog = create_catalog()
    print("Камни и драконы. Лаба 3")
    print("Все цены в игре условные. Цель — победить дракона изумрудной жилы.")
    name = input("Имя героя [Мастер]: ").strip() or "Мастер"
    print("Классы: " + ", ".join(f"{k} — {v[0]}" for k, v in HERO_CLASSES.items()))
    hero_class = input("Класс [warrior]: ").strip() or "warrior"
    hero = HeroBuilder(catalog).set_name(name).set_class(hero_class).build()
    while True:
        print(f"\n{hero.name}: уровень {hero.level}, опыт {hero.experience}, золото {hero.gold}")
        print("forest / crypt / dragon — экспедиция; bag — камни; sell — продать камни; 0 — выход")
        command = input("> ").strip()
        if command == "0":
            return
        if command in locations():
            text = input("Сид [2026]: ").strip() or "2026"
            try:
                print_report(locations()[command].explore(hero, catalog, int(text)))
            except ValueError as error:
                print(error)
        elif command == "bag":
            print("\n".join(str(item) for item in hero.inventory) or "Пока пусто")
        elif command == "sell":
            gems = [item for item in hero.inventory if isinstance(item, Gem)]
            total = sum(item.price for item in gems)
            hero.gold += total
            hero.inventory = [item for item in hero.inventory if not isinstance(item, Gem)]
            print(f"Торговец заплатил {total} золотых.")
        else:
            print("Нет такой команды")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nДо встречи!")
    except ValueError as error:
        print(error)
