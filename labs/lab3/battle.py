from dataclasses import dataclass

from .tactics import BalancedTactic


@dataclass
class BattleReport:
    won: bool
    rounds: int
    log: list[str]


def fight(hero, enemy, tactic=None) -> BattleReport:
    tactic = tactic or BalancedTactic()
    log = []
    potions = 2
    for turn in range(1, 201):
        action = tactic.choose(hero, potions)
        if action.heal:
            healed = min(hero.max_health - hero.health, hero.max_health // 3)
            hero.health += healed
            potions -= 1
            log.append(f"{hero.name} пьёт зелье: +{healed} HP.")
        else:
            taken = enemy.receive_hit(max(1, int(hero.roll_damage() * action.attack)))
            log.append(f"{hero.name} наносит {taken}. У врага {enemy.health} HP.")
        if not enemy.is_alive():
            return BattleReport(True, turn, log)
        taken = hero.receive_hit(max(1, int(enemy.roll_damage() * action.incoming)))
        log.append(f"{enemy.name} наносит {taken}. У героя {hero.health} HP.")
        if not hero.is_alive():
            return BattleReport(False, turn, log)
    return BattleReport(False, 200, log + ["Бой затянулся. Герой отступил."])
