"""
Core utility functions for the Freight Price Movement Agent backend.

This module provides general-purpose utility functions that are used across
multiple components of the application, including data transformation, type conversion,
error handling, and common operations.
"""

import os
import sys
import uuid
import json
import decimal
from decimal import Decimal
import datetime
import typing
import logging
import traceback
import time
from functools import wraps
from collections import OrderedDict

from .exceptions import ApplicationException
from .config import settings

# Configure module-level logger
logger = logging.getLogger(__name__)


def setup_logging(log_level: typing.Optional[str] = None) -> None:
    """
    Configures the logging system for the application.
    
    Args:
        log_level: Optional log level override. If None, uses settings.LOG_LEVEL
    """
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    root_logger.addHandler(console_handler)
    
    # Special handling for DEBUG mode
    if settings.DEBUG:
        logger.debug("Running in DEBUG mode - verbose logging enabled")
    
    logger.info(f"Logging configured with level: {level}")


def generate_uuid() -> str:
    """
    Generates a unique identifier string.
    
    Returns:
        A new UUID string
    """
    return str(uuid.uuid4())


def safe_cast(value: typing.Any, target_type: typing.Type, default: typing.Any = None) -> typing.Any:
    """
    Safely casts a value to a specified type with a default fallback.
    
    Args:
        value: The value to cast
        target_type: The type to cast to
        default: Value to return if casting fails
        
    Returns:
        The value cast to the target type, or default if casting fails
    """
    if value is None:
        return default
    
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        logger.debug(f"Failed to cast {value} to {target_type.__name__}: {str(e)}")
        return default


def to_decimal(value: typing.Any, default: typing.Optional[Decimal] = None) -> Decimal:
    """
    Converts a value to Decimal with proper handling of various input types.
    
    Args:
        value: The value to convert
        default: Value to return if conversion fails
        
    Returns:
        Converted Decimal value or default
    """
    if value is None:
        return default if default is not None else Decimal('0')
    
    if isinstance(value, Decimal):
        return value
    
    try:
        if isinstance(value, str):
            # Handle string with possible currency symbols or commas
            value = value.strip()
            # Remove currency symbols and commas
            for symbol in ['$', '€', '£', '¥', ',']:
                value = value.replace(symbol, '')
            
            return Decimal(value)
        
        # Handle other numeric types
        return Decimal(str(value))
    
    except (decimal.InvalidOperation, ValueError, TypeError) as e:
        logger.debug(f"Failed to convert {value} to Decimal: {str(e)}")
        return default if default is not None else Decimal('0')


def to_bool(value: typing.Any, default: typing.Optional[bool] = False) -> bool:
    """
    Converts a value to boolean with proper handling of various input types.
    
    Args:
        value: The value to convert
        default: Value to return if conversion is ambiguous
        
    Returns:
        Converted boolean value or default
    """
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', 'yes', 'y', '1', 'on'):
            return True
        if value in ('false', 'no', 'n', '0', 'off'):
            return False
        # If string is neither clearly True nor False, return default
        logger.debug(f"Ambiguous boolean string: {value}, using default: {default}")
        return default
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    # For other types, use Python's bool() function
    try:
        return bool(value)
    except (ValueError, TypeError) as e:
        logger.debug(f"Failed to convert {value} to bool: {str(e)}")
        return default


def chunks(lst: typing.List, chunk_size: int) -> typing.Generator:
    """
    Splits a list into chunks of specified size.
    
    Args:
        lst: The list to split
        chunk_size: Size of each chunk
        
    Returns:
        Generator yielding chunks of the list
        
    Raises:
        ValueError: If chunk_size is not positive
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def flatten_dict(nested_dict: dict, parent_key: typing.Optional[str] = None, 
               separator: typing.Optional[str] = None) -> dict:
    """
    Flattens a nested dictionary into a single-level dictionary with dot-notation keys.
    
    Args:
        nested_dict: The nested dictionary to flatten
        parent_key: Base key for nested keys (used in recursion)
        separator: Character to use when joining keys, defaults to '.'
        
    Returns:
        A flattened dictionary
    """
    items = []
    parent_key = parent_key or ''
    separator = separator or '.'
    
    for k, v in nested_dict.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def deep_get(dictionary: dict, keys: str, default: typing.Any = None) -> typing.Any:
    """
    Safely gets a value from a nested dictionary using dot notation.
    
    Args:
        dictionary: The dictionary to search in
        keys: Dot-separated string of keys (e.g., 'level1.level2.key')
        default: Value to return if key path is not found
        
    Returns:
        Value from the nested dictionary or default
    """
    if not dictionary or not keys:
        return default
    
    try:
        # Split keys by dot
        key_parts = keys.split('.')
        current = dictionary
        
        # Navigate through the keys
        for key in key_parts:
            if not isinstance(current, dict):
                return default
            
            # Get the next level
            if key not in current:
                return default
            
            current = current[key]
        
        return current
    except Exception as e:
        logger.debug(f"Error accessing nested key '{keys}': {str(e)}")
        return default


def deep_set(dictionary: dict, keys: str, value: typing.Any) -> dict:
    """
    Sets a value in a nested dictionary using dot notation, creating intermediate
    dictionaries as needed.
    
    Args:
        dictionary: The dictionary to modify
        keys: Dot-separated string of keys (e.g., 'level1.level2.key')
        value: Value to set at the specified key path
        
    Returns:
        Updated dictionary
    """
    if not keys:
        return dictionary
    
    # Split keys by dot
    key_parts = keys.split('.')
    current = dictionary
    
    # Navigate through the keys, creating dictionaries as needed
    for i, key in enumerate(key_parts[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    # Set the value at the final key
    current[key_parts[-1]] = value
    
    return dictionary


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merges two dictionaries, with values from dict2 taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (values overwrite dict1)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()  # Start with dict1's keys and values
    
    for key, value in dict2.items():
        # If both values are dictionaries, merge them recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            # Otherwise, use the value from dict2
            result[key] = value
    
    return result


def dict_to_object(dictionary: dict) -> typing.Any:
    """
    Converts a dictionary to an object with attributes.
    
    Args:
        dictionary: Dictionary to convert
        
    Returns:
        Object with attributes from the dictionary
    """
    if not dictionary:
        return None
    
    class Object:
        pass
    
    obj = Object()
    
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # Recursively convert nested dictionaries
            setattr(obj, key, dict_to_object(value))
        else:
            setattr(obj, key, value)
    
    return obj


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncates a string to a specified length, adding an ellipsis if truncated.
    
    Args:
        text: String to truncate
        max_length: Maximum length of the truncated string
        suffix: String to append if truncated
        
    Returns:
        Truncated string
    """
    if text is None:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_exception(exception: Exception, include_traceback: bool = True) -> str:
    """
    Formats an exception into a readable string with traceback.
    
    Args:
        exception: The exception to format
        include_traceback: Whether to include the full traceback
        
    Returns:
        Formatted exception string
    """
    if exception is None:
        return "No exception information available"
    
    # Get exception type and message
    exception_type = type(exception).__name__
    exception_message = str(exception)
    
    # Format the basic exception info
    formatted_exception = f"{exception_type}: {exception_message}"
    
    # Add traceback if requested
    if include_traceback:
        exception_traceback = ''.join(traceback.format_exception(type(exception), 
                                                               exception, 
                                                               exception.__traceback__))
        formatted_exception = f"{formatted_exception}\n\nTraceback:\n{exception_traceback}"
    
    # Add details for ApplicationException
    if isinstance(exception, ApplicationException) and exception.details:
        formatted_exception = f"{formatted_exception}\n\nDetails: {exception.details}"
    
    return formatted_exception


def safe_divide(numerator: typing.Union[int, float, Decimal], 
                denominator: typing.Union[int, float, Decimal], 
                default: typing.Union[int, float, Decimal] = Decimal('0')) -> typing.Union[int, float, Decimal]:
    """
    Safely divides two numbers, handling division by zero.
    
    Args:
        numerator: Dividend (number being divided)
        denominator: Divisor (number to divide by)
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default if denominator is zero
    """
    try:
        # Convert to Decimal for precise arithmetic
        num = to_decimal(numerator)
        denom = to_decimal(denominator)
        
        if denom == Decimal('0'):
            logger.debug("Division by zero detected, using default value")
            return default
        
        return num / denom
    
    except Exception as e:
        logger.debug(f"Error in safe_divide: {str(e)}")
        return default


def is_json_serializable(obj: typing.Any) -> bool:
    """
    Checks if an object can be serialized to JSON.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object is JSON serializable, False otherwise
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def get_object_size(obj: typing.Any) -> int:
    """
    Estimates the memory size of an object in bytes.
    
    Args:
        obj: Object to measure
        
    Returns:
        Estimated size in bytes
    """
    size = sys.getsizeof(obj)
    
    # Handle common container types
    if isinstance(obj, dict):
        size += sum(get_object_size(k) + get_object_size(v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        size += sum(get_object_size(item) for item in obj)
    
    return size


def retry(max_retries: int = 3, 
          exceptions: typing.List[typing.Type[Exception]] = None, 
          backoff_factor: float = 0.5) -> typing.Callable:
    """
    Decorator that retries a function on specified exceptions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        exceptions: List of exception types to catch and retry
        backoff_factor: Factor for exponential backoff calculation
        
    Returns:
        Decorated function
    """
    if exceptions is None:
        exceptions = [Exception]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.warning(f"Maximum retries ({max_retries}) exceeded for {func.__name__}")
                        raise e
                    
                    # Calculate backoff time with exponential factor
                    backoff_time = backoff_factor * (2 ** (retry_count - 1))
                    logger.info(f"Retry {retry_count}/{max_retries} for {func.__name__} after {backoff_time:.2f}s")
                    time.sleep(backoff_time)
        
        return wrapper
    
    return decorator


def memoize(max_size: typing.Optional[int] = None) -> typing.Callable:
    """
    Decorator that caches function results based on arguments.
    
    Args:
        max_size: Maximum number of results to cache (None for unlimited)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        # Use OrderedDict to maintain insertion order for LRU-like behavior
        cache = OrderedDict()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from the function arguments
            key = str(args) + str(sorted(kwargs.items()))
            
            if key in cache:
                # Move to end to mark as recently used
                value = cache.pop(key)
                cache[key] = value
                return value
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = result
            
            # If max_size is specified and cache is full, remove the oldest entry
            if max_size is not None and len(cache) > max_size:
                cache.popitem(last=False)  # Remove the first item (oldest)
            
            return result
        
        # Add a method to clear the cache
        wrapper.clear_cache = lambda: cache.clear()
        
        return wrapper
    
    return decorator


def timeit(name: typing.Optional[str] = None) -> typing.Callable:
    """
    Decorator that measures and logs the execution time of a function.
    
    Args:
        name: Optional name for the timer (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timer_name = name or func.__name__
            start_time = time.time()
            
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_time = time.time() - start_time
                logger.info(f"{timer_name} executed in {elapsed_time:.4f} seconds")
        
        return wrapper
    
    return decorator


class Singleton(type):
    """
    Metaclass that ensures only one instance of a class exists.
    
    Usage:
        class MyClass(metaclass=Singleton):
            pass
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Timer:
    """
    Context manager for measuring execution time.
    
    Usage:
        with Timer("Operation name"):
            # code to measure
    """
    def __init__(self, name: typing.Optional[str] = None):
        """
        Initialize a new Timer instance.
        
        Args:
            name: Optional name for the timer
        """
        self.name = name or "Timer"
        self.start_time = None
        self.end_time = None
    
    def __enter__(self) -> 'Timer':
        """
        Called when entering the context manager.
        
        Returns:
            Self reference for use in the context
        """
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Called when exiting the context manager.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.end_time = time.time()
        elapsed = self.elapsed()
        logger.info(f"{self.name} completed in {elapsed:.4f} seconds")
    
    def elapsed(self) -> float:
        """
        Returns the elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        if self.end_time is None:
            # Still running, calculate from start to now
            return time.time() - self.start_time
        
        return self.end_time - self.start_time


class LazyLoader:
    """
    Utility class for lazy loading of objects.
    
    Usage:
        expensive_operation = LazyLoader(lambda: perform_expensive_initialization())
        # The initialization happens only when the object is first called
        result = expensive_operation()
    """
    def __init__(self, loader_func: typing.Callable):
        """
        Initialize a new LazyLoader instance.
        
        Args:
            loader_func: Function that creates the object when needed
        """
        self._loader_func = loader_func
        self._cached_obj = None
        self._initialized = False
    
    def __call__(self):
        """
        Called when the lazy loader is invoked.
        
        Returns:
            The loaded object
        """
        if not self._initialized:
            self._cached_obj = self._loader_func()
            self._initialized = True
        return self._cached_obj
    
    def reset(self) -> None:
        """
        Resets the lazy loader, forcing a reload on next call.
        """
        self._cached_obj = None
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """
        Checks if the object has been loaded.
        
        Returns:
            True if initialized, False otherwise
        """
        return self._initialized