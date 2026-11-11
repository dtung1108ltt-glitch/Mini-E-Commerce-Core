"""
FIFO Queue Implementation for Checkout & Flash Sale Order Processing
Built using linked nodes with front and rear pointers for guaranteed O(1) enqueue and O(1) dequeue.
"""
from typing import Optional, Any, List


class QueueNode:
    __slots__ = ('data', 'next')

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional['QueueNode'] = None


class LinkedQueue:
    __slots__ = ('front', 'rear', '_size')

    def __init__(self):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def enqueue(self, item: Any) -> None:
        """Add an item to the back of the queue - O(1)"""
        node = QueueNode(item)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self._size += 1

    def dequeue(self) -> Optional[Any]:
        """Remove and return the item from the front of the queue - O(1)"""
        if self.is_empty() or self.front is None:
            return None
        item = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return item

    def peek(self) -> Optional[Any]:
        """Inspect the front item without removing - O(1)"""
        return self.front.data if self.front else None

    def to_list(self) -> List[Any]:
        """Return list representation from front to rear"""
        items = []
        curr = self.front
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items

    def clear(self) -> None:
        while self.front:
            next_node = self.front.next
            self.front.next = None
            self.front = next_node
        self.rear = None
        self._size = 0
