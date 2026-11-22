import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from labs.lab3.enemies import ArmoredEnemy, Goblin, HauntedWeapon, LegendaryEnemy, WindfuryEnemy
from labs.lab3.events import AchievementTracker, EventPublisher, ExpeditionJournal, GameEvent
from labs.lab3.hero import HeroBuilder
from labs.lab3.items import create_catalog
from labs.lab3.tactics import AggressiveTactic, BalancedTactic, CautiousTactic


class DecoratorTests(unittest.TestCase):
    def test_every_nested_decorator_participates(self):
        base = Mock()
        base.name, base.health = "Гоблин", 40
        base.roll_damage.return_value = 10
        base.receive_hit.return_value = 16
        enemy = ArmoredEnemy(WindfuryEnemy(LegendaryEnemy(base)))
        with patch("labs.lab3.enemies.Dice") as dice:
            dice.return_value.chance.return_value = True
            self.assertEqual(enemy.roll_damage(), 30)
        self.assertEqual(base.roll_damage.call_count, 2)
        self.assertEqual(enemy.receive_hit(20), 16)
        base.receive_hit.assert_called_once_with(16)
        self.assertEqual(enemy.name, "Бронированный Стремительный Легендарный Гоблин")
        self.assertEqual(enemy.health, 40)

    def test_decorated_enemy_uses_original_health(self):
        base = Goblin()
        enemy = ArmoredEnemy(base)
        self.assertEqual(enemy.receive_hit(20), 16)
        self.assertEqual(base.health, 24)
        self.assertEqual(enemy.health, 24)


class AdapterTests(unittest.TestCase):
    def test_weapon_can_fight_through_adapter(self):
        weapon = create_catalog().create("sword")
        enemy = HauntedWeapon(weapon)
        with patch.object(weapon, "roll_damage", return_value=17) as roll:
            self.assertEqual(enemy.roll_damage(), 17)
            roll.assert_called_once_with()
        self.assertEqual(enemy.receive_hit(-5), 0)
        self.assertEqual(enemy.receive_hit(100), 70)
        self.assertFalse(enemy.is_alive())
        self.assertEqual(weapon.damage, 16)


class StrategyTests(unittest.TestCase):
    def test_aggressive_trades_defense_for_attack(self):
        hero = HeroBuilder().build()
        normal = BalancedTactic().choose(hero, 2)
        aggressive = AggressiveTactic().choose(hero, 2)
        self.assertGreater(aggressive.attack, normal.attack)
        self.assertGreater(aggressive.incoming, normal.incoming)

    def test_cautious_heals_only_when_needed_and_possible(self):
        hero = HeroBuilder().build()
        tactic = CautiousTactic()
        self.assertFalse(tactic.choose(hero, 2).heal)
        hero.health = 10
        self.assertTrue(tactic.choose(hero, 2).heal)
        self.assertFalse(tactic.choose(hero, 0).heal)


class ObserverTests(unittest.TestCase):
    def test_all_subscribers_are_notified_once(self):
        publisher = EventPublisher()
        first, second = Mock(), Mock()
        publisher.subscribe(first)
        publisher.subscribe(first)
        publisher.subscribe(second)
        event = GameEvent(None, None)
        publisher.publish(event)
        first.on_event.assert_called_once_with(event)
        second.on_event.assert_called_once_with(event)
        publisher.unsubscribe(first)
        publisher.publish(event)
        self.assertEqual(first.on_event.call_count, 1)
        self.assertEqual(second.on_event.call_count, 2)

    def test_achievements_do_not_repeat_and_journal_records_losses(self):
        hero = HeroBuilder().build()
        report = SimpleNamespace(location="Изумрудная жила", seed=1,
                                 battle=SimpleNamespace(won=True))
        tracker, journal = AchievementTracker(), ExpeditionJournal()
        for _ in range(2):
            tracker.on_event(GameEvent(hero, report))
        self.assertEqual(hero.achievements, ["Первая находка", "Хозяин изумрудной жилы"])
        report.battle.won = False
        tracker.on_event(GameEvent(hero, report))
        journal.on_event(GameEvent(hero, report))
        self.assertEqual(len(hero.achievements), 2)
        self.assertIn("отступление", journal.entries[0])
