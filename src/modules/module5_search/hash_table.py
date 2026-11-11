"""
Hash Table with Separate Chaining and Polynomial Rolling Hash
Indexes products by Name string.
Reports load factor, collision count, longest chain, and performs dynamic rehashing.
"""
from typing import Optional, List, Any, Tuple
from src.core.product import Product


class HashNode:
    __slots__ = ('key', 'product', 'next')

    def __init__(self, key: str, product: Product):
        self.key: str = key
        self.product: Product = product
        self.next: Optional['HashNode'] = None


class HashTable:
    __slots__ = ('_capacity', '_size', '_buckets', '_collisions', 'rehash_count', 'load_factor_threshold')

    # Initial prime capacity
    INITIAL_CAPACITY = 10007

    def __init__(self, initial_capacity: int = INITIAL_CAPACITY, load_factor_threshold: float = 0.75):
        self._capacity: int = initial_capacity
        self._size: int = 0
        self._buckets: List[Optional[HashNode]] = [None] * self._capacity
        self._collisions: int = 0
        self.rehash_count: int = 0
        self.load_factor_threshold: float = load_factor_threshold

    def __len__(self) -> int:
        return self._size

    def _hash_function(self, key: str) -> int:
        """
        Polynomial rolling hash function:
        H(s) = sum(s[i] * p^i) mod M, with p=31
        """
        p = 31
        hash_val = 0
        for char in key:
            hash_val = (hash_val * p + ord(char)) % self._capacity
        return hash_val

    def get_load_factor(self) -> float:
        return self._size / self._capacity if self._capacity > 0 else 0.0

    def insert(self, key: str, product: Product) -> None:
        """Insert product into hash table - average O(1)."""
        idx = self._hash_function(key)
        head = self._buckets[idx]

        # Check if key already exists in the chain -> update
        curr = head
        while curr:
            if curr.key == key:
                curr.product = product
                return
            curr = curr.next

        # Collision occurred if bucket is already occupied
        if head is not None:
            self._collisions += 1

        # Prepend new node to bucket chain (Separate Chaining) - O(1)
        new_node = HashNode(key, product)
        new_node.next = head
        self._buckets[idx] = new_node
        self._size += 1

        # Check if rehashing is required
        if self.get_load_factor() > self.load_factor_threshold:
            self._rehash()

    def search(self, key: str) -> Optional[Product]:
        """Lookup by exact name key - average O(1)."""
        idx = self._hash_function(key)
        curr = self._buckets[idx]
        while curr:
            if curr.key == key:
                return curr.product
            curr = curr.next
        return None

    def delete(self, key: str) -> Optional[Product]:
        """Delete by key - average O(1)."""
        idx = self._hash_function(key)
        curr = self._buckets[idx]
        prev = None

        while curr:
            if curr.key == key:
                if prev:
                    prev.next = curr.next
                else:
                    self._buckets[idx] = curr.next
                self._size -= 1
                deleted_product = curr.product
                curr.next = None
                return deleted_product
            prev = curr
            curr = curr.next

        return None

    def _next_prime(self, n: int) -> int:
        """Find the next prime number greater than or equal to n."""
        def _is_prime(num: int) -> bool:
            if num < 2:
                return False
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    return False
            return True

        candidate = n
        while not _is_prime(candidate):
            candidate += 1
        return candidate

    def _rehash(self) -> None:
        """Dynamically double capacity to next prime and re-index all nodes."""
        old_buckets = self._buckets
        new_capacity = self._next_prime(self._capacity * 2)

        self._capacity = new_capacity
        self._buckets = [None] * new_capacity
        self._collisions = 0
        self._size = 0
        self.rehash_count += 1

        for head in old_buckets:
            curr = head
            while curr:
                self.insert(curr.key, curr.product)
                curr = curr.next

    def get_statistics(self) -> dict:
        """Calculate load factor, longest chain, and collision count."""
        longest_chain = 0
        empty_buckets = 0

        for head in self._buckets:
            if head is None:
                empty_buckets += 1
            else:
                chain_len = 0
                curr = head
                while curr:
                    chain_len += 1
                    curr = curr.next
                if chain_len > longest_chain:
                    longest_chain = chain_len

        return {
            "capacity": self._capacity,
            "total_items": self._size,
            "load_factor": round(self.get_load_factor(), 4),
            "collision_count": self._collisions,
            "longest_chain": longest_chain,
            "empty_buckets": empty_buckets,
            "rehash_count": self.rehash_count
        }

    def clear(self) -> None:
        self._buckets = [None] * self._capacity
        self._size = 0
        self._collisions = 0
        self.rehash_count = 0
