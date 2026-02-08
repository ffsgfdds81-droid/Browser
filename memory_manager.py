# -*- coding: utf-8 -*-
"""
Advanced Memory Management System
Provides optimized memory usage, garbage collection optimization, and memory pooling
"""

import gc
import weakref
import psutil
import threading
import time
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Set
import weakref
from dataclasses import dataclass
from enum import Enum

class MemoryPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryPoolItem:
    obj: Any
    size: int
    last_used: float
    priority: MemoryPriority
    ref_count: int = 0

class MemoryManager:
    """
    Advanced memory management system with pooling, garbage collection optimization,
    and real-time memory monitoring
    """
    
    def __init__(self, max_memory_mb: int = 2048, cleanup_interval: float = 30.0):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.cleanup_interval = cleanup_interval
        self.process = psutil.Process()
        
        # Memory pools for different object types
        self.pools: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_objects: Dict[str, Set[weakref.ref]] = defaultdict(set)
        self.pool_metadata: Dict[str, MemoryPoolItem] = {}
        
        # Performance tracking
        self.stats = {
            'allocations': 0,
            'deallocations': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'gc_runs': 0,
            'memory_freed': 0
        }
        
        # Memory monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.memory_history = deque(maxlen=100)
        
        # Garbage collection optimization
        self.gc_thresholds = [700, 10, 10]  # Custom GC thresholds
        gc.set_threshold(*self.gc_thresholds)
        
        # Start monitoring
        self.start_monitoring()
        
    def start_monitoring(self):
        """Start memory monitoring in background thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_memory(self):
        """Background memory monitoring thread"""
        while self.monitoring_active:
            try:
                memory_info = self.process.memory_info()
                current_memory = memory_info.rss
                self.memory_history.append({
                    'timestamp': time.time(),
                    'memory_mb': current_memory / 1024 / 1024,
                    'memory_percent': self.process.memory_percent()
                })
                
                # Trigger cleanup if memory usage is high
                if current_memory > self.max_memory * 0.8:
                    self.perform_emergency_cleanup()
                
                time.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                break
    
    def allocate_from_pool(self, obj_type: str, factory_func, *args, **kwargs) -> Any:
        """
        Allocate object from pool or create new one
        """
        pool = self.pools[obj_type]
        
        if pool:
            obj = pool.popleft()
            self.stats['pool_hits'] += 1
            
            # Update metadata
            if id(obj) in self.pool_metadata:
                metadata = self.pool_metadata[id(obj)]
                metadata.last_used = time.time()
                metadata.ref_count += 1
            
            # Reinitialize object if needed
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            
            return obj
        else:
            self.stats['pool_misses'] += 1
            obj = factory_func(*args, **kwargs)
            
            # Track active object
            self.active_objects[obj_type].add(weakref.ref(obj, lambda r: self._cleanup_ref(obj_type, r)))
            
            # Store metadata
            self.pool_metadata[id(obj)] = MemoryPoolItem(
                obj=obj,
                size=self._estimate_object_size(obj),
                last_used=time.time(),
                priority=MemoryPriority.NORMAL
            )
            
            self.stats['allocations'] += 1
            return obj
    
    def return_to_pool(self, obj_type: str, obj: Any):
        """
        Return object to pool for reuse
        """
        if obj_type not in self.pools:
            return
            
        pool = self.pools[obj_type]
        
        if len(pool) < pool.maxlen:
            # Clean object if possible
            if hasattr(obj, 'cleanup'):
                obj.cleanup()
            
            pool.append(obj)
            
            # Update metadata
            if id(obj) in self.pool_metadata:
                metadata = self.pool_metadata[id(obj)]
                metadata.ref_count = max(0, metadata.ref_count - 1)
        else:
            # Pool is full, let object be garbage collected
            self._cleanup_object(obj)
    
    def _cleanup_ref(self, obj_type: str, ref: weakref.ref):
        """Cleanup when weak reference is destroyed"""
        self.active_objects[obj_type].discard(ref)
    
    def _cleanup_object(self, obj: Any):
        """Perform cleanup on object"""
        if hasattr(obj, 'cleanup'):
            obj.cleanup()
        
        # Remove from metadata
        obj_id = id(obj)
        if obj_id in self.pool_metadata:
            metadata = self.pool_metadata[obj_id]
            self.stats['memory_freed'] += metadata.size
            del self.pool_metadata[obj_id]
        
        self.stats['deallocations'] += 1
    
    def perform_emergency_cleanup(self):
        """Perform emergency memory cleanup"""
        print("🧹 Performing emergency memory cleanup...")
        
        # Force garbage collection
        collected = gc.collect()
        self.stats['gc_runs'] += 1
        
        # Clear least recently used objects from pools
        for obj_type, pool in self.pools.items():
            if len(pool) > 10:  # Keep some objects for performance
                removed = 0
                while len(pool) > 10 and removed < 50:
                    obj = pool.popleft()
                    self._cleanup_object(obj)
                    removed += 1
        
        print(f"✅ Emergency cleanup completed. Collected {collected} objects.")
    
    def optimize_gc(self):
        """Optimize garbage collection based on current memory usage"""
        current_memory = self.process.memory_info().rss
        memory_ratio = current_memory / self.max_memory
        
        if memory_ratio > 0.9:
            # High memory usage - aggressive GC
            gc.set_threshold(300, 5, 5)
        elif memory_ratio > 0.7:
            # Medium memory usage - moderate GC
            gc.set_threshold(500, 7, 7)
        else:
            # Low memory usage - relaxed GC
            gc.set_threshold(*self.gc_thresholds)
    
    def _estimate_object_size(self, obj: Any) -> int:
        """Estimate object size in bytes"""
        try:
            import sys
            return sys.getsizeof(obj)
        except:
            return 1024  # Default estimate
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        memory_info = self.process.memory_info()
        
        return {
            'current_memory_mb': memory_info.rss / 1024 / 1024,
            'memory_percent': self.process.memory_percent(),
            'max_memory_mb': self.max_memory / 1024 / 1024,
            'pool_objects': {obj_type: len(pool) for obj_type, pool in self.pools.items()},
            'active_objects': {obj_type: len(refs) for obj_type, refs in self.active_objects.items()},
            'gc_stats': gc.get_stats() if hasattr(gc, 'get_stats') else {},
            'performance_stats': self.stats.copy(),
            'gc_counts': gc.get_count(),
            'gc_thresholds': gc.get_threshold()
        }
    
    def get_memory_history(self) -> List[Dict[str, Any]]:
        """Get memory usage history"""
        return list(self.memory_history)
    
    def clear_pools(self):
        """Clear all object pools"""
        for obj_type, pool in self.pools.items():
            while pool:
                obj = pool.popleft()
                self._cleanup_object(obj)
        
        self.pools.clear()
        print("🧹 All memory pools cleared")
    
    def cleanup(self):
        """Cleanup memory manager"""
        self.stop_monitoring()
        self.clear_pools()
        gc.collect()

class MemoryPool:
    """
    Generic memory pool for specific object types
    """
    
    def __init__(self, obj_class, max_size: int = 100, factory_args=None, factory_kwargs=None):
        self.obj_class = obj_class
        self.max_size = max_size
        self.factory_args = factory_args or []
        self.factory_kwargs = factory_kwargs or {}
        self.pool = deque(maxlen=max_size)
        self.active_objects = weakref.WeakSet()
        
    def acquire(self, *args, **kwargs) -> Any:
        """Acquire object from pool"""
        if self.pool:
            obj = self.pool.popleft()
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
        else:
            obj = self.obj_class(*self.factory_args, **self.factory_kwargs)
        
        self.active_objects.add(obj)
        return obj
    
    def release(self, obj: Any):
        """Release object back to pool"""
        if obj in self.active_objects:
            self.active_objects.discard(obj)
            
            if len(self.pool) < self.max_size:
                if hasattr(obj, 'cleanup'):
                    obj.cleanup()
                self.pool.append(obj)
    
    def clear(self):
        """Clear pool"""
        self.pool.clear()
        self.active_objects.clear()

# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

def cleanup_memory():
    """Cleanup global memory manager"""
    global _memory_manager
    if _memory_manager:
        _memory_manager.cleanup()
        _memory_manager = None

# Decorators for automatic memory management
def memory_pooled(obj_type: str, pool_size: int = 100):
    """Decorator to make class use memory pooling"""
    def decorator(cls):
        original_init = cls.__init__
        
        def __new__(cls_inner, *args, **kwargs):
            manager = get_memory_manager()
            return manager.allocate_from_pool(obj_type, lambda: object.__new__(cls_inner))
        
        def reset(self, *args, **kwargs):
            """Reset object for reuse"""
            original_init(self, *args, **kwargs)
        
        cls.__new__ = __new__
        cls.reset = reset
        
        return cls
    
    return decorator

def memory_critical(priority: MemoryPriority = MemoryPriority.HIGH):
    """Decorator to mark critical memory objects"""
    def decorator(cls):
        cls._memory_priority = priority
        return cls
    return decorator