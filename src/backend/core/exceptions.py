"""
Exception classes for the Freight Price Movement Agent application.

This module defines custom exception classes for the Freight Price Movement Agent
to provide structured error handling across the application. Each exception type
represents a specific category of error, enabling consistent error reporting and
appropriate response strategies based on the error type.
"""

from typing import Optional, Dict, Any


class ApplicationException(Exception):
    """Base exception class for all application-specific exceptions.
    
    This serves as the parent class for all specialized exceptions within the application,
    providing common functionality for error details and original exception tracking.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the ApplicationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing additional error context
            original_exception: Optional original exception that was caught
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception
    
    def __str__(self) -> str:
        """Return a string representation of the exception.
        
        Returns:
            String representation including the message and any details
        """
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ValidationException(ApplicationException):
    """Exception raised when data validation fails.
    
    Used for invalid input data, schema violations, and business rule constraints.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the ValidationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing validation errors
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class NotFoundException(ApplicationException):
    """Exception raised when a requested resource is not found.
    
    Used when a specific entity or data record cannot be located.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the NotFoundException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing resource identification details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class DataSourceException(ApplicationException):
    """Exception raised when there are issues with data sources.
    
    Used for connection failures, data retrieval errors, and format issues from external data sources.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the DataSourceException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing data source details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class AnalysisException(ApplicationException):
    """Exception raised when there are issues with price movement analysis.
    
    Used for calculation errors, algorithm failures, and invalid analysis parameters.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the AnalysisException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing analysis details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class ConfigurationException(ApplicationException):
    """Exception raised when there are issues with application configuration.
    
    Used for missing or invalid configuration settings.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the ConfigurationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing configuration details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class AuthenticationException(ApplicationException):
    """Exception raised when there are issues with user authentication.
    
    Used for login failures, invalid credentials, and session expiration.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the AuthenticationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing authentication details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class AuthorizationException(ApplicationException):
    """Exception raised when a user lacks permission for an operation.
    
    Used for access control violations and insufficient privileges.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the AuthorizationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing authorization details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)


class IntegrationException(ApplicationException):
    """Exception raised when there are issues with external system integration.
    
    Used for API failures, connection timeouts, and third-party service errors.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 original_exception: Optional[Exception] = None):
        """Initialize the IntegrationException.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing integration details
            original_exception: Optional original exception that was caught
        """
        super().__init__(message, details, original_exception)