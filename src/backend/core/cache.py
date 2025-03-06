"""
Caching module for the Freight Price Movement Agent.

This module provides a unified interface for caching frequently accessed data
and analysis results using Redis, implementing different TTLs for various data types
to optimize performance and reduce database load.
"""

import redis
import json
import typing
import functools
import pickle

from .config import settings
from .exceptions import ConfigurationException
from .utils import logger

# Global Redis client instance
redis_client = None  # Redis client instance, initialized in initialize_cache()


def initialize_cache() -> redis.Redis:
    """
    Initializes the Redis cache connection
    
    Returns:
        redis.Redis: Redis client instance
    
    Raises:
        ConfigurationException: If Redis connection cannot be established
    """
    global redis_client
    
    try:
        conn_params = settings.get_redis_connection_parameters()
        redis_client = redis.Redis(**conn_params)
        
        # Test connection
        redis_client.ping()
        
        logger.info("Cache initialized successfully")
        return redis_client
    except redis.ConnectionError as e:
        raise ConfigurationException(
            "Failed to connect to Redis server",
            details={"redis_url": settings.REDIS_URL},
            original_exception=e
        )
    except Exception as e:
        raise ConfigurationException(
            "Failed to initialize cache",
            details={"error": str(e)},
            original_exception=e
        )


def get_redis_client() -> redis.Redis:
    """
    Returns the Redis client, initializing it if necessary
    
    Returns:
        redis.Redis: Redis client instance
    """
    global redis_client
    
    if redis_client is None:
        redis_client = initialize_cache()
    
    return redis_client


def cache_key(prefix: str, identifier: str) -> str:
    """
    Generates a standardized cache key from prefix and identifier
    
    Args:
        prefix: Cache type prefix
        identifier: Unique identifier for the cached item
        
    Returns:
        str: Formatted cache key
    """
    # Sanitize keys to ensure they're valid for Redis
    prefix = prefix.strip().lower()
    # Remove any characters that could cause issues in Redis keys
    identifier = str(identifier).replace(' ', '_')
    
    # Format: prefix:identifier
    return f"{prefix}:{identifier}"


def cached(prefix: typing.Optional[str] = None, ttl: typing.Optional[int] = None):
    """
    Decorator for caching function results
    
    Args:
        prefix: Cache key prefix (defaults to function name)
        ttl: Time-to-live in seconds (defaults to CACHE_TTL)
        
    Returns:
        typing.Callable: Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_prefix = prefix or func.__name__
            
            # Create a stable representation of args and kwargs for the cache key
            args_str = str(args)
            kwargs_str = str(sorted(kwargs.items()))
            key_identifier = f"{args_str}:{kwargs_str}"
            
            # Create full cache key
            key = cache_key(key_prefix, key_identifier)
            
            # Get Redis client
            client = get_redis_client()
            
            # Try to get from cache
            cached_result = client.get(key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    # Try with pickle if JSON fails
                    try:
                        return pickle.loads(cached_result)
                    except pickle.PickleError:
                        logger.warning(f"Failed to deserialize cached result for key: {key}")
            
            # Execute function if not in cache
            result = func(*args, **kwargs)
            
            # Cache the result
            try:
                # Try JSON first for better interoperability
                serialized = json.dumps(result)
            except (TypeError, OverflowError):
                # Fall back to pickle for complex objects
                try:
                    serialized = pickle.dumps(result)
                except pickle.PickleError as e:
                    logger.warning(f"Failed to serialize result for caching: {str(e)}")
                    return result
            
            # Store in cache with TTL
            cache_ttl = ttl or settings.CACHE_TTL
            client.setex(key, cache_ttl, serialized)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidates cache entries matching a pattern
    
    Args:
        pattern: Redis key pattern to match (e.g., "result:*")
        
    Returns:
        int: Number of invalidated cache entries
    """
    client = get_redis_client()
    
    # Find keys matching the pattern
    keys = client.keys(pattern)
    
    # Delete all matching keys
    if keys:
        count = client.delete(*keys)
        logger.info(f"Invalidated {count} cache entries matching pattern '{pattern}'")
        return count
    
    return 0


class CacheManager:
    """
    Manager class for different types of caches with varying TTLs
    """
    
    def __init__(self):
        """
        Initializes the CacheManager with Redis connection
        """
        self._redis = get_redis_client()
    
    def get(self, key: str, prefix: str) -> typing.Any:
        """
        Retrieves a value from cache by key
        
        Args:
            key: Cache item identifier
            prefix: Cache type prefix
            
        Returns:
            typing.Any: Cached value or None if not found
        """
        full_key = cache_key(prefix, key)
        
        try:
            value = self._redis.get(full_key)
            if value is None:
                return None
                
            try:
                # Try JSON deserialization first
                return json.loads(value)
            except json.JSONDecodeError:
                # Fall back to pickle
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, key: str, value: typing.Any, prefix: str, ttl: typing.Optional[int] = None) -> bool:
        """
        Stores a value in cache with specified TTL
        
        Args:
            key: Cache item identifier
            value: Value to cache
            prefix: Cache type prefix
            ttl: Time-to-live in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        full_key = cache_key(prefix, key)
        
        try:
            # Try JSON serialization
            try:
                serialized = json.dumps(value)
            except (TypeError, OverflowError):
                # Fall back to pickle for complex objects
                serialized = pickle.dumps(value)
            
            # Set with expiration
            return bool(self._redis.setex(full_key, ttl or settings.CACHE_TTL, serialized))
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str, prefix: str) -> bool:
        """
        Deletes a value from cache by key
        
        Args:
            key: Cache item identifier
            prefix: Cache type prefix
            
        Returns:
            bool: True if successful, False otherwise
        """
        full_key = cache_key(prefix, key)
        
        try:
            return bool(self._redis.delete(full_key))
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def get_result_cache(self, key: str) -> typing.Any:
        """
        Retrieves a value from the analysis results cache
        
        Args:
            key: Cache item identifier
            
        Returns:
            typing.Any: Cached analysis result or None if not found
        """
        return self.get(key, "result")
    
    def set_result_cache(self, key: str, value: typing.Any) -> bool:
        """
        Stores a value in the analysis results cache
        
        Args:
            key: Cache item identifier
            value: Value to cache
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set(key, value, "result", settings.RESULT_CACHE_TTL)
    
    def get_reference_cache(self, key: str) -> typing.Any:
        """
        Retrieves a value from the reference data cache
        
        Args:
            key: Cache item identifier
            
        Returns:
            typing.Any: Cached reference data or None if not found
        """
        return self.get(key, "reference")
    
    def set_reference_cache(self, key: str, value: typing.Any) -> bool:
        """
        Stores a value in the reference data cache
        
        Args:
            key: Cache item identifier
            value: Value to cache
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set(key, value, "reference", settings.REFERENCE_CACHE_TTL)
    
    def get_query_cache(self, key: str) -> typing.Any:
        """
        Retrieves a value from the query results cache
        
        Args:
            key: Cache item identifier
            
        Returns:
            typing.Any: Cached query result or None if not found
        """
        return self.get(key, "query")
    
    def set_query_cache(self, key: str, value: typing.Any) -> bool:
        """
        Stores a value in the query results cache
        
        Args:
            key: Cache item identifier
            value: Value to cache
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set(key, value, "query", settings.QUERY_CACHE_TTL)
    
    def invalidate_result_cache(self) -> int:
        """
        Invalidates all entries in the analysis results cache
        
        Returns:
            int: Number of invalidated cache entries
        """
        return invalidate_cache("result:*")
    
    def invalidate_reference_cache(self) -> int:
        """
        Invalidates all entries in the reference data cache
        
        Returns:
            int: Number of invalidated cache entries
        """
        return invalidate_cache("reference:*")
    
    def invalidate_query_cache(self) -> int:
        """
        Invalidates all entries in the query results cache
        
        Returns:
            int: Number of invalidated cache entries
        """
        return invalidate_cache("query:*")


# Create a singleton instance of CacheManager for application-wide use
cache_manager = CacheManager()