import unittest
from decimal import Decimal

from labs.lab2.crm import Customer, Jewelry, Order, Stone
from labs.lab2.pets import Animal, Parrot, Person, Turtle


class PetTests(unittest.TestCase):
    def test_people_use_pet_methods_and_handle_missing_pet(self):
        person = Person("Иван")
        self.assertIn("нет питомца", person.get_pet_info())
        person.pet = Parrot("Кеша", 3)
        self.assertIn("15", person.get_pet_info())
        self.assertIn("Кеша", person.get_pet_info())
        person.pet = Turtle("Завала", 4)
        self.assertIn("21", person.get_pet_info())

    def test_age_boundaries_and_birthday(self):
        turtle = Turtle("Черепаха", 0)
        self.assertEqual(turtle.get_age_in_human_years(), 0)
        turtle.happy_birthday()
        self.assertEqual(turtle.get_age_in_human_years(), 15)
        with self.assertRaises(ValueError):
            Parrot("Кеша", -1)
        with self.assertRaises(TypeError):
            Animal("Животное", 1)


class CrmTests(unittest.TestCase):
    def test_order_accepts_stone_and_jewelry(self):
        garnet = Stone("G211", "Гранат", "2.85", "кушон", 18000)
        ring = Jewelry("R001", "Кольцо", "золото 585", garnet, 32000)
        moonstone = Stone("M015", "Лунный камень", "6.20", "кабошон", 12000)
        order = Order(Customer("Учебный клиент"))
        order.add(ring)
        order.add(moonstone)
        self.assertEqual(order.total, 62000)
        self.assertEqual(garnet.carats, Decimal("2.85"))
        self.assertIn("Кольцо", order.summary())
        self.assertIn("Лунный камень", order.summary())

    def test_duplicate_article_and_negative_values_are_rejected(self):
        order = Order(Customer("Клиент"))
        stone = Stone("G211", "Гранат", "2.85", "кушон", 18000)
        order.add(stone)
        with self.assertRaises(ValueError):
            order.add(stone)
        for weight, price in [("0", 1), ("1", -1)]:
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                Stone("G211", "Гранат", weight, "кушон", price)
        with self.assertRaises(ValueError):
            Jewelry("R001", "Кольцо", "золото", stone, -1)
