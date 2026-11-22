from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


class Product(ABC):
    def __init__(self, article: str, price: int):
        if not article.strip() or price < 0:
            raise ValueError("Проверьте артикул и цену")
        self._article = article
        self._price = price

    @property
    def article(self) -> str:
        return self._article

    @property
    def price(self) -> int:
        return self._price

    @abstractmethod
    def describe(self) -> str: ...


class Stone(Product):
    def __init__(self, article: str, name: str, carats: str, cut: str, price: int):
        super().__init__(article, price)
        self.name = name
        self.carats = Decimal(carats)
        if self.carats <= 0:
            raise ValueError("Вес должен быть больше нуля")
        self.cut = cut

    def describe(self) -> str:
        return f"{self.article}: {self.name}, {self.carats} ct, {self.cut}"


class Jewelry(Product):
    def __init__(self, article: str, kind: str, metal: str, stone: Stone, work_price: int):
        if work_price < 0:
            raise ValueError("Стоимость работы не может быть отрицательной")
        super().__init__(article, stone.price + work_price)
        self.kind = kind
        self.metal = metal
        self.stone = stone

    def describe(self) -> str:
        return f"{self.article}: {self.kind}, {self.metal}, {self.stone.name} {self.stone.carats} ct"


@dataclass(frozen=True)
class Customer:
    name: str


class Order:
    def __init__(self, customer: Customer):
        self.customer = customer
        self._products: list[Product] = []

    def add(self, product: Product) -> None:
        if any(item.article == product.article for item in self._products):
            raise ValueError("Этот товар уже добавлен в заказ")
        self._products.append(product)

    @property
    def total(self) -> int:
        return sum(product.price for product in self._products)

    def summary(self) -> str:
        rows = [f"Заказ: {self.customer.name}"]
        rows.extend(f"{p.describe()} — {p.price:,} ₽" for p in self._products)
        rows.append(f"Итого: {self.total:,} ₽")
        return "\n".join(rows)
