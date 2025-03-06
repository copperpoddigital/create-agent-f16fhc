"""
Centralized error handling service for the Freight Price Movement Agent.

This module provides standardized error handling, classification, recovery mechanisms,
and error response formatting across all application components.
"""

import traceback
import json
import time
import functools
from typing import Optional, Any, Dict, List, Tuple, Callable

from fastapi import HTTPException
from fastapi import status

from ..core.exceptions import (
    ApplicationException, ValidationException, NotFoundException, 
    DataSourceException, AnalysisException, ConfigurationException, 
    AuthenticationException, AuthorizationException, IntegrationException
)
from ..core.logging import logger, log_exception
from ..core.config import settings

# Constants for error handling
ERROR_RESPONSE_TEMPLATE = '{"status": "error", "message": "{message}", "details": {details}, "error_type": "{error_type}", "error_code": "{error_code}"}'

# Map exception types to error types
ERROR_TYPE_MAP = {
    ApplicationException: "application_error",
    ValidationException: "validation_error",
    NotFoundException: "not_found",
    DataSourceException: "data_source_error",
    AnalysisException: "analysis_error",
    ConfigurationException: "configuration_error",
    AuthenticationException: "authentication_error",
    AuthorizationException: "authorization_error",
    IntegrationException: "integration_error"
}

# Map exception types to HTTP status codes
HTTP_STATUS_MAP = {
    ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    NotFoundException: status.HTTP_404_NOT_FOUND,
    DataSourceException: status.HTTP_503_SERVICE_UNAVAILABLE,
    AnalysisException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ConfigurationException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    AuthenticationException: status.HTTP_401_UNAUTHORIZED,
    AuthorizationException: status.HTTP_403_FORBIDDEN,
    IntegrationException: status.HTTP_502_BAD_GATEWAY,
    ApplicationException: status.HTTP_500_INTERNAL_SERVER_ERROR
}

# Error code prefix for all application errors
ERROR_CODE_PREFIX = "FPMA"


def format_error_response(exception: Exception, include_traceback: Optional[bool] = None) -> dict:
    """
    Formats an exception into a standardized error response.
    
    Args:
        exception: The exception to format
        include_traceback: Whether to include the traceback in the response
    
    Returns:
        Standardized error response dictionary
    """
    # Determine error type based on exception class
    exception_type = type(exception)
    error_type_key = next((et for et in ERROR_TYPE_MAP if isinstance(exception, et)), None)
    error_type = ERROR_TYPE_MAP.get(error_type_key, "unknown_error")
    
    # Extract error message and details
    if isinstance(exception, ApplicationException):
        message = exception.message
        details = exception.details
    else:
        message = str(exception)
        details = {}
    
    # Generate error code
    error_code = generate_error_code(exception)
    
    # Include traceback in debug mode if requested
    if (include_traceback or settings.DEBUG) and include_traceback is not False:
        details["traceback"] = traceback.format_exc()
    
    # Format response using template
    response_str = ERROR_RESPONSE_TEMPLATE.format(
        message=message,
        details=json.dumps(details),
        error_type=error_type,
        error_code=error_code
    )
    
    # Parse into dictionary
    return json.loads(response_str)


def get_http_status_code(exception: Exception) -> int:
    """
    Maps an exception to the appropriate HTTP status code.
    
    Args:
        exception: The exception to map
    
    Returns:
        HTTP status code
    """
    # Check exception type hierarchy and find the most specific match
    for exception_type, status_code in HTTP_STATUS_MAP.items():
        if isinstance(exception, exception_type):
            return status_code
    
    # Default to internal server error if no match
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def create_http_exception(exception: Exception) -> HTTPException:
    """
    Creates a FastAPI HTTPException from an application exception.
    
    Args:
        exception: The application exception
    
    Returns:
        FastAPI HTTPException
    """
    # Get HTTP status code
    status_code = get_http_status_code(exception)
    
    # Format error response
    error_response = format_error_response(exception)
    
    # Create and return HTTPException
    return HTTPException(
        status_code=status_code,
        detail=error_response
    )


def handle_exception(exception: Exception, module_name: Optional[str] = None, 
                     context: Optional[str] = None) -> Tuple[dict, int]:
    """
    Central exception handler that logs and processes exceptions.
    
    Args:
        exception: The exception to handle
        module_name: The name of the module where the exception occurred
        context: Additional context information
    
    Returns:
        Tuple of (error_response, http_status_code)
    """
    # Log the exception
    log_exception(exception, module_name, context)
    
    # Format error response
    error_response = format_error_response(exception)
    
    # Get HTTP status code
    status_code = get_http_status_code(exception)
    
    # Return response and status code
    return error_response, status_code


def is_recoverable_error(exception: Exception) -> bool:
    """
    Determines if an error is recoverable and should be retried.
    
    Args:
        exception: The exception to check
    
    Returns:
        True if the error is recoverable, False otherwise
    """
    # Check if it's a known transient error type
    if isinstance(exception, (DataSourceException, IntegrationException)):
        # Check for specific error messages indicating transient issues
        error_msg = str(exception).lower()
        
        # Connection errors are typically transient
        if any(keyword in error_msg for keyword in ["connection", "timeout", "temporary", "retry"]):
            return True
    
    # Consider specific HTTP status codes as recoverable
    if hasattr(exception, 'status_code'):
        status_code = getattr(exception, 'status_code')
        # 429 (Too Many Requests), 503 (Service Unavailable), etc.
        if status_code in [429, 503, 502, 504]:
            return True
    
    # Default to non-recoverable
    return False


def with_retry(max_retries: Optional[int] = None, 
               backoff_factor: Optional[float] = None, 
               retry_exceptions: Optional[List[type]] = None):
    """
    Decorator that adds retry logic to functions that may experience transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts (default from settings)
        backoff_factor: Backoff factor for exponential delay (default from settings)
        retry_exceptions: List of exception types to retry (default is recoverable errors)
    
    Returns:
        Decorated function with retry logic
    """
    # Set defaults from settings if not provided
    if max_retries is None:
        max_retries = settings.MAX_RETRIES
    
    if backoff_factor is None:
        backoff_factor = settings.RETRY_BACKOFF_FACTOR
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if exception is retryable
                    should_retry = False
                    if retry_exceptions and isinstance(e, tuple(retry_exceptions)):
                        should_retry = True
                    elif is_recoverable_error(e):
                        should_retry = True
                    
                    # If not retryable or max retries reached, re-raise
                    if not should_retry or retry_count >= max_retries:
                        raise
                    
                    # Calculate backoff delay using exponential backoff
                    delay = backoff_factor * (2 ** retry_count)
                    
                    # Log retry attempt
                    logger.warning(
                        f"Retrying due to {type(e).__name__}: {str(e)}. "
                        f"Attempt {retry_count + 1}/{max_retries} after {delay:.2f}s"
                    )
                    
                    # Wait before retrying
                    time.sleep(delay)
                    
                    # Increment retry counter
                    retry_count += 1
            
            # This should not be reached due to the raise above, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func: Callable, default_value: Any, 
                 error_message: Optional[str] = None, 
                 module_name: Optional[str] = None,
                 raise_exception: Optional[bool] = False) -> Any:
    """
    Executes a function with error handling and returns a default value on failure.
    
    Args:
        func: The function to execute
        default_value: The default value to return on failure
        error_message: Custom error message to log
        module_name: Module name for logging
        raise_exception: Whether to re-raise the exception after logging
    
    Returns:
        Function result or default value on failure
    """
    try:
        # Attempt to execute the function
        return func()
    except Exception as e:
        # Log the error
        if error_message:
            log_exception(e, module_name, error_message)
        else:
            log_exception(e, module_name, f"Error executing {func.__name__}")
        
        # Re-raise if requested
        if raise_exception:
            raise
        
        # Return default value
        return default_value


class CircuitBreakerOpenException(Exception):
    """
    Exception raised when a circuit breaker is open.
    """
    def __init__(self, message: str, circuit_name: Optional[str] = None, 
                 reset_timeout: Optional[int] = None):
        super().__init__(message)
        self.circuit_name = circuit_name
        self.reset_timeout = reset_timeout


def circuit_breaker(failure_threshold: Optional[int] = 5, 
                    reset_timeout: Optional[int] = 60):
    """
    Implements circuit breaker pattern to prevent cascading failures.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        reset_timeout: Time in seconds before attempting to reset the circuit
    
    Returns:
        Decorator function implementing circuit breaker
    """
    # Circuit state constants
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    # Shared state for the decorator
    state = {
        'status': CLOSED,
        'failure_count': 0,
        'last_failure_time': 0,
        'circuit_name': None
    }
    
    def decorator(func):
        # Set circuit name based on function
        circuit_name = f"{func.__module__}.{func.__name__}"
        state['circuit_name'] = circuit_name
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check circuit state
            current_time = time.time()
            
            # If circuit is open, check if timeout has elapsed
            if state['status'] == OPEN:
                elapsed = current_time - state['last_failure_time']
                
                # If timeout has elapsed, transition to half-open
                if elapsed >= reset_timeout:
                    state['status'] = HALF_OPEN
                    logger.info(f"Circuit {circuit_name} transitioned from OPEN to HALF-OPEN")
                else:
                    # Circuit is still open, raise exception
                    remaining = reset_timeout - elapsed
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker for {circuit_name} is open",
                        circuit_name=circuit_name,
                        reset_timeout=int(remaining)
                    )
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # If successful and in half-open state, reset circuit
                if state['status'] == HALF_OPEN:
                    state['status'] = CLOSED
                    state['failure_count'] = 0
                    logger.info(f"Circuit {circuit_name} reset to CLOSED after successful execution")
                
                return result
            except Exception as e:
                # Increment failure count
                state['failure_count'] += 1
                state['last_failure_time'] = current_time
                
                # If failure count exceeds threshold, open the circuit
                if state['status'] != OPEN and state['failure_count'] >= failure_threshold:
                    state['status'] = OPEN
                    logger.warning(
                        f"Circuit {circuit_name} OPENED after {failure_threshold} failures. "
                        f"Last error: {type(e).__name__}: {str(e)}"
                    )
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator


def generate_error_code(exception: Exception) -> str:
    """
    Generates a unique error code for an exception.
    
    Args:
        exception: The exception to generate a code for
    
    Returns:
        Unique error code
    """
    # Determine error type
    error_type_key = next((et for et in ERROR_TYPE_MAP if isinstance(exception, et)), None)
    error_type = ERROR_TYPE_MAP.get(error_type_key, "UNK")
    
    # Generate a unique identifier based on exception details
    if isinstance(exception, ApplicationException):
        # Use details for more specific identification
        details_str = str(sorted(exception.details.items()) if exception.details else "")
        message = exception.message
    else:
        details_str = ""
        message = str(exception)
    
    # Create a hash from the message and details
    import hashlib
    hash_input = f"{message}{details_str}".encode('utf-8')
    hash_value = hashlib.md5(hash_input).hexdigest()[:6].upper()
    
    # Construct error code: PREFIX-TYPE-HASH
    return f"{ERROR_CODE_PREFIX}-{error_type[:3].upper()}-{hash_value}"


class ErrorHandler:
    """
    Central error handling service for the application.
    """
    
    def __init__(self):
        """
        Initializes the ErrorHandler.
        """
        # Initialize error count tracking
        self._error_counts = {}
        
        # Initialize circuit breaker states
        self._circuit_states = {}
    
    def handle_exception(self, exception: Exception, module_name: Optional[str] = None, 
                         context: Optional[str] = None) -> Tuple[dict, int]:
        """
        Handles an exception and returns appropriate response.
        
        Args:
            exception: The exception to handle
            module_name: The name of the module where the exception occurred
            context: Additional context information
        
        Returns:
            Tuple of (error_response, http_status_code)
        """
        # Track error occurrence for monitoring
        exception_type = type(exception).__name__
        self._error_counts[exception_type] = self._error_counts.get(exception_type, 0) + 1
        
        # Use the global handle_exception function
        return handle_exception(exception, module_name, context)
    
    def with_error_handling(self, default_value: Optional[Any] = None, 
                            error_message: Optional[str] = None, 
                            raise_exception: Optional[bool] = False):
        """
        Decorator that adds error handling to functions.
        
        Args:
            default_value: Value to return on error
            error_message: Custom error message to log
            raise_exception: Whether to re-raise the exception
        
        Returns:
            Decorated function with error handling
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Get module name from function
                    module_name = func.__module__
                    
                    # Handle the exception
                    self.handle_exception(e, module_name, error_message or f"Error in {func.__name__}")
                    
                    # Re-raise if requested
                    if raise_exception:
                        raise
                    
                    # Return default value
                    return default_value
            
            return wrapper
        
        return decorator
    
    def get_error_statistics(self) -> dict:
        """
        Returns statistics about errors that have occurred.
        
        Returns:
            Error statistics by type and frequency
        """
        total_errors = sum(self._error_counts.values())
        
        stats = {
            "total_errors": total_errors,
            "error_types": {
                error_type: {
                    "count": count,
                    "percentage": (count / total_errors * 100) if total_errors > 0 else 0
                }
                for error_type, count in self._error_counts.items()
            }
        }
        
        return stats
    
    def reset_statistics(self) -> None:
        """
        Resets error statistics counters.
        """
        self._error_counts = {}
        logger.info("Error statistics reset")
    
    def get_circuit_status(self) -> dict:
        """
        Returns the current status of all circuit breakers.
        
        Returns:
            Circuit breaker statuses
        """
        return {
            circuit_name: {
                "status": state.get("status", "unknown"),
                "failure_count": state.get("failure_count", 0),
                "last_failure_time": state.get("last_failure_time", 0)
            }
            for circuit_name, state in self._circuit_states.items()
        }
    
    def reset_circuit(self, circuit_name: str) -> bool:
        """
        Resets a specific circuit breaker to closed state.
        
        Args:
            circuit_name: Name of the circuit to reset
            
        Returns:
            True if reset was successful, False otherwise
        """
        if circuit_name in self._circuit_states:
            self._circuit_states[circuit_name] = {
                "status": "closed",
                "failure_count": 0,
                "last_failure_time": 0
            }
            logger.info(f"Circuit {circuit_name} manually reset to CLOSED")
            return True
        
        return False