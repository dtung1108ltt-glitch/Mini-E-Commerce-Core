"""
Memory Profiler and Cleanup Manager
Measures RAM consumption, tracks allocations via tracemalloc, and validates node garbage collection.
"""
import gc
import tracemalloc
from typing import Dict, Any


class MemoryProfiler:
    _instance = None

    def __init__(self):
        self.snapshots = {}
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MemoryProfiler()
        return cls._instance

    def take_snapshot(self, label: str) -> Dict[str, Any]:
        """Record current and peak memory allocations in MB."""
        current, peak = tracemalloc.get_traced_memory()
        data = {
            "label": label,
            "current_mb": round(current / (1024 * 1024), 3),
            "peak_mb": round(peak / (1024 * 1024), 3),
        }
        self.snapshots[label] = data
        return data

    def get_memory_summary(self) -> Dict[str, Any]:
        current, peak = tracemalloc.get_traced_memory()
        return {
            "current_mb": round(current / (1024 * 1024), 3),
            "peak_mb": round(peak / (1024 * 1024), 3),
            "snapshots": self.snapshots
        }

    def force_cleanup(self) -> Dict[str, Any]:
        """Perform comprehensive garbage collection and update memory metrics."""
        collected = gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        res = {
            "unreachable_objects_collected": collected,
            "current_mb_after_gc": round(current / (1024 * 1024), 3),
            "peak_mb": round(peak / (1024 * 1024), 3)
        }
        self.snapshots["after_explicit_cleanup"] = res
        return res
