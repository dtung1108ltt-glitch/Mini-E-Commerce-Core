"""
Product ADT (Abstract Data Type)
Represents a product item in the Mini E-Commerce Engine.
Optimized with __slots__ to minimize per-object memory overhead across 100,000+ instances.
"""
from typing import Dict, Any


class Product:
    __slots__ = ('id', 'name', 'price', 'stock', 'rating')

    def __init__(self, product_id: int, name: str, price: float, stock: int, rating: float):
        self.id = int(product_id)
        self.name = str(name)
        self.price = float(price)
        self.stock = int(stock)
        self.rating = round(float(rating), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "rating": self.rating
        }

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name='{self.name}', price={self.price:,.0f}, stock={self.stock}, rating={self.rating})"

    def __str__(self) -> str:
        return f"[{self.id:06d}] {self.name:<32} | Price: {self.price:>10,.0f} | Stock: {self.stock:>4} | ★ {self.rating:.1f}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.id < other.id
