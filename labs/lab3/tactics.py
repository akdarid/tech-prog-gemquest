from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    attack: float = 1.0
    incoming: float = 1.0
    heal: bool = False


class Tactic(ABC):
    @abstractmethod
    def choose(self, hero, potions: int) -> Action: ...


class BalancedTactic(Tactic):
    def choose(self, hero, potions: int) -> Action:
        return Action()


class AggressiveTactic(Tactic):
    def choose(self, hero, potions: int) -> Action:
        return Action(attack=1.4, incoming=1.25)


class CautiousTactic(Tactic):
    def choose(self, hero, potions: int) -> Action:
        return Action(attack=0.8, incoming=0.7,
                      heal=hero.health < hero.max_health / 2 and potions > 0)


TACTICS = {
    "balanced": BalancedTactic,
    "aggressive": AggressiveTactic,
    "cautious": CautiousTactic,
}
