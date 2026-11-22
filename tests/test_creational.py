import unittest

from labs.lab3.dice import Dice
from labs.lab3.hero import HeroBuilder
from labs.lab3.items import MageKitFactory, WarriorKitFactory, create_catalog
from labs.lab3.world import Crypt, Forest


class DiceTests(unittest.TestCase):
    def setUp(self):
        Dice().reseed(2026)

    def test_one_instance_and_constructor_keeps_sequence(self):
        first = Dice()
        expected = [first.roll(1, 1000) for _ in range(3)]
        first.reseed(2026)
        actual = [Dice().roll(1, 1000) for _ in range(3)]
        self.assertIs(first, Dice())
        self.assertEqual(expected, actual)

    def test_roll_bounds_and_single_value(self):
        for _ in range(100):
            self.assertIn(Dice().roll(-2, 2), range(-2, 3))
        self.assertEqual(Dice().roll(7, 7), 7)

    def test_certain_and_impossible_events(self):
        for _ in range(30):
            self.assertFalse(Dice().chance(0))
            self.assertTrue(Dice().chance(1))

    def test_invalid_probability(self):
        for probability in (-0.1, 1.1):
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                Dice().chance(probability)

    def test_pick_returns_member_and_rejects_empty_list(self):
        self.assertIn(Dice().pick(["гранат", "сапфир"]), ["гранат", "сапфир"])
        token = object()
        self.assertIs(Dice().pick([token]), token)
        with self.assertRaises(IndexError):
            Dice().pick([])


class BuilderTests(unittest.TestCase):
    def test_builds_configured_hero(self):
        hero = HeroBuilder().set_name("  Матвей  ").set_class("mage").set_level(3).build()
        self.assertEqual((hero.name, hero.hero_class, hero.level), ("Матвей", "mage", 3))
        self.assertEqual(hero.max_health, 115)
        self.assertEqual(hero.weapon.code, "staff")

    def test_invalid_settings(self):
        builders = [HeroBuilder().set_name(" "), HeroBuilder().set_name("я" * 21),
                    HeroBuilder().set_class("unknown"), HeroBuilder().set_level(0)]
        for builder in builders:
            with self.subTest(builder=builder), self.assertRaises(ValueError):
                builder.build()

    def test_builds_independent_heroes(self):
        builder = HeroBuilder()
        first, second = builder.build(), builder.build()
        first.weapon.enchantments.append("Гранат")
        first.inventory.append(create_catalog().create("emerald"))
        self.assertEqual(second.weapon.enchantments, [])
        self.assertEqual(second.inventory, [])


class PrototypeTests(unittest.TestCase):
    def test_nested_state_is_copied(self):
        original = create_catalog().create("garnet")
        original.enchantments.append("Свет")
        copied = original.clone()
        copied.enchantments.append("Огонь")
        copied.carats = 1.2
        self.assertEqual(original.enchantments, ["Свет"])
        self.assertEqual(original.carats, 2.85)
        self.assertEqual(copied.cut, original.cut)

    def test_catalog_isolates_registered_template(self):
        catalog = create_catalog()
        template = catalog.create("garnet")
        catalog.register(template)
        template.name = "Изменён"
        first = catalog.create("garnet")
        first.enchantments.append("Свет")
        second = catalog.create("garnet")
        self.assertEqual(second.name, "Гранат")
        self.assertEqual(second.enchantments, [])

    def test_unknown_code(self):
        with self.assertRaises(ValueError):
            create_catalog().create("unknown")


class FactoryTests(unittest.TestCase):
    def test_abstract_factory_produces_matching_families(self):
        catalog = create_catalog()
        warrior = WarriorKitFactory(catalog)
        mage = MageKitFactory(catalog)
        self.assertEqual((warrior.create_weapon().code, warrior.create_armor().code), ("sword", "plate"))
        self.assertEqual((mage.create_weapon().code, mage.create_armor().code), ("staff", "robe"))
        self.assertIsNot(mage.create_weapon(), mage.create_weapon())

    def test_locations_create_different_enemies(self):
        forest, crypt = Forest().create_enemy(), Crypt().create_enemy()
        self.assertNotEqual(type(forest), type(crypt))
        self.assertLess(forest.health, crypt.health)
