import unittest
from unittest.mock import Mock, patch

from labs.lab3.defense import ArmorHandler, BarrierHandler, EvasionHandler


class BarrierTests(unittest.TestCase):
    def test_absorbs_smaller_equal_and_larger_hit(self):
        for incoming, remaining, strength in [(0, 0, 10), (7, 0, 3), (10, 0, 0), (14, 4, 0)]:
            with self.subTest(incoming=incoming):
                barrier = BarrierHandler(10)
                self.assertEqual(barrier.handle(incoming), remaining)
                self.assertEqual(barrier.strength, strength)

    def test_strength_is_spent_between_hits(self):
        barrier = BarrierHandler(10)
        self.assertEqual(barrier.handle(6), 0)
        self.assertEqual(barrier.handle(7), 3)
        self.assertEqual(barrier.handle(9), 9)

    def test_negative_strength_is_invalid(self):
        with self.assertRaises(ValueError):
            BarrierHandler(-1)


class DefenseChainTests(unittest.TestCase):
    def test_request_passes_through_every_handler_in_order(self):
        evasion = EvasionHandler(0.15)
        armor = ArmorHandler(0.2)
        barrier = BarrierHandler(5)
        evasion.set_next(armor).set_next(barrier)
        # Настоящая цепочка: 20 -> 20 -> 16 -> 11.
        with patch("labs.lab3.defense.Dice") as dice:
            dice.return_value.chance.return_value = False
            self.assertEqual(evasion.handle(20), 11)
            dice.return_value.chance.assert_called_once_with(0.15)
        self.assertEqual(barrier.strength, 0)

    def test_evasion_stops_chain(self):
        evasion = EvasionHandler(0.15)
        following = Mock()
        evasion.set_next(following)
        with patch("labs.lab3.defense.Dice") as dice:
            dice.return_value.chance.return_value = True
            self.assertEqual(evasion.handle(20), 0)
        following.handle.assert_not_called()

    def test_full_absorption_stops_chain(self):
        barrier = BarrierHandler(10)
        following = Mock()
        barrier.set_next(following)
        self.assertEqual(barrier.handle(10), 0)
        following.handle.assert_not_called()

    def test_zero_and_negative_damage_do_not_spend_barrier(self):
        armor = ArmorHandler(0.2)
        barrier = BarrierHandler(5)
        armor.set_next(barrier)
        self.assertEqual(armor.handle(0), 0)
        self.assertEqual(armor.handle(-20), 0)
        self.assertEqual(barrier.strength, 5)

    def test_armor_rounding_and_minimum_damage(self):
        self.assertEqual(ArmorHandler(0.25).handle(10), 8)
        self.assertEqual(ArmorHandler(0.8).handle(1), 1)

    def test_invalid_armor_and_evasion(self):
        for handler, value in [(ArmorHandler, -0.1), (ArmorHandler, 1.0),
                               (EvasionHandler, -0.1), (EvasionHandler, 1.1)]:
            with self.subTest(handler=handler, value=value), self.assertRaises(ValueError):
                handler(value)
