from dataclasses import dataclass


@dataclass
class BattleReport:
    won: bool
    rounds: int
    log: list[str]


def fight(hero, enemy) -> BattleReport:
    log = []
    for turn in range(1, 201):
        taken = enemy.receive_hit(hero.roll_damage())
        log.append(f"{hero.name} наносит {taken}. У врага {enemy.health} HP.")
        if not enemy.is_alive():
            return BattleReport(True, turn, log)
        taken = hero.receive_hit(enemy.roll_damage())
        log.append(f"{enemy.name} наносит {taken}. У героя {hero.health} HP.")
        if not hero.is_alive():
            return BattleReport(False, turn, log)
    return BattleReport(False, 200, log + ["Бой затянулся. Герой отступил."])
