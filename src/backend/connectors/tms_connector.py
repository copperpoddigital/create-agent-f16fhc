#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transportation Management System (TMS) connector module for the Freight Price Movement Agent.

This module provides specialized connectors for retrieving freight pricing data from various 
TMS platforms including SAP TM, Oracle TMS, and JDA TMS.
"""

import json
from typing import Dict, List, Optional, Any, Union, Tuple

import pandas as pd  # version 1.5.x
import requests  # version 2.28.x

from ..core.logging import getLogger
from ..core.config import settings
from ..core.exceptions import IntegrationException, DataSourceException
from ..utils.api_client import APIClient, OAuth2Client
from .generic_api_connector import GenericAPIConnector, RESTAPIConnector, SOAPAPIConnector

# Initialize logger
logger = getLogger(__name__)

# Default timeout for API requests
DEFAULT_TIMEOUT = settings.TMS_REQUEST_TIMEOUT

# Supported TMS types
TMS_TYPES = {
    "sap": "SAP TM",
    "oracle": "Oracle TMS",
    "jda": "JDA TMS"
}


def validate_tms_connection_params(connection_params: Dict) -> bool:
    """
    Validates that the TMS connection parameters contain all required fields.

    Args:
        connection_params: Dictionary containing connection parameters

    Returns:
        True if parameters are valid, raises exception otherwise

    Raises:
        DataSourceException: If required parameters are missing or invalid
    """
    if not isinstance(connection_params, dict):
        raise DataSourceException("Connection parameters must be a dictionary")

    # Check for required fields
    if 'tms_type' not in connection_params:
        raise DataSourceException("Missing required parameter: tms_type")
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

    # Verify TMS-specific parameters
    tms_type = connection_params['tms_type'].lower()
    
    if tms_type == 'sap':
        if 'system_id' not in connection_params:
            raise DataSourceException("Missing required parameter for SAP TM: system_id")
        if 'client_number' not in connection_params:
            raise DataSourceException("Missing required parameter for SAP TM: client_number")
    elif tms_type == 'oracle':
        if 'instance_id' not in connection_params:
            raise DataSourceException("Missing required parameter for Oracle TMS: instance_id")
    elif tms_type == 'jda':
        if 'environment' not in connection_params:
            raise DataSourceException("Missing required parameter for JDA TMS: environment")
    elif tms_type not in TMS_TYPES:
        raise DataSourceException(f"Unsupported TMS type: {tms_type}")

    return True


def create_tms_connector(connection_params: Dict) -> 'TMSConnector':
    """
    Factory function to create the appropriate TMS connector based on the TMS type.

    Args:
        connection_params: Dictionary containing connection parameters

    Returns:
        An instance of the appropriate TMSConnector subclass

    Raises:
        DataSourceException: If the TMS type is unsupported or parameters are invalid
    """
    try:
        # Validate connection parameters
        validate_tms_connection_params(connection_params)
        
        # Extract TMS type
        tms_type = connection_params['tms_type'].lower()
        
        # Create appropriate connector based on TMS type
        if tms_type == 'sap':
            connector = SAPTMConnector(connection_params)
        elif tms_type == 'oracle':
            connector = OracleTMSConnector(connection_params)
        elif tms_type == 'jda':
            connector = JDATMSConnector(connection_params)
        else:
            raise DataSourceException(f"Unsupported TMS type: {tms_type}")
        
        logger.info(f"Created TMS connector for {TMS_TYPES[tms_type]}")
        return connector
        
    except DataSourceException:
        # Re-raise DataSourceException
        raise
    except Exception as e:
        # Wrap other exceptions in DataSourceException
        raise DataSourceException(
            f"Error creating TMS connector: {str(e)}",
            details={"tms_type": connection_params.get('tms_type', 'unknown')},
            original_exception=e
        )


def map_tms_response(response_data: Dict, tms_type: str, field_mapping: Optional[Dict] = None) -> Dict:
    """
    Maps TMS-specific response fields to standardized field names used by the system.

    Args:
        response_data: Original response data from the TMS
        tms_type: Type of TMS (sap, oracle, jda)
        field_mapping: Dictionary mapping source field names to target field names

    Returns:
        Mapped response data with standardized field names

    Raises:
        DataSourceException: If required fields are missing in the mapping or response
    """
    # Use default mapping if not provided
    if field_mapping is None:
        # Default mappings based on TMS type
        if tms_type == 'sap':
            field_mapping = {
                'FreightCharge': 'freight_charge',
                'Currency': 'currency',
                'OriginLocation': 'origin',
                'DestinationLocation': 'destination',
                'CarrierID': 'carrier',
                'EffectiveDate': 'date',
                'TransportMode': 'mode',
                'ServiceLevel': 'service_level'
            }
        elif tms_type == 'oracle':
            field_mapping = {
                'FREIGHT_COST': 'freight_charge',
                'CURRENCY_CODE': 'currency',
                'ORIGIN_LOCATION_CODE': 'origin',
                'DESTINATION_LOCATION_CODE': 'destination',
                'CARRIER_CODE': 'carrier',
                'EFFECTIVE_DATE': 'date',
                'MODE_OF_TRANSPORT': 'mode',
                'SERVICE_LEVEL': 'service_level'
            }
        elif tms_type == 'jda':
            field_mapping = {
                'freightRate': 'freight_charge',
                'currencyCode': 'currency',
                'origin': 'origin',
                'destination': 'destination',
                'carrierId': 'carrier',
                'effectiveDate': 'date',
                'transportMode': 'mode',
                'serviceType': 'service_level'
            }
        else:
            raise DataSourceException(f"Unsupported TMS type for default mapping: {tms_type}")

    # Create an empty dict for the mapped data
    mapped_data = {}
    
    # Apply the field mapping
    for source_field, target_field in field_mapping.items():
        if source_field in response_data:
            mapped_data[target_field] = response_data[source_field]
        else:
            # Log a warning for missing fields but don't fail
            logger.warning(f"Field '{source_field}' not found in TMS response")
    
    # Ensure we have minimum required fields
    required_fields = ['freight_charge', 'currency', 'origin', 'destination', 'date']
    missing_fields = [field for field in required_fields if field not in mapped_data]
    
    if missing_fields:
        logger.warning(f"Mapped TMS response is missing required fields: {', '.join(missing_fields)}")
    
    logger.debug(f"Mapped TMS response fields: {list(mapped_data.keys())}")
    
    return mapped_data


class TMSConnector:
    """
    Base class for connecting to and retrieving data from Transportation Management Systems.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new TMSConnector instance.

        Args:
            connection_params: Dictionary containing connection parameters

        Raises:
            DataSourceException: If required parameters are missing or invalid
        """
        # Validate connection parameters
        validate_tms_connection_params(connection_params)
        
        self.connection_params = connection_params
        self.tms_type = connection_params['tms_type'].lower()
        self.api_url = connection_params['api_url']
        self.auth_type = connection_params.get('auth_type', 'none').lower()
        self.api_client = None
        self.connected = False
        
        logger.info(f"Initialized {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} connector for {self.api_url}")
    
    def connect(self, timeout: Optional[int] = None) -> bool:
        """
        Establishes a connection to the TMS.
        
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
            logger.info(f"Connecting to {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} at {self.api_url}")
            
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
            logger.info(f"Successfully connected to {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} at {self.api_url}")
            return True
            
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} at {self.api_url}: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to connect to {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} at {self.api_url}: {str(e)}",
                details={"api_url": self.api_url, "auth_type": self.auth_type},
                original_exception=e
            )
    
    def disconnect(self) -> bool:
        """
        Closes the TMS connection.
        
        Returns:
            True if disconnection successful
        """
        try:
            if self.api_client:
                self.api_client.close()
                self.api_client = None
            
            self.connected = False
            logger.info(f"Disconnected from {TMS_TYPES.get(self.tms_type, 'Unknown TMS')} at {self.api_url}")
            return True
        
        except Exception as e:
            logger.error(f"Error disconnecting from {TMS_TYPES.get(self.tms_type, 'Unknown TMS')}: {str(e)}", exc_info=True)
            return False
    
    def test_connection(self, timeout: Optional[int] = None) -> bool:
        """
        Tests the TMS connection.
        
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
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None, 
                           field_mapping: Optional[Dict] = None, 
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from the TMS.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of TMS fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            NotImplementedError: This is an abstract method that should be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement fetch_freight_data method")
    
    def __enter__(self) -> 'TMSConnector':
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
        logger.debug("Exited TMS connector context")


class SAPTMConnector(TMSConnector):
    """
    Specialized connector for SAP Transportation Management System.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new SAPTMConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
        self.system_id = connection_params['system_id']
        self.client_number = connection_params['client_number']
        
        logger.info(f"Initialized SAP TM connector for system {self.system_id}, client {self.client_number}")
    
    def connect(self, timeout: Optional[int] = None) -> bool:
        """
        Establishes a connection to the SAP TM system.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        
        Raises:
            DataSourceException: If connection fails
        """
        # First call the parent connect method
        result = super().connect(timeout=timeout)
        
        if result and self.api_client:
            try:
                # Add SAP-specific headers
                sap_headers = {
                    'x-sap-client': self.client_number,
                    'x-sap-system-id': self.system_id
                }
                
                # Update API client headers
                if hasattr(self.api_client, 'default_headers'):
                    self.api_client.default_headers.update(sap_headers)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to configure SAP-specific connection: {str(e)}", exc_info=True)
                self.disconnect()
                
                raise DataSourceException(
                    f"Failed to configure SAP-specific connection: {str(e)}",
                    details={"system_id": self.system_id, "client_number": self.client_number},
                    original_exception=e
                )
        
        return result
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None, 
                           field_mapping: Optional[Dict] = None, 
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from SAP TM.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of SAP TM fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            
            # SAP TM typically uses OData APIs
            endpoint = self.connection_params.get('data_endpoint', 'sap/opu/odata/sap/YY1_FREIGHTRATES_CDS/FreightRates')
            
            # Construct OData query filters
            filters = []
            if 'origin' in query_params:
                filters.append(f"OriginLocation eq '{query_params['origin']}'")
            if 'destination' in query_params:
                filters.append(f"DestinationLocation eq '{query_params['destination']}'")
            if 'carrier' in query_params:
                filters.append(f"CarrierID eq '{query_params['carrier']}'")
            if 'effective_date' in query_params:
                filters.append(f"EffectiveDate eq datetime'{query_params['effective_date']}'")
            if 'mode' in query_params:
                filters.append(f"TransportMode eq '{query_params['mode']}'")
            
            # Prepare request parameters
            request_params = {
                '$format': 'json'
            }
            
            if filters:
                request_params['$filter'] = ' and '.join(filters)
            
            if limit:
                request_params['$top'] = str(limit)
            
            # Execute the API request
            logger.info(f"Fetching freight data from SAP TM endpoint: {endpoint}")
            response = self.api_client.get_json(endpoint=endpoint, params=request_params)
            
            # SAP OData response typically has a 'd' wrapper with results array
            if 'd' in response and 'results' in response['d']:
                sap_data = response['d']['results']
            else:
                raise DataSourceException(
                    "Unexpected SAP TM API response format",
                    details={"response_keys": list(response.keys())}
                )
            
            # Map SAP-specific fields to standardized fields
            mapped_data = []
            for item in sap_data:
                mapped_item = map_tms_response(item, 'sap', field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified and not already applied in the API request
            if limit and '$top' not in request_params and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from SAP TM")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data from SAP TM: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data from SAP TM: {str(e)}",
                details={"endpoint": endpoint, "params": query_params},
                original_exception=e
            )
    
    def get_freight_orders(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves freight orders from SAP TM.
        
        Args:
            filter_params: Parameters to filter the orders
            limit: Maximum number of records to return
            
        Returns:
            Freight orders as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        if not self.connected:
            self.connect()
        
        try:
            filter_params = filter_params or {}
            
            # Endpoint for freight orders
            endpoint = 'sap/opu/odata/sap/YY1_FREIGHTORDERS_CDS/FreightOrders'
            
            # Construct OData query filters
            filters = []
            for key, value in filter_params.items():
                if isinstance(value, str):
                    filters.append(f"{key} eq '{value}'")
                elif isinstance(value, (int, float)):
                    filters.append(f"{key} eq {value}")
                elif isinstance(value, bool):
                    filters.append(f"{key} eq {str(value).lower()}")
            
            # Prepare request parameters
            request_params = {
                '$format': 'json'
            }
            
            if filters:
                request_params['$filter'] = ' and '.join(filters)
            
            if limit:
                request_params['$top'] = str(limit)
            
            # Execute the API request
            logger.info(f"Fetching freight orders from SAP TM endpoint: {endpoint}")
            response = self.api_client.get_json(endpoint=endpoint, params=request_params)
            
            # Extract the data from the response
            if 'd' in response and 'results' in response['d']:
                orders_data = response['d']['results']
            else:
                raise DataSourceException(
                    "Unexpected SAP TM API response format for freight orders",
                    details={"response_keys": list(response.keys())}
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(orders_data)
            
            # Apply limit if specified and not already applied in the API request
            if limit and '$top' not in request_params and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight orders from SAP TM")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight orders from SAP TM: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight orders from SAP TM: {str(e)}",
                details={"endpoint": endpoint, "params": filter_params},
                original_exception=e
            )
    
    def get_freight_rates(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves freight rates from SAP TM.
        
        Args:
            filter_params: Parameters to filter the rates
            limit: Maximum number of records to return
            
        Returns:
            Freight rates as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        # This is essentially a wrapper around fetch_freight_data with different default parameters
        try:
            logger.info("Fetching freight rates from SAP TM")
            return self.fetch_freight_data(query_params=filter_params, limit=limit)
            
        except Exception as e:
            logger.error(f"Failed to fetch freight rates from SAP TM: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight rates from SAP TM: {str(e)}",
                details={"params": filter_params},
                original_exception=e
            )


class OracleTMSConnector(TMSConnector):
    """
    Specialized connector for Oracle Transportation Management System.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new OracleTMSConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
        self.instance_id = connection_params['instance_id']
        
        logger.info(f"Initialized Oracle TMS connector for instance {self.instance_id}")
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None, 
                           field_mapping: Optional[Dict] = None, 
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from Oracle TMS.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of Oracle TMS fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            
            # Determine the appropriate endpoint based on the query parameters
            if query_params.get('data_type') == 'rate_records':
                endpoint = f'instance/{self.instance_id}/glog.integration.servlet.WMServlet/RateRecordAPI'
            elif query_params.get('data_type') == 'shipments':
                endpoint = f'instance/{self.instance_id}/glog.integration.servlet.WMServlet/ShipmentAPI'
            else:
                endpoint = f'instance/{self.instance_id}/glog.integration.servlet.WMServlet/RateAPI'
            
            # Prepare request parameters
            request_params = {}
            
            # Add filters
            if 'origin' in query_params:
                request_params['sourceLocationId'] = query_params['origin']
            if 'destination' in query_params:
                request_params['destLocationId'] = query_params['destination']
            if 'carrier' in query_params:
                request_params['carrierId'] = query_params['carrier']
            if 'effective_date' in query_params:
                request_params['effectiveDate'] = query_params['effective_date']
            if 'expiration_date' in query_params:
                request_params['expirationDate'] = query_params['expiration_date']
            
            # Add pagination
            if limit:
                request_params['rowLimit'] = str(limit)
            
            # Execute the API request
            logger.info(f"Fetching freight data from Oracle TMS endpoint: {endpoint}")
            response = self.api_client.get_json(endpoint=endpoint, params=request_params)
            
            # Oracle TMS response format varies by endpoint, but typically has a data array
            data_key = self.connection_params.get('data_key', 'RateList')
            
            if data_key in response:
                oracle_data = response[data_key]
            else:
                raise DataSourceException(
                    f"Data key '{data_key}' not found in Oracle TMS response",
                    details={"response_keys": list(response.keys())}
                )
            
            # Ensure oracle_data is a list
            if not isinstance(oracle_data, list):
                oracle_data = [oracle_data]
            
            # Map Oracle-specific fields to standardized fields
            mapped_data = []
            for item in oracle_data:
                mapped_item = map_tms_response(item, 'oracle', field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified and not already applied in the API request
            if limit and 'rowLimit' not in request_params and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from Oracle TMS")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data from Oracle TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data from Oracle TMS: {str(e)}",
                details={"endpoint": endpoint, "params": query_params},
                original_exception=e
            )
    
    def get_rate_records(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves rate records from Oracle TMS.
        
        Args:
            filter_params: Parameters to filter the rate records
            limit: Maximum number of records to return
            
        Returns:
            Rate records as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        filter_params = filter_params or {}
        filter_params['data_type'] = 'rate_records'
        
        try:
            logger.info("Fetching rate records from Oracle TMS")
            return self.fetch_freight_data(query_params=filter_params, limit=limit)
            
        except Exception as e:
            logger.error(f"Failed to fetch rate records from Oracle TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch rate records from Oracle TMS: {str(e)}",
                details={"params": filter_params},
                original_exception=e
            )
    
    def get_shipments(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves shipments from Oracle TMS.
        
        Args:
            filter_params: Parameters to filter the shipments
            limit: Maximum number of records to return
            
        Returns:
            Shipments as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        filter_params = filter_params or {}
        filter_params['data_type'] = 'shipments'
        
        try:
            logger.info("Fetching shipments from Oracle TMS")
            return self.fetch_freight_data(query_params=filter_params, limit=limit)
            
        except Exception as e:
            logger.error(f"Failed to fetch shipments from Oracle TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch shipments from Oracle TMS: {str(e)}",
                details={"params": filter_params},
                original_exception=e
            )


class JDATMSConnector(TMSConnector):
    """
    Specialized connector for JDA Transportation Management System.
    """
    
    def __init__(self, connection_params: Dict):
        """
        Initializes a new JDATMSConnector instance.
        
        Args:
            connection_params: Dictionary containing connection parameters
        """
        super().__init__(connection_params)
        self.environment = connection_params['environment']
        
        logger.info(f"Initialized JDA TMS connector for environment {self.environment}")
    
    def connect(self, timeout: Optional[int] = None) -> bool:
        """
        Establishes a connection to the JDA TMS system.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        
        Raises:
            DataSourceException: If connection fails
        """
        # First call the parent connect method
        result = super().connect(timeout=timeout)
        
        if result and self.api_client:
            try:
                # Add JDA-specific headers
                jda_headers = {
                    'X-JDA-Environment': self.environment
                }
                
                # Update API client headers
                if hasattr(self.api_client, 'default_headers'):
                    self.api_client.default_headers.update(jda_headers)
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to configure JDA-specific connection: {str(e)}", exc_info=True)
                self.disconnect()
                
                raise DataSourceException(
                    f"Failed to configure JDA-specific connection: {str(e)}",
                    details={"environment": self.environment},
                    original_exception=e
                )
        
        return result
    
    def fetch_freight_data(self, query_params: Optional[Dict] = None, 
                           field_mapping: Optional[Dict] = None, 
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from JDA TMS.
        
        Args:
            query_params: Parameters to filter the data
            field_mapping: Mapping of JDA TMS fields to standard fields
            limit: Maximum number of records to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            
            # JDA TMS typically uses SOAP APIs
            soap_operation = query_params.get('operation', 'getCarrierRates')
            
            # Create a SOAP connector using the SOAPAPIConnector from generic_api_connector
            soap_connector = SOAPAPIConnector({
                'api_url': self.api_url,
                'wsdl_url': self.connection_params.get('wsdl_url', self.api_url + '?wsdl'),
                'auth_type': self.auth_type
            })
            
            # Connect the SOAP connector
            soap_connector.connect()
            
            # Prepare SOAP request parameters
            soap_params = {}
            
            if 'origin' in query_params:
                soap_params['originLocationId'] = query_params['origin']
            if 'destination' in query_params:
                soap_params['destinationLocationId'] = query_params['destination']
            if 'carrier' in query_params:
                soap_params['carrierId'] = query_params['carrier']
            if 'effective_date' in query_params:
                soap_params['effectiveDate'] = query_params['effective_date']
            if 'mode' in query_params:
                soap_params['transportMode'] = query_params['mode']
            
            # Execute the SOAP operation
            logger.info(f"Executing JDA TMS SOAP operation: {soap_operation}")
            result = soap_connector.execute_soap_operation(soap_operation, soap_params)
            
            # Disconnect the SOAP connector
            soap_connector.disconnect()
            
            # Extract data from the SOAP response
            data_key = self.connection_params.get('data_key', 'carrierRates')
            
            if data_key in result:
                jda_data = result[data_key]
            else:
                raise DataSourceException(
                    f"Data key '{data_key}' not found in JDA TMS response",
                    details={"response_keys": list(result.keys())}
                )
            
            # Ensure jda_data is a list
            if not isinstance(jda_data, list):
                jda_data = [jda_data]
            
            # Map JDA-specific fields to standardized fields
            mapped_data = []
            for item in jda_data:
                mapped_item = map_tms_response(item, 'jda', field_mapping)
                mapped_data.append(mapped_item)
            
            # Convert to DataFrame
            df = pd.DataFrame(mapped_data)
            
            # Apply limit if specified
            if limit and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from JDA TMS")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch freight data from JDA TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch freight data from JDA TMS: {str(e)}",
                details={"operation": soap_operation, "params": query_params},
                original_exception=e
            )
    
    def get_carrier_rates(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves carrier rates from JDA TMS.
        
        Args:
            filter_params: Parameters to filter the carrier rates
            limit: Maximum number of records to return
            
        Returns:
            Carrier rates as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        filter_params = filter_params or {}
        filter_params['operation'] = 'getCarrierRates'
        
        try:
            logger.info("Fetching carrier rates from JDA TMS")
            return self.fetch_freight_data(query_params=filter_params, limit=limit)
            
        except Exception as e:
            logger.error(f"Failed to fetch carrier rates from JDA TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch carrier rates from JDA TMS: {str(e)}",
                details={"params": filter_params},
                original_exception=e
            )
    
    def get_load_tenders(self, filter_params: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieves load tenders from JDA TMS.
        
        Args:
            filter_params: Parameters to filter the load tenders
            limit: Maximum number of records to return
            
        Returns:
            Load tenders as a DataFrame
            
        Raises:
            DataSourceException: If the data retrieval fails
        """
        filter_params = filter_params or {}
        filter_params['operation'] = 'getLoadTenders'
        
        try:
            logger.info("Fetching load tenders from JDA TMS")
            return self.fetch_freight_data(query_params=filter_params, limit=limit)
            
        except Exception as e:
            logger.error(f"Failed to fetch load tenders from JDA TMS: {str(e)}", exc_info=True)
            
            if isinstance(e, DataSourceException):
                raise
            
            raise DataSourceException(
                f"Failed to fetch load tenders from JDA TMS: {str(e)}",
                details={"params": filter_params},
                original_exception=e
            )