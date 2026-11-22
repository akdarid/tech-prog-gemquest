import unittest
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from labs.lab3.game import GameFacade
from labs.lab3.hero import HeroBuilder
from labs.lab3.items import Gem, create_catalog
from labs.lab3.storage import HeroRepository, hero_snapshot
from labs.lab3.world import Forest


class GameTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "heroes.json"
        self.game = GameFacade(self.path)
        self.hero = self.game.new_hero("Матвей", "warrior")

    def test_full_session_finds_stone_enchants_and_loads(self):
        report = self.game.explore("forest", seed=2026)
        self.assertTrue(report.battle.won)
        self.assertIsInstance(self.hero.inventory[0], Gem)
        self.assertEqual(self.hero.achievements, ["Первая находка"])
        self.assertEqual(len(self.game.journal.entries), 1)
        self.game.enchant_weapon(0)
        self.assertEqual(self.hero.inventory, [])
        self.assertEqual(len(self.hero.weapon.enchantments), 1)
        self.game.save()
        other = GameFacade(self.path)
        loaded = other.load("Матвей")
        self.assertEqual(hero_snapshot(loaded), hero_snapshot(self.hero))

    def test_repeated_seed_reproduces_expedition(self):
        first = HeroBuilder().build()
        second = HeroBuilder().build()
        catalog = create_catalog()
        left = Forest().explore(first, catalog, 42, elite=True)
        right = Forest().explore(second, catalog, 42, elite=True)
        self.assertEqual(asdict(left), asdict(right))
        self.assertEqual(hero_snapshot(first), hero_snapshot(second))

    def test_sell_counts_only_free_gems(self):
        self.hero.inventory = [self.game.catalog.create("garnet"), self.game.catalog.create("sword")]
        self.assertEqual(self.game.sell_gems(), 30)
        self.assertEqual(self.hero.gold, 80)
        self.assertEqual([item.code for item in self.hero.inventory], ["sword"])
        self.assertEqual(self.game.sell_gems(), 0)

    def test_invalid_enchant_does_not_consume_items(self):
        self.hero.inventory = [self.game.catalog.create("sword")]
        for index in (-1, 0, 1):
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.game.enchant_weapon(index)
        self.assertEqual(len(self.hero.inventory), 1)
        self.hero.inventory = [self.game.catalog.create("garnet")]
        self.hero.weapon.enchantments = ["a", "b", "c"]
        with self.assertRaises(ValueError):
            self.game.enchant_weapon(0)
        self.assertEqual(len(self.hero.inventory), 1)

    def test_invalid_location_tactic_and_load_keep_state(self):
        before = hero_snapshot(self.hero)
        for location, tactic in [("unknown", "balanced"), ("forest", "unknown")]:
            with self.subTest(location=location, tactic=tactic), self.assertRaises(ValueError):
                self.game.explore(location, tactic)
        with self.assertRaises(ValueError):
            self.game.load("Нет")
        self.assertEqual(hero_snapshot(self.game.hero), before)

    def test_duplicate_name_does_not_overwrite_saved_hero(self):
        self.game.save()
        with self.assertRaises(ValueError):
            self.game.new_hero("Матвей", "mage")
        self.assertEqual(self.game.load("Матвей").hero_class, "warrior")

    def test_operations_need_active_hero(self):
        game = GameFacade(self.path)
        for operation in (game.save, game.sell_gems, lambda: game.explore("forest")):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                operation()

    def test_facade_uses_injected_repository(self):
        repository = Mock(spec=HeroRepository)
        repository.find_by_name.return_value = None
        game = GameFacade(repository=repository)
        hero = game.new_hero("Мастер", "mage")
        game.save()
        repository.save.assert_called_once_with(hero)


class ProgressTests(unittest.TestCase):
    def test_level_can_increase_several_times(self):
        hero = HeroBuilder().build()
        hero.gain_experience(350)
        self.assertEqual((hero.level, hero.experience), (3, 50))
        hero.rest()
        self.assertEqual(hero.health, 150)

    def test_barrier_recovers_in_camp(self):
        hero = HeroBuilder().set_class("mage").build()
        self.assertEqual(hero.receive_hit(20), 0)
        self.assertEqual(hero.receive_hit(20), 6)
        hero.rest()
        self.assertEqual(hero.receive_hit(20), 0)

    def test_dragon_can_be_defeated_after_training(self):
        hero = HeroBuilder().set_level(7).build()
        from labs.lab3.world import DragonLair
        report = DragonLair().explore(hero, create_catalog(), 2026)
        self.assertTrue(report.battle.won)
        self.assertEqual(hero.inventory[0].code, "emerald")
