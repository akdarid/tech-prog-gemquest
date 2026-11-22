import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from labs.lab3.hero import HeroBuilder
from labs.lab3.items import create_catalog
from labs.lab3.storage import CachingHeroRepository, FileHeroRepository, HeroRepository, hero_snapshot


class CachingRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.hero = HeroBuilder().set_name("Матвей").build()
        self.target = Mock(spec=HeroRepository)
        self.target.find_all.return_value = [self.hero]
        self.proxy = CachingHeroRepository(self.target)

    def test_cache_is_lazy_and_reads_target_once(self):
        self.target.find_all.assert_not_called()
        self.assertEqual(self.proxy.find_by_name("Матвей").name, "Матвей")
        self.proxy.find_all()
        self.assertIsNone(self.proxy.find_by_name("Нет"))
        self.target.find_all.assert_called_once_with()

    def test_returns_independent_snapshots(self):
        first = self.proxy.find_by_name("Матвей")
        first.gold = 999
        self.proxy.find_all().clear()
        self.assertEqual(self.proxy.find_by_name("Матвей").gold, 50)

    def test_save_updates_storage_and_loaded_cache(self):
        self.proxy.find_all()
        self.hero.gold = 99
        self.proxy.save(self.hero)
        self.target.save.assert_called_once_with(self.hero)
        self.assertEqual(self.proxy.find_by_name("Матвей").gold, 99)
        self.hero.gold = 1
        self.assertEqual(self.proxy.find_by_name("Матвей").gold, 99)
        self.target.find_all.assert_called_once_with()

    def test_save_before_first_read_populates_cache(self):
        self.proxy.save(self.hero)
        self.assertEqual(self.proxy.find_by_name("Матвей").name, "Матвей")
        self.target.save.assert_called_once_with(self.hero)

    def test_failed_write_does_not_change_cache(self):
        self.proxy.find_all()
        self.hero.gold = 999
        self.target.save.side_effect = OSError("Диск недоступен")
        with self.assertRaises(OSError):
            self.proxy.save(self.hero)
        self.assertEqual(self.proxy.find_by_name("Матвей").gold, 50)


class FileRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "nested" / "heroes.json"
        self.repository = FileHeroRepository(self.path)

    def test_absent_file_is_empty(self):
        self.assertEqual(self.repository.find_all(), [])
        self.assertIsNone(self.repository.find_by_name("Нет"))

    def test_empty_file_is_empty(self):
        self.path.parent.mkdir()
        self.path.write_text(" \n", encoding="utf-8")
        self.assertEqual(self.repository.find_all(), [])

    def test_round_trip_preserves_progress_gems_and_enchantments(self):
        hero = HeroBuilder().set_name("Мастер").set_class("mage").set_level(3).build()
        hero.experience, hero.gold, hero.health = 45, 220, 51
        hero.weapon.enchantments.append("Гранат")
        hero.inventory.append(create_catalog().create("emerald"))
        hero.achievements.append("Первая находка")
        self.repository.save(hero)
        loaded = FileHeroRepository(self.path).find_by_name("Мастер")
        self.assertEqual(hero_snapshot(loaded), hero_snapshot(hero))
        self.assertIn("Мастер", self.path.read_text(encoding="utf-8"))
        self.assertFalse(self.path.with_suffix(".json.tmp").exists())

    def test_update_keeps_other_heroes_and_does_not_duplicate(self):
        first = HeroBuilder().set_name("Первый").build()
        second = HeroBuilder().set_name("Второй").build()
        self.repository.save(first)
        self.repository.save(second)
        first.gold = 123
        self.repository.save(first)
        self.assertEqual(len(self.repository.find_all()), 2)
        self.assertEqual(self.repository.find_by_name("Первый").gold, 123)
        self.assertEqual(self.repository.find_by_name("Второй").gold, 50)

    def test_bad_save_is_not_silently_overwritten(self):
        self.path.parent.mkdir()
        for text in ("broken json", '{"heroes": []}'):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises((ValueError, json.JSONDecodeError)):
                    self.repository.save(HeroBuilder().build())
                self.assertEqual(self.path.read_text(encoding="utf-8"), text)
