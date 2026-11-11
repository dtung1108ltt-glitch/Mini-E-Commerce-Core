"""
Self-Organizing List for Search Keyword History
Supports two heuristic strategies:
1. Move-to-Front (MTF): Moves the accessed element directly to the head of the list.
2. Transpose: Swaps the accessed element with its immediate predecessor.
Measures total comparisons/probes to evaluate efficiency on skewed workloads (e.g., 80/20 Zipfian queries).
"""
from typing import Optional, List, Dict, Any, Tuple


class HistoryNode:
    __slots__ = ('keyword', 'count', 'prev', 'next')

    def __init__(self, keyword: str):
        self.keyword: str = keyword
        self.count: int = 1
        self.prev: Optional['HistoryNode'] = None
        self.next: Optional['HistoryNode'] = None


class SelfOrganizingList:
    __slots__ = ('head', 'tail', '_size', 'strategy', 'total_probes', 'access_count')

    def __init__(self, strategy: str = "MTF"):
        """
        strategy: 'MTF' (Move-to-Front) or 'Transpose'
        """
        self.head: Optional[HistoryNode] = None
        self.tail: Optional[HistoryNode] = None
        self._size: int = 0
        self.strategy: str = strategy.upper()
        self.total_probes: int = 0
        self.access_count: int = 0

    def __len__(self) -> int:
        return self._size

    def set_strategy(self, strategy: str) -> None:
        self.strategy = strategy.upper()

    def record_search(self, keyword: str) -> int:
        """
        Record or lookup a search keyword.
        Applies chosen heuristic (MTF or Transpose).
        Returns the number of probes (comparisons) taken to locate the keyword.
        """
        clean_kw = keyword.strip()
        if not clean_kw:
            return 0

        self.access_count += 1
        curr = self.head
        probes = 0

        # Linear scan to locate node
        while curr:
            probes += 1
            if curr.keyword == clean_kw:
                curr.count += 1
                self.total_probes += probes
                # Reorganize based on strategy
                if self.strategy == "MTF":
                    self._move_to_front(curr)
                elif self.strategy == "TRANSPOSE":
                    self._transpose(curr)
                return probes
            curr = curr.next

        # Not found -> Add as new keyword at head
        self.total_probes += (probes + 1)
        new_node = HistoryNode(clean_kw)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
        return probes + 1

    def _move_to_front(self, node: HistoryNode) -> None:
        """Move node to head of doubly linked list."""
        if node == self.head:
            return

        # Unlink node
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        # Prepend to head
        node.prev = None
        node.next = self.head
        if self.head:
            self.head.prev = node
        self.head = node

    def _transpose(self, node: HistoryNode) -> None:
        """Swap node with its immediate predecessor."""
        if node == self.head or node.prev is None:
            return

        p = node.prev
        pp = p.prev
        n = node.next

        # Connect pp with node
        if pp:
            pp.next = node
        else:
            self.head = node
        node.prev = pp

        # Connect node with p
        node.next = p
        p.prev = node

        # Connect p with n
        p.next = n
        if n:
            n.prev = p
        else:
            self.tail = p

    def get_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        results = []
        curr = self.head
        while curr and len(results) < limit:
            results.append({
                "keyword": curr.keyword,
                "count": curr.count
            })
            curr = curr.next
        return results

    def get_metrics(self) -> Dict[str, Any]:
        avg_probes = (self.total_probes / self.access_count) if self.access_count > 0 else 0.0
        return {
            "strategy": self.strategy,
            "total_items": self._size,
            "access_count": self.access_count,
            "total_probes": self.total_probes,
            "avg_probes_per_access": round(avg_probes, 3)
        }

    def clear(self) -> None:
        curr = self.head
        while curr:
            next_node = curr.next
            curr.prev = None
            curr.next = None
            curr = next_node
        self.head = self.tail = None
        self._size = 0
        self.total_probes = 0
        self.access_count = 0
