from pathlib import Path
from tempfile import TemporaryDirectory

from labs.lab3.defense import ArmorHandler, BarrierHandler, EvasionHandler
from labs.lab3.dice import Dice
from labs.lab3.enemies import ArmoredEnemy, Goblin, HauntedWeapon, LegendaryEnemy, WindfuryEnemy
from labs.lab3.game import GameFacade
from labs.lab3.hero import HeroBuilder
from labs.lab3.items import create_catalog
from labs.lab3.storage import CachingHeroRepository, FileHeroRepository
from labs.lab3.tactics import AggressiveTactic, BalancedTactic, CautiousTactic


def main():
    Dice().reseed(2026)
    catalog = create_catalog()
    weapon = catalog.create("sword")
    enemy = HauntedWeapon(weapon)
    print(f"Adapter: {weapon.name} стал врагом: {enemy.name}, HP {enemy.health}")

    elite = ArmoredEnemy(WindfuryEnemy(LegendaryEnemy(Goblin())))
    print(f"Decorator: {elite.name}, атака {elite.roll_damage()}, получил {elite.receive_hit(20)} урона")

    hero = HeroBuilder().build()
    hero.health = 20
    for tactic in (BalancedTactic(), AggressiveTactic(), CautiousTactic()):
        print(f"Strategy: {type(tactic).__name__} -> {tactic.choose(hero, 2)}")

    evasion = EvasionHandler(0)
    barrier = BarrierHandler(5)
    evasion.set_next(ArmorHandler(0.20)).set_next(barrier)
    print(f"Chain: 20 -> уклонение 0% -> броня 20% -> барьер 5 -> {evasion.handle(20)}")

    with TemporaryDirectory() as directory:
        repository = CachingHeroRepository(FileHeroRepository(Path(directory) / "heroes.json"))
        repository.save(hero)
        print("Proxy: герой через кэш ->", repository.find_by_name(hero.name).name)
        game = GameFacade(repository=repository)
        game.load(hero.name)
        report = game.explore("forest", seed=2026)
        print(f"Facade: экспедиция одним вызовом, победа -> {report.battle.won}")
        print("Observer, достижения:", game.hero.achievements)
        print("Observer, журнал:", game.journal.entries)


if __name__ == "__main__":
    main()
