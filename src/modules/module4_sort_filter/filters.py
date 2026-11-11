"""
Filter Engine for Product Catalog
Filters products by Price Range and Rating threshold.
"""
from typing import List, Optional
from src.core.product import Product


class ProductFilter:
    @staticmethod
    def filter_by_price(products: List[Product], min_price: float = 0.0, max_price: float = float('inf')) -> List[Product]:
        return [p for p in products if min_price <= p.price <= max_price]

    @staticmethod
    def filter_by_rating(products: List[Product], min_rating: float = 0.0, max_rating: float = 5.0) -> List[Product]:
        return [p for p in products if min_rating <= p.rating <= max_rating]

    @staticmethod
    def filter_combined(
        products: List[Product],
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        in_stock_only: bool = False
    ) -> List[Product]:
        results = products
        if min_price is not None:
            results = [p for p in results if p.price >= min_price]
        if max_price is not None:
            results = [p for p in results if p.price <= max_price]
        if min_rating is not None:
            results = [p for p in results if p.rating >= min_rating]
        if max_rating is not None:
            results = [p for p in results if p.rating <= max_rating]
        if in_stock_only:
            results = [p for p in results if p.stock > 0]
        return results
