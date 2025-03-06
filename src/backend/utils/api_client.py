#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP client module for the Freight Price Movement Agent.

This module provides robust API client classes for making HTTP requests to external
systems with features like retry logic, error handling, authentication, and
response processing. It supports various authentication methods including Basic Auth,
OAuth 2.0, and API keys.
"""

import json
import time
import base64
from typing import Dict, List, Optional, Any, Union, Tuple

import requests
from requests.auth import AuthBase, HTTPBasicAuth
import requests.exceptions
import requests.adapters
from urllib3.util import Retry

from ..core.config import settings
from ..core.logging import get_logger
from ..core.exceptions import IntegrationException

# Initialize logger
logger = get_logger(__name__)

# Default timeout values
DEFAULT_TIMEOUT = settings.API_REQUEST_TIMEOUT
DEFAULT_CONNECTION_TIMEOUT = settings.API_CONNECTION_TIMEOUT
MAX_RETRIES = settings.API_RETRY_MAX_ATTEMPTS
BACKOFF_FACTOR = settings.API_RETRY_BACKOFF_FACTOR


def create_retry_session(max_retries: int = MAX_RETRIES, 
                        backoff_factor: float = BACKOFF_FACTOR, 
                        status_forcelist: List[int] = None) -> requests.Session:
    """
    Creates a requests session with retry capabilities.
    
    Args:
        max_retries: Maximum number of retries
        backoff_factor: Backoff factor for exponential backoff
        status_forcelist: List of status codes to retry on
        
    Returns:
        Session with retry configuration
    """
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
    )
    
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def handle_response_errors(response: requests.Response) -> None:
    """
    Checks response for errors and raises appropriate exceptions.
    
    Args:
        response: Response to check
        
    Raises:
        IntegrationException: If the response contains an error
    """
    if not response.ok:
        error_details = {
            "status_code": response.status_code,
            "url": response.url,
            "method": response.request.method if response.request else None,
        }
        
        try:
            error_details["response_body"] = response.json()
        except ValueError:
            error_details["response_body"] = response.text[:1000] if response.text else None
        
        if response.status_code == 401:
            raise IntegrationException("Authentication failed", details=error_details)
        elif response.status_code == 403:
            raise IntegrationException("Authorization failed", details=error_details)
        elif response.status_code == 404:
            raise IntegrationException("Resource not found", details=error_details)
        elif response.status_code == 429:
            raise IntegrationException("Rate limit exceeded", details=error_details)
        elif 500 <= response.status_code < 600:
            raise IntegrationException("Server error", details=error_details)
        else:
            raise IntegrationException(f"HTTP error {response.status_code}", details=error_details)


class APIClient:
    """
    HTTP client for making API requests with retry logic and error handling.
    """
    
    def __init__(self, base_url: str, 
                headers: Optional[Dict[str, str]] = None, 
                auth: Optional[AuthBase] = None, 
                timeout: Optional[int] = None, 
                max_retries: Optional[int] = None, 
                backoff_factor: Optional[float] = None):
        """
        Initializes a new APIClient instance.
        
        Args:
            base_url: Base URL for API requests
            headers: Default headers for requests
            auth: Authentication handler
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': f'FreightPriceMovementAgent/1.0.0',
        }
        
        if headers:
            self.default_headers.update(headers)
        
        max_retries = max_retries if max_retries is not None else MAX_RETRIES
        backoff_factor = backoff_factor if backoff_factor is not None else BACKOFF_FACTOR
        
        self.session = create_retry_session(max_retries, backoff_factor)
        
        if auth:
            self.session.auth = auth
            
        logger.info(f"Initialized API client for {base_url}")
    
    def request(self, method: str, endpoint: str, 
               params: Optional[Dict[str, Any]] = None, 
               data: Optional[Dict[str, Any]] = None, 
               json_data: Optional[Dict[str, Any]] = None, 
               headers: Optional[Dict[str, str]] = None, 
               timeout: Optional[int] = None) -> requests.Response:
        """
        Makes an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
            
        Raises:
            IntegrationException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        timeout_value = timeout or self.timeout
        
        logger.debug(f"Making {method} request to {url} with params: {params}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=(DEFAULT_CONNECTION_TIMEOUT, timeout_value)
            )
            
            handle_response_errors(response)
            
            logger.debug(f"Received response from {url}: status={response.status_code}, time={response.elapsed.total_seconds():.3f}s")
            
            return response
        except requests.exceptions.RequestException as e:
            error_details = {
                "url": url,
                "method": method,
                "params": params,
            }
            
            if isinstance(e, requests.exceptions.Timeout):
                message = f"Request to {url} timed out after {timeout_value}s"
            elif isinstance(e, requests.exceptions.ConnectionError):
                message = f"Failed to connect to {url}"
            else:
                message = f"Request to {url} failed: {str(e)}"
                
            logger.error(message, exc_info=True)
            raise IntegrationException(message, details=error_details, original_exception=e)
    
    def get(self, endpoint: str, 
           params: Optional[Dict[str, Any]] = None, 
           headers: Optional[Dict[str, str]] = None, 
           timeout: Optional[int] = None) -> requests.Response:
        """
        Makes a GET request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
        """
        return self.request('GET', endpoint, params=params, headers=headers, timeout=timeout)
    
    def post(self, endpoint: str, 
            data: Optional[Dict[str, Any]] = None, 
            json_data: Optional[Dict[str, Any]] = None, 
            params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, 
            timeout: Optional[int] = None) -> requests.Response:
        """
        Makes a POST request to the API.
        
        Args:
            endpoint: API endpoint to call
            data: Form data
            json_data: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
        """
        return self.request('POST', endpoint, params=params, data=data, json_data=json_data, headers=headers, timeout=timeout)
    
    def put(self, endpoint: str, 
           data: Optional[Dict[str, Any]] = None, 
           json_data: Optional[Dict[str, Any]] = None, 
           params: Optional[Dict[str, Any]] = None, 
           headers: Optional[Dict[str, str]] = None, 
           timeout: Optional[int] = None) -> requests.Response:
        """
        Makes a PUT request to the API.
        
        Args:
            endpoint: API endpoint to call
            data: Form data
            json_data: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
        """
        return self.request('PUT', endpoint, params=params, data=data, json_data=json_data, headers=headers, timeout=timeout)
    
    def delete(self, endpoint: str, 
              params: Optional[Dict[str, Any]] = None, 
              headers: Optional[Dict[str, str]] = None, 
              timeout: Optional[int] = None) -> requests.Response:
        """
        Makes a DELETE request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
        """
        return self.request('DELETE', endpoint, params=params, headers=headers, timeout=timeout)
    
    def get_json(self, endpoint: str, 
                params: Optional[Dict[str, Any]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Makes a GET request and returns the JSON response.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON response data
            
        Raises:
            IntegrationException: If the response is not valid JSON
        """
        response = self.get(endpoint, params=params, headers=headers, timeout=timeout)
        try:
            return response.json()
        except ValueError as e:
            raise IntegrationException(
                f"Invalid JSON response from {endpoint}",
                details={"url": response.url, "status_code": response.status_code, "response_text": response.text[:1000]},
                original_exception=e
            )
    
    def post_json(self, endpoint: str, 
                 json_data: Optional[Dict[str, Any]] = None, 
                 params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None, 
                 timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Makes a POST request with JSON data and returns the JSON response.
        
        Args:
            endpoint: API endpoint to call
            json_data: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON response data
            
        Raises:
            IntegrationException: If the response is not valid JSON
        """
        response = self.post(endpoint, json_data=json_data, params=params, headers=headers, timeout=timeout)
        try:
            return response.json()
        except ValueError as e:
            raise IntegrationException(
                f"Invalid JSON response from {endpoint}",
                details={"url": response.url, "status_code": response.status_code, "response_text": response.text[:1000]},
                original_exception=e
            )
    
    def put_json(self, endpoint: str, 
                json_data: Optional[Dict[str, Any]] = None, 
                params: Optional[Dict[str, Any]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Makes a PUT request with JSON data and returns the JSON response.
        
        Args:
            endpoint: API endpoint to call
            json_data: JSON data
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON response data
            
        Raises:
            IntegrationException: If the response is not valid JSON
        """
        response = self.put(endpoint, json_data=json_data, params=params, headers=headers, timeout=timeout)
        try:
            return response.json()
        except ValueError as e:
            raise IntegrationException(
                f"Invalid JSON response from {endpoint}",
                details={"url": response.url, "status_code": response.status_code, "response_text": response.text[:1000]},
                original_exception=e
            )
    
    def close(self) -> None:
        """
        Closes the API client session.
        """
        if self.session:
            self.session.close()
            logger.debug("Closed API client session")
    
    def __enter__(self) -> 'APIClient':
        """
        Context manager entry point.
        
        Returns:
            Self
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit point.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()
        logger.debug("Exited API client context manager")


class OAuth2Client(APIClient):
    """
    API client with OAuth 2.0 authentication support.
    """
    
    def __init__(self, base_url: str, 
                token_url: str, 
                client_id: str, 
                client_secret: str, 
                scope: Optional[str] = None, 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None, 
                max_retries: Optional[int] = None, 
                backoff_factor: Optional[float] = None):
        """
        Initializes a new OAuth2Client instance.
        
        Args:
            base_url: Base URL for API requests
            token_url: URL for token acquisition
            client_id: OAuth client ID
            client_secret: OAuth client secret
            scope: OAuth scope
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
        """
        super().__init__(base_url, headers=headers, timeout=timeout, 
                         max_retries=max_retries, backoff_factor=backoff_factor)
        
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.token_data = None
        self.token_expiry = 0
        
        logger.info(f"Initialized OAuth2 client for {base_url} with client_id {client_id}")
    
    def fetch_token(self, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetches an OAuth 2.0 access token.
        
        Args:
            additional_params: Additional parameters for token request
            
        Returns:
            Token data including access_token
            
        Raises:
            IntegrationException: If token acquisition fails
        """
        token_request_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        if self.scope:
            token_request_data['scope'] = self.scope
        
        if additional_params:
            token_request_data.update(additional_params)
        
        try:
            logger.debug(f"Fetching OAuth token from {self.token_url}")
            token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            response = self.session.post(
                self.token_url, 
                data=token_request_data,
                headers=token_headers,
                timeout=(DEFAULT_CONNECTION_TIMEOUT, self.timeout)
            )
            
            handle_response_errors(response)
            
            token_data = response.json()
            if 'access_token' not in token_data:
                raise IntegrationException(
                    "Invalid token response",
                    details={"token_url": self.token_url, "response": token_data}
                )
            
            self.token_data = token_data
            
            # Calculate token expiry time
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            self.token_expiry = time.time() + expires_in - 60  # Subtract 60 seconds as buffer
            
            logger.info(f"Successfully obtained OAuth token, expires in {expires_in} seconds")
            return token_data
            
        except Exception as e:
            if isinstance(e, IntegrationException):
                raise
            
            error_details = {"token_url": self.token_url, "client_id": self.client_id}
            logger.error(f"Failed to fetch OAuth token: {str(e)}", exc_info=True)
            raise IntegrationException("Failed to fetch OAuth token", details=error_details, original_exception=e)
    
    def is_token_valid(self) -> bool:
        """
        Checks if the current token is valid and not expired.
        
        Returns:
            True if token is valid, False otherwise
        """
        return self.token_data is not None and time.time() < self.token_expiry
    
    def ensure_valid_token(self) -> Dict[str, Any]:
        """
        Ensures a valid token is available, fetching a new one if needed.
        
        Returns:
            Valid token data
        """
        if not self.is_token_valid():
            self.fetch_token()
        return self.token_data
    
    def request(self, method: str, endpoint: str, 
               params: Optional[Dict[str, Any]] = None, 
               data: Optional[Dict[str, Any]] = None, 
               json_data: Optional[Dict[str, Any]] = None, 
               headers: Optional[Dict[str, str]] = None, 
               timeout: Optional[int] = None) -> requests.Response:
        """
        Makes an authenticated HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
        """
        # Ensure we have a valid token
        token_data = self.ensure_valid_token()
        
        # Add authorization header
        auth_headers = {'Authorization': f"Bearer {token_data['access_token']}"}
        if headers:
            auth_headers.update(headers)
        
        try:
            return super().request(method, endpoint, params, data, json_data, auth_headers, timeout)
        except IntegrationException as e:
            # If authentication fails, try to refresh the token and retry once
            if hasattr(e, 'details') and isinstance(e.details, dict) and e.details.get('status_code') == 401:
                logger.info("OAuth token expired, refreshing and retrying request")
                self.token_expiry = 0  # Force token refresh
                token_data = self.ensure_valid_token()
                
                auth_headers = {'Authorization': f"Bearer {token_data['access_token']}"}
                if headers:
                    auth_headers.update(headers)
                
                return super().request(method, endpoint, params, data, json_data, auth_headers, timeout)
            raise


class BasicAuthClient(APIClient):
    """
    API client with HTTP Basic Authentication support.
    """
    
    def __init__(self, base_url: str, 
                username: str, 
                password: str, 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None, 
                max_retries: Optional[int] = None, 
                backoff_factor: Optional[float] = None):
        """
        Initializes a new BasicAuthClient instance.
        
        Args:
            base_url: Base URL for API requests
            username: Authentication username
            password: Authentication password
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
        """
        auth = HTTPBasicAuth(username, password)
        super().__init__(base_url, headers=headers, auth=auth, timeout=timeout, 
                         max_retries=max_retries, backoff_factor=backoff_factor)
        
        logger.info(f"Initialized BasicAuth client for {base_url} with username {username}")


class ApiKeyClient(APIClient):
    """
    API client with API key authentication support.
    """
    
    def __init__(self, base_url: str, 
                api_key: str, 
                header_name: str = "X-API-Key", 
                headers: Optional[Dict[str, str]] = None, 
                timeout: Optional[int] = None, 
                max_retries: Optional[int] = None, 
                backoff_factor: Optional[float] = None):
        """
        Initializes a new ApiKeyClient instance.
        
        Args:
            base_url: Base URL for API requests
            api_key: API key for authentication
            header_name: Name of the header for the API key
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
        """
        api_headers = {header_name: api_key}
        if headers:
            api_headers.update(headers)
            
        super().__init__(base_url, headers=api_headers, timeout=timeout, 
                         max_retries=max_retries, backoff_factor=backoff_factor)
        
        logger.info(f"Initialized ApiKey client for {base_url} with header {header_name}")