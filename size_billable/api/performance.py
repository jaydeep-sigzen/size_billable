"""
Performance Monitoring and Optimization Utilities

This module provides utilities for monitoring and optimizing the performance
of the Size Billable app, including query analysis, caching, and performance metrics.

Key Features:
- Query performance monitoring
- Database query optimization suggestions
- Caching utilities for frequently accessed data
- Performance metrics collection
- Memory usage monitoring
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, cint
import time
import functools
from typing import Dict, List, Any, Optional

# Cache for frequently accessed data
_query_cache = {}
_cache_ttl = 300  # 5 minutes

def cache_query_result(ttl: int = 300):
    """
    Decorator to cache query results for better performance
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Check if result is in cache
            if cache_key in _query_cache:
                cached_result, timestamp = _query_cache[cache_key]
                if time.time() - timestamp < ttl:
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _query_cache[cache_key] = (result, time.time())
            
            return result
        return wrapper
    return decorator

@frappe.whitelist()
def get_performance_metrics():
    """Get current performance metrics for Size Billable"""
    metrics = {
        "cache_size": len(_query_cache),
        "cache_hit_ratio": get_cache_hit_ratio(),
        "slow_queries": get_slow_queries(),
        "memory_usage": get_memory_usage(),
        "timestamp": now_datetime()
    }
    
    return metrics

def get_cache_hit_ratio() -> float:
    """Calculate cache hit ratio"""
    # This would need to be implemented with proper tracking
    return 0.0

def get_slow_queries() -> List[Dict]:
    """Get list of slow queries (if query logging is enabled)"""
    # This would need to be implemented with proper query logging
    return []

def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics"""
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss,  # Resident Set Size
        "vms": memory_info.vms,  # Virtual Memory Size
        "percent": process.memory_percent()
    }

@frappe.whitelist()
def clear_cache():
    """Clear the query cache"""
    global _query_cache
    _query_cache.clear()
    return {"message": "Cache cleared successfully"}

@frappe.whitelist()
def optimize_database():
    """Run database optimization tasks"""
    try:
        # Analyze tables for optimization
        tables_to_optimize = [
            "tabProject",
            "tabTimesheet",
            "tabTimesheet Detail"
        ]
        
        for table in tables_to_optimize:
            frappe.db.sql(f"ANALYZE TABLE {table}")
        
        return {"message": "Database optimization completed successfully"}
    except Exception as e:
        frappe.logger().error(f"Database optimization failed: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def get_query_performance_report():
    """Get detailed query performance report"""
    # This would need to be implemented with proper query logging
    return {
        "message": "Query performance monitoring not yet implemented",
        "suggestions": [
            "Enable MySQL slow query log",
            "Use EXPLAIN to analyze query plans",
            "Consider adding database indexes",
            "Monitor query execution times"
        ]
    }

class QueryProfiler:
    """Context manager for profiling database queries"""
    
    def __init__(self, query_name: str):
        self.query_name = query_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        # Log slow queries
        if execution_time > 1.0:  # Log queries taking more than 1 second
            frappe.logger().warning(
                f"Slow query detected: {self.query_name} took {execution_time:.2f} seconds"
            )

def profile_query(query_name: str):
    """Decorator to profile query execution time"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with QueryProfiler(query_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage of performance utilities
@cache_query_result(ttl=600)  # Cache for 10 minutes
@profile_query("get_project_summary")
def get_cached_project_summary(project_name: str) -> Dict[str, Any]:
    """Get project summary with caching and profiling"""
    return frappe.get_value("Project", project_name, 
        ["project_name", "billing_type", "total_purchased_hours", 
         "total_consumed_hours", "hourly_rate"], as_dict=True)

@frappe.whitelist()
def get_optimization_suggestions():
    """Get suggestions for optimizing the Size Billable app"""
    suggestions = [
        {
            "category": "Database",
            "suggestion": "Add indexes on frequently queried columns",
            "impact": "High",
            "effort": "Low"
        },
        {
            "category": "Caching",
            "suggestion": "Implement Redis caching for frequently accessed data",
            "impact": "High",
            "effort": "Medium"
        },
        {
            "category": "Queries",
            "suggestion": "Use bulk operations instead of loops for database updates",
            "impact": "Medium",
            "effort": "Low"
        },
        {
            "category": "Memory",
            "suggestion": "Implement pagination for large datasets",
            "impact": "Medium",
            "effort": "Low"
        },
        {
            "category": "API",
            "suggestion": "Add response compression for large API responses",
            "impact": "Low",
            "effort": "Low"
        }
    ]
    
    return suggestions
