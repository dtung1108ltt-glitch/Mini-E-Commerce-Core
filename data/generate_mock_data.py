"""
Synthetic Mock Data Generator for Mini E-Commerce System
Generates realistic e-commerce product catalogs with ID, Name, Price, Stock, Rating.
"""
import os
import csv
import random
from typing import List

ADJECTIVES = [
    "Ultra", "Pro", "Smart", "Eco", "Premium", "Wireless", "Gaming", "Compact",
    "Max", "Super", "Neo", "Lite", "Advanced", "Dynamic", "Classic", "Hyper"
]

BRANDS = [
    "Sony", "Apple", "Samsung", "Xiaomi", "Dell", "Asus", "Logitech", "Anker",
    "Baseus", "Nike", "Adidas", "Uniqlo", "Philips", "Panasonic", "Casio", "Seiko"
]

NOUNS = [
    "Headphones", "Mechanical Keyboard", "Mouse", "Smartphone", "Laptop", "Smartwatch",
    "Monitor", "Power Bank", "Earbuds", "Backpack", "Running Shoes", "Desk Lamp",
    "Air Purifier", "Bluetooth Speaker", "Tablet", "Coffee Maker", "Thermal Cup", "Jacket"
]


def generate_product_name(product_id: int) -> str:
    brand = random.choice(BRANDS)
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    model = random.randint(10, 999)
    return f"{brand} {adj} {noun} #{model}"


def generate_mock_csv(output_path: str, count: int = 100000, verbose: bool = False) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)  # Deterministic seed for reproducible benchmarks

    if verbose:
        print(f"Generating {count:,} products into {output_path}...")
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "price", "stock", "rating"])
        for pid in range(1, count + 1):
            name = generate_product_name(pid)
            # Price between 50,000 VND and 45,000,000 VND
            price = round(random.uniform(50000, 45000000), -3)
            # Stock between 0 (out of stock) and 500
            stock = random.randint(0, 500)
            # Rating between 1.0 and 5.0
            rating = round(random.uniform(2.5, 5.0), 2)
            writer.writerow([pid, name, price, stock, rating])

    if verbose:
        print(f"Successfully generated {count:,} records in {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    path = os.path.join(os.path.dirname(__file__), "products_100k.csv")
    generate_mock_csv(path, count)
