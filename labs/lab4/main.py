import argparse
from pathlib import Path

from labs.lab3.game import GameFacade
from labs.lab3.hero import HERO_CLASSES
from labs.lab3.main import print_report


def main():
    parser = argparse.ArgumentParser(description="Камни и драконы")
    parser.add_argument("--save", type=Path, default=Path("data/heroes.json"), help="Файл сохранений")
    args = parser.parse_args()
    game = GameFacade(args.save)
    print("Камни и драконы. Лаба 4")
    print("Новая игра: new Имя warrior/ranger/mage; загрузка: load Имя; список: saves")
    print("Цель — победить дракона изумрудной жилы. Цены и свойства камней игровые.")
    while True:
        if game.hero is not None:
            hero = game.hero
            print(f"\n{hero.name}: {HERO_CLASSES[hero.hero_class][0]}, уровень {hero.level}, "
                  f"опыт {hero.experience}/{hero.level * 100}, HP {hero.health}/{hero.max_health}, золото {hero.gold}")
        print("go forest/crypt/manor/dragon [balanced/aggressive/cautious] [сид]")
        print("bag | sell | enchant Номер | stats | journal | save | load Имя | saves | new Имя Класс | 0")
        words = input("> ").strip().split()
        if not words:
            continue
        command, *values = words
        try:
            if command == "0":
                print("До встречи! Прогресс сохраняется командой save.")
                return
            if command == "new" and len(values) == 2:
                game.new_hero(*values)
            elif command == "load" and len(values) == 1:
                game.load(values[0])
                print("Герой загружен. Журнал текущего сеанса очищен.")
            elif command == "saves" and not values:
                print(", ".join(hero.name for hero in game.repository.find_all()) or "Сохранений нет")
            elif command == "go" and 1 <= len(values) <= 3:
                tactic = values[1] if len(values) >= 2 else "balanced"
                seed = int(values[2]) if len(values) == 3 else 2026
                print_report(game.explore(values[0], tactic, seed))
                print("Достижения:", ", ".join(game.hero.achievements) or "пока нет")
            elif command == "bag" and not values:
                hero = game.active_hero()
                print("\n".join(f"{i}. {item}, цена {item.price}" for i, item in enumerate(hero.inventory, 1)) or "Пусто")
            elif command == "sell" and not values:
                print(f"Продажа всех свободных камней: +{game.sell_gems()} золотых.")
            elif command == "enchant" and len(values) == 1:
                print(game.enchant_weapon(int(values[0]) - 1))
            elif command == "stats" and not values:
                hero = game.active_hero()
                print(f"{hero.weapon.name}, базовый урон {hero.weapon.damage}, камни: {hero.weapon.enchantments}")
                print(f"{hero.armor.name}, защита {hero.armor.defense:.0%}")
            elif command == "journal" and not values:
                print("\n".join(game.journal.entries) or "В этом сеансе экспедиций пока нет")
            elif command == "save" and not values:
                game.save()
                print("Герой сохранён.")
            else:
                print("Проверьте команду и число аргументов")
        except (ValueError, OSError, KeyError, TypeError) as error:
            print(f"Не получилось: {error}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nДо встречи! Прогресс сохраняется командой save.")
