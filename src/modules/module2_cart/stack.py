"""
LIFO Stack Implementation for Cart Undo History
Built using a linked chain of nodes to avoid static array pre-allocation.
Supports O(1) push, O(1) pop, O(1) peek, and size tracking.
"""
from typing import Optional, Any, List


class StackNode:
    __slots__ = ('data', 'next')

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['StackNode'] = None


class LinkedStack:
    __slots__ = ('top', '_size')

    def __init__(self):
        self.top: Optional[StackNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def push(self, item: Any) -> None:
        """Push an item onto the top of the stack - O(1)"""
        node = StackNode(item)
        node.next = self.top
        self.top = node
        self._size += 1

    def pop(self) -> Optional[Any]:
        """Remove and return the top item - O(1)"""
        if self.is_empty() or self.top is None:
            return None
        item = self.top.data
        self.top = self.top.next
        self._size -= 1
        return item

    def peek(self) -> Optional[Any]:
        """Inspect the top item without removing - O(1)"""
        return self.top.data if self.top else None

    def to_list(self) -> List[Any]:
        """Return list representation from top to bottom"""
        items = []
        curr = self.top
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def clear(self) -> None:
        while self.top:
            next_node = self.top.next
            self.top.next = None
            self.top = next_node
        self._size = 0
