from .crm import Customer, Jewelry, Order, Stone
from .pets import Parrot, Person, Turtle


def main():
    print("Лаба 2. ООП\n")
    first = Person("Матвей", Parrot("Кеша", 3))
    second = Person("Иван")
    print(first.get_pet_info())
    print(second.get_pet_info())
    second.pet = Turtle("Завала", 4)
    print(second.get_pet_info())

    print("\nПример для ювелирной CRM (данные учебные)")
    garnet = Stone("G211", "Гранат", "2.85", "кушон", 18000)
    ring = Jewelry("R001", "Кольцо", "золото 585", garnet, 32000)
    moonstone = Stone("M015", "Лунный камень", "6.20", "кабошон", 12000)
    order = Order(Customer("Учебный клиент"))
    order.add(ring)
    order.add(moonstone)
    print(order.summary())


if __name__ == "__main__":
    main()
