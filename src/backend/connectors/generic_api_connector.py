#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic API connector module for the Freight Price Movement Agent.

This module provides a standardized interface for connecting to external APIs,
executing requests, and transforming the results into a consistent format for
freight pricing data analysis.
"""

import json
from typing import Dict, List, Optional, Any, Union, Tuple

import pandas as pd  # version 1.5.x
import requests  # version 2.28.x

from ..core.config import settings
from ..core.logging import getLogger
from ..core.exceptions import IntegrationException, DataSourceException
from ..utils.api_client import APIClient, OAuth2Client

# Initialize logger
logger = getLogger(__name__)

# Default timeout for API requests
DEFAULT_TIMEOUT = settings.API_REQUEST_TIMEOUT


def validate_api_connection_params(connection_params: Dict) -> bool:
    """
    Validates that the API connection parameters contain all required fields.

    Args:
        connection_params: Dictionary containing connection parameters

    Returns:
        True if parameters are valid, raises exception otherwise

    Raises:
        DataSourceException: If required parameters are missing or invalid
    """
    if not isinstance(connection_params, dict):
        raise DataSourceException("Connection parameters must be a dictionary")

    # Check for required parameters
    if 'api_url' not in connection_params:
        raise DataSourceException("Missing required parameter: api_url")

    # Check authentication parameters based on auth_type
    auth_type = connection_params.get('auth_type', 'none').lower()
    
    if auth_type == 'basic':
        if 'username' not in connection_params:
            raise DataSourceException("Missing required parameter for basic auth: username")
        if 'password' not in connection_params:
            raise DataSourceException("Missing required parameter for basic auth: password")
    elif auth_type == 'oauth2':
        if 'client_id' not in connection_params:
            raise DataSourceException("Missing required parameter for OAuth2: client_id")
        if 'client_secret' not in connection_params:
            raise DataSourceException("Missing required parameter for OAuth2: client_secret")
        if 'token_url' not in connection_params:
            raise DataSourceException("Missing required parameter for OAuth2: token_url")
    elif auth_type == 'api_key':
        if 'api_key' not in connection_params:
            raise DataSourceException("Missing required parameter for API key auth: api_key")
        if 'header_name' not in connection_params:
            raise DataSourceException("Missing required parameter for API key auth: header_name")
    
    return True


def create_api_connector(api_type: str, connection_params: Dict) -> 'GenericAPIConnector':
    """
    Factory function to create the appropriate API connector based on the API type.

    Args:
        api_type: Type of API ('rest', 'soap', 'graphql')
        connection_params: Dictionary containing connection parameters

    Returns:
        An instance of the appropriate GenericAPIConnector subclass

    Raises:
        DataSourceException: If the API type is unsupported or parameters are invalid
    """
    try:
        if not api_type:
            raise DataSourceException("API type must be specified")
        
        # Validate connection parameters
        validate_api_connection_params(connection_params)
        
        api_type = api_type.lower()
        
        if api_type == 'rest':
            connector = RESTAPIConnector(connection_params)
        elif api_type == 'soap':
            connector = SOAPAPIConnector(connection_params)
        elif api_type == 'graphql':
            connector = GraphQLAPIConnector(connection_params)
        else:
            raise DataSourceException(f"Unsupported API type: {api_type}")
        
        logger.info(f"Created {api_type} API connector")
        return connector
        
    except DataSourceException:
        # Re-raise DataSourceException
        raise
    except Exception as e:
        # Wrap other exceptions in DataSourceException
        raise DataSourceException(
            f"Error creating API connector: {str(e)}",
            details={"api_type": api_type},
            original_exception=e
        )


def map_api_response(response_data: Dict, field_mapping: Dict) -> Dict:
    """
    Maps API response fields to standardized field names used by the system.

    Args:
        response_data: Original response data from the API
        field_mapping: Dictionary mapping source field names to target field names

    Returns:
        Mapped response data with standardized field names

    Raises:
        DataSourceException: If required fields are missing in the mapping or response
    """
    # Check if field_mapping contains mappings for all required fields
    required_fields = ['freight_charge', 'currency', 'origin', 'destination', 'date']
    missing_fields = [field for field in required_fields if field not in field_mapping.values()]
    
    if missing_fields:
        raise DataSourceException(
            f"Field mapping is missing required fields: {', '.join(missing_fields)}",
            details={"field_mapping": field_mapping}
        )
    
    mapped_data = {}
    
    # Apply field mapping
    for source_field, target_field in field_mapping.items():
        if source_field in response_data:
            mapped_data[target_field] = response_data[source_field]
        else:
            # Log warning for missing fields but don't fail
            logger.warning(f"Field '{source_field}' not found in API response")
    
    logger.debug(f"Mapped API response fields: {list(mapped_data.keys())}")
    
    return mapped_data


class GenericAPIConnector:
    """
    Base class for connecting to and retrieving data from external APIs.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new GenericAPIConnector instance.

        Args:
            connection_params: Dictionary containing connection parameters

        Raises:
            DataSourceException: If required parameters are missing or invalid
        """
        # Validate connection parameters
        validate_api_connection_params(connection_params)
        
        self.connection_params = connection_params
        self.api_url = connection_params['api_url']
        self.auth_type = connection_params.get('auth_type', 'none').lower()
        self.api_client = None
        self.connected = False
        
        logger.info(f"Initialized API connector for {self.api_url}")
    
    def connect(self, timeout: Optional[int] = None) -> bool:
        """
        Establishes a connection to the API.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        
        Raises:
            DataSourceException: If connection fails
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            logger.info(f"Connecting to API at {self.api_url}")
            
            # Create appropriate API client based on auth_type
            if self.auth_type == 'none':
                self.api_client = APIClient(base_url=self.api_url, timeout=timeout)
            
            elif self.auth_type == 'basic':
                username = self.connection_params['username']
                password = self.connection_params['password']
                self.api_client = APIClient(
                    base_url=self.api_url,
                    auth=requests.auth.HTTPBasicAuth(username, password),
                    timeout=timeout
                )
            
            elif self.auth_type == 'oauth2':
                client_id = self.connection_params['client_id']
                client_secret = self.connection_params['client_secret']
                token_url = self.connection_params['token_url']
                scope = self.connection_params.get('scope')
                
                self.api_client = OAuth2Client(
                    base_url=self.api_url,
                    token_url=token_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    scope=scope,
                    timeout=timeout
                )
                # Fetch token to verify connection
                self.api_client.fetch_token()
            
            elif self.auth_type == 'api_key':
                api_key = self.connection_params['api_key']
                header_name = self.connection_params.get('header_name', 'X-API-Key')
                headers = {header_name: api_key}
                self.api_client = APIClient(base_url=self.api_url, headers=headers, timeout=timeout)
            
            else:
                raise DataSourceException(f"Unsupported authentication type: {self.auth_type}")
            
            # Test connection with a simple request if a test_endpoint is provided
            test_endpoint = self.connection_params.get('test_endpoint')
            if test_endpoint:
                self.api_client.get(endpoint=test_endpoint)
            
            self.connected = True
            logger.info(f"Successfully connected to API at {self.api_url}")
            return True
            
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to API at {self.api_url}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to connect to API at {self.api_url}: {str(e)}",
                details={"api_url": self.api_url, "auth_type": self.auth_type},
                original_exception=e
            )
    
    def disconnect(self) -> bool:
        """
        Closes the API connection.
        
        Returns:
            True if disconnection successful
        """
        try:
            if self.api_client:
                self.api_client.close()
                self.api_client = None
            
            self.connected = False
            logger.info(f"Disconnected from API at {self.api_url}")
            return True
        
        except Exception as e:
            logger.error(f"Error disconnecting from API at {self.api_url}: {str(e)}", exc_info=True)
            return False
    
    def test_connection(self, timeout: Optional[int] = None) -> bool:
        """
        Tests the API connection.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.connect(timeout=timeout)
            self.disconnect()
            return result
        except Exception as e:
            logger.error(f"Connection test failed for {self.api_url}: {str(e)}", exc_info=True)
            return False
    
    def execute_request(self, method: str, endpoint: str, 
                        params: Optional[Dict] = None,
                        data: Optional[Dict] = None,
                        headers: Optional[Dict] = None,
                        timeout: Optional[int] = None) -> requests.Response:
        """
        Executes an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            params: Query parameters
            data: Request body data
            headers: Additional request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response from the API
            
        Raises:
            DataSourceException: If the request fails
        """
        if not self.connected:
            self.connect()
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            logger.debug(f"Executing {method} request to {endpoint}")
            response = self.api_client.request(
                method=method,
                endpoint=endpoint,
                params=params,
                json_data=data,
                headers=headers,
                timeout=timeout
            )
            return response
        
        except Exception as e:
            logger.error(f"API request failed: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"API request failed: {str(e)}",
                details={"method": method, "endpoint": endpoint, "params": params},
                original_exception=e
            )
    
    def get_data(self, endpoint: str, 
                params: Optional[Dict] = None,
                headers: Optional[Dict] = None,
                timeout: Optional[int] = None) -> Dict:
        """
        Retrieves data from the API using a GET request.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Additional request headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON response data
            
        Raises:
            DataSourceException: If the request fails
        """
        if not self.connected:
            self.connect()
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            logger.debug(f"Getting data from {endpoint}")
            return self.api_client.get_json(
                endpoint=endpoint,
                params=params,
                headers=headers,
                timeout=timeout
            )
        
        except Exception as e:
            logger.error(f"Failed to get data from {endpoint}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to get data from {endpoint}: {str(e)}",
                details={"endpoint": endpoint, "params": params},
                original_exception=e
            )
    
    def post_data(self, endpoint: str, 
                 json_data: Optional[Dict] = None,
                 params: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 timeout: Optional[int] = None) -> Dict:
        """
        Sends data to the API using a POST request.
        
        Args:
            endpoint: API endpoint to call
            json_data: JSON data to send
            params: Query parameters
            headers: Additional request headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON response data
            
        Raises:
            DataSourceException: If the request fails
        """
        if not self.connected:
            self.connect()
        
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            logger.debug(f"Posting data to {endpoint}")
            return self.api_client.post_json(
                endpoint=endpoint,
                json_data=json_data,
                params=params,
                headers=headers,
                timeout=timeout
            )
        
        except Exception as e:
            logger.error(f"Failed to post data to {endpoint}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to post data to {endpoint}: {str(e)}",
                details={"endpoint": endpoint, "params": params},
                original_exception=e
            )
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None,
                          field_mapping: Optional[Dict] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from the API.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of API fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        raise NotImplementedError("Subclasses must implement fetch_freight_data method")
    
    def paginate_results(self, endpoint: str, params: Dict, 
                        data_key: str, next_page_key: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict]:
        """
        Handles paginated API responses.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            data_key: Key in the response that contains the data
            next_page_key: Key in the response that indicates if there are more pages
            limit: Maximum number of records to return
            
        Returns:
            Combined results from all pages
            
        Raises:
            DataSourceException: If the pagination fails
        """
        all_results = []
        current_page = 1
        
        # Initialize parameters with page=1
        page_params = params.copy()
        page_params['page'] = current_page
        
        try:
            logger.info(f"Fetching paginated results from {endpoint}")
            
            while True:
                # Get data for the current page
                response = self.get_data(endpoint, params=page_params)
                
                # Extract data using data_key
                if data_key in response:
                    page_data = response[data_key]
                    all_results.extend(page_data)
                    logger.debug(f"Retrieved page {current_page} with {len(page_data)} records")
                else:
                    raise DataSourceException(
                        f"Data key '{data_key}' not found in API response",
                        details={"response_keys": list(response.keys())}
                    )
                
                # Check if we've reached the limit
                if limit and len(all_results) >= limit:
                    all_results = all_results[:limit]
                    break
                
                # Check if there are more pages
                if next_page_key and next_page_key in response:
                    has_more = response[next_page_key]
                    if not has_more:
                        break
                else:
                    # If next_page_key is not provided, check if the current page has data
                    if not page_data:
                        break
                
                # Move to the next page
                current_page += 1
                page_params['page'] = current_page
            
            logger.info(f"Retrieved {len(all_results)} total records from paginated API")
            return all_results
            
        except Exception as e:
            logger.error(f"Failed to paginate results: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to paginate results: {str(e)}",
                details={"endpoint": endpoint, "params": params},
                original_exception=e
            )
    
    def __enter__(self) -> 'GenericAPIConnector':
        """
        Context manager entry point.
        
        Returns:
            Self
        """
        if not self.connected:
            self.connect()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit point.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.disconnect()
        logger.debug("Exited API connector context")


class RESTAPIConnector(GenericAPIConnector):
    """
    Specialized connector for REST APIs.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new RESTAPIConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None,
                          field_mapping: Optional[Dict] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from a REST API.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of API fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Extract endpoint from connection_params or use default
            endpoint = self.connection_params.get('data_endpoint', 'freight/rates')
            
            # Extract data_key from connection_params or use default
            data_key = self.connection_params.get('data_key', 'data')
            
            # Check if pagination is enabled
            use_pagination = self.connection_params.get('use_pagination', False)
            next_page_key = self.connection_params.get('next_page_key')
            
            # Fetch data (with pagination if enabled)
            if use_pagination:
                response_data = self.paginate_results(
                    endpoint=endpoint,
                    params=query_params,
                    data_key=data_key,
                    next_page_key=next_page_key,
                    limit=limit
                )
            else:
                response = self.get_data(endpoint, params=query_params)
                if data_key in response:
                    response_data = response[data_key]
                else:
                    raise DataSourceException(
                        f"Data key '{data_key}' not found in API response",
                        details={"response_keys": list(response.keys())}
                    )
            
            # Map API fields to standard fields
            mapped_data = []
            for item in response_data:
                mapped_item = map_api_response(item, field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified
            if limit and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from REST API")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data: {str(e)}",
                details={"endpoint": endpoint, "params": query_params},
                original_exception=e
            )


class SOAPAPIConnector(GenericAPIConnector):
    """
    Specialized connector for SOAP APIs.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new SOAPAPIConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
        self.wsdl_url = connection_params.get('wsdl_url', self.api_url)
        self.soap_client = None
    
    def connect(self, timeout: Optional[int] = None) -> bool:
        """
        Establishes a connection to the SOAP API.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            DataSourceException: If connection fails
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        
        try:
            logger.info(f"Connecting to SOAP API at {self.wsdl_url}")
            
            # Import zeep here to avoid making it a hard dependency
            try:
                from zeep import Client
                from zeep.transports import Transport
                from requests import Session
            except ImportError:
                raise DataSourceException(
                    "Zeep library is required for SOAP API connections. Install with: pip install zeep"
                )
            
            # Create a session with appropriate timeout
            session = Session()
            session.verify = self.connection_params.get('verify_ssl', True)
            transport = Transport(session=session, timeout=timeout)
            
            # Create the SOAP client
            self.soap_client = Client(self.wsdl_url, transport=transport)
            
            # Configure authentication
            if self.auth_type == 'basic':
                username = self.connection_params['username']
                password = self.connection_params['password']
                session.auth = requests.auth.HTTPBasicAuth(username, password)
            
            elif self.auth_type == 'oauth2' or self.auth_type == 'api_key':
                # For OAuth2 and API key auth, we need a regular API client for token management
                super().connect(timeout)
                
                # For each SOAP request, we'll need to add the appropriate headers
                # This is handled in execute_soap_operation
            
            # Test the connection if a test_operation is provided
            test_operation = self.connection_params.get('test_operation')
            if test_operation:
                self.execute_soap_operation(test_operation)
            
            self.connected = True
            logger.info(f"Successfully connected to SOAP API at {self.wsdl_url}")
            return True
            
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to SOAP API at {self.wsdl_url}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to connect to SOAP API at {self.wsdl_url}: {str(e)}",
                details={"wsdl_url": self.wsdl_url, "auth_type": self.auth_type},
                original_exception=e
            )
    
    def disconnect(self) -> bool:
        """
        Closes the SOAP API connection.
        
        Returns:
            True if disconnection successful
        """
        try:
            self.soap_client = None
            self.connected = False
            
            # Also disconnect the API client if it was created
            super().disconnect()
            
            logger.info(f"Disconnected from SOAP API at {self.wsdl_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from SOAP API: {str(e)}", exc_info=True)
            return False
    
    def execute_soap_operation(self, operation_name: str, 
                              parameters: Optional[Dict] = None) -> Dict:
        """
        Executes a SOAP operation.
        
        Args:
            operation_name: Name of the SOAP operation to execute
            parameters: Parameters for the operation
            
        Returns:
            Result of the SOAP operation
            
        Raises:
            DataSourceException: If the operation execution fails
        """
        if not self.connected:
            self.connect()
        
        try:
            logger.debug(f"Executing SOAP operation {operation_name}")
            
            parameters = parameters or {}
            
            # Get the operation from the SOAP client
            operation = getattr(self.soap_client.service, operation_name)
            
            # Execute the operation
            result = operation(**parameters)
            
            # Convert the result to a dictionary
            from zeep.helpers import serialize_object
            result_dict = serialize_object(result)
            
            return result_dict
            
        except Exception as e:
            logger.error(f"Failed to execute SOAP operation {operation_name}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to execute SOAP operation {operation_name}: {str(e)}",
                details={"operation": operation_name, "parameters": parameters},
                original_exception=e
            )
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None,
                          field_mapping: Optional[Dict] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from a SOAP API.
        
        Args:
            query_params: Parameters for the SOAP operation
            field_mapping: Mapping of API fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Extract operation name from connection_params or use default
            operation_name = self.connection_params.get('data_operation', 'GetFreightRates')
            
            # Extract data key from connection_params or use default
            data_key = self.connection_params.get('data_key', 'FreightRates')
            
            # Execute the SOAP operation
            result = self.execute_soap_operation(operation_name, query_params)
            
            # Extract data using data_key
            if data_key in result:
                response_data = result[data_key]
            else:
                raise DataSourceException(
                    f"Data key '{data_key}' not found in SOAP response",
                    details={"response_keys": list(result.keys())}
                )
            
            # Ensure response_data is a list
            if not isinstance(response_data, list):
                response_data = [response_data]
            
            # Map SOAP response fields to standard fields
            mapped_data = []
            for item in response_data:
                mapped_item = map_api_response(item, field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified
            if limit and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from SOAP API")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data from SOAP API: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data from SOAP API: {str(e)}",
                details={"operation": operation_name, "params": query_params},
                original_exception=e
            )


class GraphQLAPIConnector(GenericAPIConnector):
    """
    Specialized connector for GraphQL APIs.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new GraphQLAPIConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
    
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Executes a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Variables for the query
            
        Returns:
            GraphQL query result
            
        Raises:
            DataSourceException: If the query execution fails
        """
        if not self.connected:
            self.connect()
        
        try:
            logger.debug(f"Executing GraphQL query")
            
            variables = variables or {}
            
            # Prepare the GraphQL request payload
            payload = {
                'query': query,
                'variables': variables
            }
            
            # Execute the query using a POST request
            response = self.post_data('', json_data=payload)
            
            # Check for errors in the response
            if 'errors' in response:
                errors = response['errors']
                raise DataSourceException(
                    f"GraphQL query returned errors: {errors}",
                    details={"errors": errors, "query": query}
                )
            
            # Extract and return the data
            if 'data' in response:
                return response['data']
            else:
                raise DataSourceException(
                    "GraphQL response does not contain data",
                    details={"response": response}
                )
            
        except Exception as e:
            logger.error(f"Failed to execute GraphQL query: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to execute GraphQL query: {str(e)}",
                details={"query": query, "variables": variables},
                original_exception=e
            )
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None,
                          field_mapping: Optional[Dict] = None,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from a GraphQL API.
        
        Args:
            query_params: Variables for the GraphQL query
            field_mapping: Mapping of API fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Extract or construct the GraphQL query
            query = self.connection_params.get('graphql_query')
            if not query:
                query = query_params.get('query')
            
            if not query:
                # Construct a default query if none is provided
                query = """
                query FreightRates($limit: Int) {
                    freightRates(limit: $limit) {
                        origin
                        destination
                        carrier
                        freightCharge
                        currency
                        effectiveDate
                    }
                }
                """
            
            # Extract variables from query_params
            variables = query_params.get('variables', {})
            
            # Add limit to variables if specified
            if limit:
                variables['limit'] = limit
            
            # Execute the GraphQL query
            result = self.execute_query(query, variables)
            
            # Extract data from the result
            data_key = self.connection_params.get('data_key', 'freightRates')
            
            if data_key in result:
                response_data = result[data_key]
            else:
                raise DataSourceException(
                    f"Data key '{data_key}' not found in GraphQL response",
                    details={"response_keys": list(result.keys())}
                )
            
            # Map GraphQL response fields to standard fields
            mapped_data = []
            for item in response_data:
                mapped_item = map_api_response(item, field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified and not already applied in the query
            if limit and 'limit' not in variables and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from GraphQL API")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data from GraphQL API: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data from GraphQL API: {str(e)}",
                details={"query": query, "variables": variables},
                original_exception=e
            )