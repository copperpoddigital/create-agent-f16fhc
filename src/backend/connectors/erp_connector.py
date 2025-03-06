#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connector module for establishing connections to Enterprise Resource Planning (ERP) systems
and retrieving freight pricing data.

This module provides a standardized interface for connecting to various ERP platforms
(SAP ERP, Oracle ERP, Microsoft Dynamics), executing queries, and transforming 
the results into a consistent format for the Freight Price Movement Agent.
"""

from logging import getLogger
import pandas as pd  # version: 1.5.x
import requests  # version: 2.28.x
import sqlalchemy  # version: 1.4.x
import pyrfc  # version: 2.0.x

from .database_connector import DatabaseConnector
from .generic_api_connector import GenericAPIConnector
from ..core.exceptions import ERPConnectionError, ERPQueryError, DataValidationError
from ..core.config import settings

# Configure logger
logger = getLogger(__name__)

def create_erp_connector(erp_type, connection_params):
    """
    Factory function to create the appropriate ERP connector based on the ERP system type.
    
    Args:
        erp_type (str): Type of ERP system (e.g., 'sap_erp', 'oracle_erp', 'ms_dynamics')
        connection_params (dict): Dictionary containing connection parameters
        
    Returns:
        ERPConnector: An instance of the appropriate ERPConnector subclass
        
    Raises:
        ValueError: If erp_type is not supported
    """
    if not erp_type:
        raise ValueError("ERP type must be specified")
    
    erp_type = erp_type.lower()
    
    if erp_type == 'sap_erp':
        return SAPERPConnector(connection_params)
    elif erp_type == 'oracle_erp':
        return OracleERPConnector(connection_params)
    elif erp_type == 'ms_dynamics':
        return MicrosoftDynamicsConnector(connection_params)
    else:
        raise ValueError(f"Unsupported ERP type: {erp_type}")

def validate_erp_data(data):
    """
    Validates that the retrieved data contains the required freight data columns and formats.
    
    Args:
        data (pandas.DataFrame): DataFrame containing the retrieved data
        
    Returns:
        bool: True if data is valid, raises exception otherwise
        
    Raises:
        DataValidationError: If data validation fails
    """
    # Check that the DataFrame is not empty
    if data is None or data.empty:
        raise DataValidationError("Retrieved data is empty")
    
    # Required columns for freight data
    required_columns = ['origin', 'destination', 'freight_charge', 'date']
    
    # Verify that required columns exist
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise DataValidationError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Validate data types for critical columns
    try:
        # Check that freight_charge is numeric
        pd.to_numeric(data['freight_charge'])
        
        # Check that date is a valid datetime
        pd.to_datetime(data['date'])
    except Exception as e:
        raise DataValidationError(f"Data type validation failed: {str(e)}")
    
    # Check for null values in required fields
    null_counts = data[required_columns].isnull().sum()
    if null_counts.sum() > 0:
        null_fields = ", ".join([f"{col}: {count}" for col, count in null_counts.items() if count > 0])
        raise DataValidationError(f"Null values found in required fields: {null_fields}")
    
    # Validate that freight charges are numeric and positive
    if (data['freight_charge'] <= 0).any():
        raise DataValidationError("Freight charges must be positive")
    
    return True

def map_erp_fields(data, field_mapping):
    """
    Maps ERP-specific field names to standardized field names used by the system.
    
    Args:
        data (pandas.DataFrame): DataFrame with ERP-specific field names
        field_mapping (dict): Dictionary mapping ERP field names to standardized field names
        
    Returns:
        pandas.DataFrame: DataFrame with standardized column names
        
    Raises:
        ValueError: If field_mapping is invalid
    """
    if not field_mapping or not isinstance(field_mapping, dict):
        raise ValueError("Field mapping must be provided as a dictionary")
    
    # Check that field_mapping contains mappings for all required fields
    required_standard_fields = ['origin', 'destination', 'freight_charge', 'date']
    standard_fields_in_mapping = field_mapping.values()
    
    missing_standard_fields = [field for field in required_standard_fields 
                              if field not in standard_fields_in_mapping]
    
    if missing_standard_fields:
        raise ValueError(f"Field mapping is missing required standard fields: {', '.join(missing_standard_fields)}")
    
    # Create a copy of the DataFrame to avoid modifying the original
    mapped_data = data.copy()
    
    # Rename columns according to the field mapping
    mapped_data = mapped_data.rename(columns=field_mapping)
    
    # Log the field mapping operation
    logger.debug(f"Mapped ERP fields to standard fields: {field_mapping}")
    
    return mapped_data

class ERPConnector:
    """
    Abstract base class for connecting to and retrieving data from ERP systems.
    """
    
    def __init__(self, erp_type, connection_params):
        """
        Initializes a new ERPConnector instance.
        
        Args:
            erp_type (str): Type of ERP system (e.g., 'sap_erp', 'oracle_erp', 'ms_dynamics')
            connection_params (dict): Dictionary containing connection parameters
        """
        self.erp_type = erp_type
        self.connection_params = connection_params
        self.connected = False
        
        # Validate that required connection parameters are provided
        if not connection_params or not isinstance(connection_params, dict):
            raise ValueError("Connection parameters must be provided as a dictionary")
            
        logger.info(f"Initialized {self.__class__.__name__} for {erp_type}")
    
    def connect(self, timeout=None):
        """
        Establishes a connection to the ERP system.
        
        Args:
            timeout (int, optional): Connection timeout in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if timeout is None:
            timeout = getattr(settings, 'ERP_CONNECTION_TIMEOUT', 30)
        
        raise NotImplementedError("Subclasses must implement connect method")
    
    def disconnect(self):
        """
        Closes the ERP system connection.
        
        Returns:
            bool: True if disconnection successful
        """
        raise NotImplementedError("Subclasses must implement disconnect method")
    
    def test_connection(self, timeout=None):
        """
        Tests the ERP system connection.
        
        Args:
            timeout (int, optional): Connection timeout in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if timeout is None:
            timeout = getattr(settings, 'ERP_CONNECTION_TIMEOUT', 30)
            
        try:
            # Try to connect
            result = self.connect(timeout)
            
            # Disconnect after testing
            if result:
                self.disconnect()
                
            return result
        except Exception as e:
            logger.error(f"Connection test failed for {self.erp_type}: {str(e)}")
            return False
    
    def fetch_freight_data(self, query_params=None, field_mapping=None, limit=None):
        """
        Fetches freight data from the ERP system.
        
        Args:
            query_params (dict, optional): Parameters for filtering the data
            field_mapping (dict, optional): Mapping of ERP-specific fields to standardized fields
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pandas.DataFrame: Freight data as a DataFrame
        """
        raise NotImplementedError("Subclasses must implement fetch_freight_data method")

class SAPERPConnector(ERPConnector):
    """
    Connector for SAP ERP systems.
    """
    
    def __init__(self, connection_params):
        """
        Initializes a new SAPERPConnector instance.
        
        Args:
            connection_params (dict): Dictionary containing connection parameters
        """
        super().__init__('sap_erp', connection_params)
        
        # Validate SAP ERP-specific connection parameters
        required_params = ['ashost', 'sysnr', 'client', 'user', 'passwd']
        missing_params = [param for param in required_params if param not in connection_params]
        
        if missing_params:
            raise ValueError(f"Missing required SAP ERP connection parameters: {', '.join(missing_params)}")
        
        self.client = None
    
    def connect(self, timeout=None):
        """
        Establishes a connection to the SAP ERP system.
        
        Args:
            timeout (int, optional): Connection timeout in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ERPConnectionError: If connection fails
        """
        if timeout is None:
            timeout = getattr(settings, 'ERP_CONNECTION_TIMEOUT', 30)
            
        try:
            logger.info(f"Connecting to SAP ERP at {self.connection_params['ashost']}")
            
            # Create connection parameters for pyrfc
            conn_params = {
                'ashost': self.connection_params['ashost'],
                'sysnr': self.connection_params['sysnr'],
                'client': self.connection_params['client'],
                'user': self.connection_params['user'],
                'passwd': self.connection_params['passwd'],
                'timeout': timeout
            }
            
            # Add optional parameters if provided
            for param in ['lang', 'trace', 'loglevel']:
                if param in self.connection_params:
                    conn_params[param] = self.connection_params[param]
            
            # Establish connection
            self.client = pyrfc.Connection(**conn_params)
            
            # Test connection with a simple RFC call
            self.client.call('RFC_PING')
            
            self.connected = True
            logger.info(f"Successfully connected to SAP ERP at {self.connection_params['ashost']}")
            return True
            
        except Exception as e:
            self.client = None
            self.connected = False
            logger.error(f"Failed to connect to SAP ERP: {str(e)}")
            raise ERPConnectionError(f"Failed to connect to SAP ERP: {str(e)}")
    
    def disconnect(self):
        """
        Closes the SAP ERP system connection.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.client and self.connected:
                self.client.close()
                logger.info("Disconnected from SAP ERP")
            
            self.client = None
            self.connected = False
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from SAP ERP: {str(e)}")
            return False
    
    def execute_rfc(self, function_name, parameters=None):
        """
        Executes a Remote Function Call (RFC) on the SAP ERP system.
        
        Args:
            function_name (str): Name of the RFC function to call
            parameters (dict, optional): Parameters for the RFC function
            
        Returns:
            dict: Result of the RFC call
            
        Raises:
            ERPQueryError: If the RFC call fails
        """
        if not self.connected:
            self.connect()
        
        try:
            logger.debug(f"Executing RFC {function_name} with parameters: {parameters}")
            result = self.client.call(function_name, **(parameters or {}))
            return result
            
        except Exception as e:
            logger.error(f"Error executing RFC {function_name}: {str(e)}")
            raise ERPQueryError(f"Error executing RFC {function_name}: {str(e)}")
    
    def fetch_freight_data(self, query_params=None, field_mapping=None, limit=None):
        """
        Fetches freight data from the SAP ERP system.
        
        Args:
            query_params (dict, optional): Parameters for filtering the data
            field_mapping (dict, optional): Mapping of SAP field names to standardized field names
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pandas.DataFrame: Freight data as a DataFrame
            
        Raises:
            ERPQueryError: If data retrieval fails
            DataValidationError: If data validation fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Determine the appropriate RFC function to call based on query_params
            rfc_function = query_params.get('function_name', 'Z_GET_FREIGHT_DATA')
            
            # Prepare parameters for the RFC call
            rfc_params = {}
            
            # Map query parameters to RFC parameters
            if 'date_from' in query_params:
                rfc_params['DATE_FROM'] = query_params['date_from']
            if 'date_to' in query_params:
                rfc_params['DATE_TO'] = query_params['date_to']
            if 'origin' in query_params:
                rfc_params['ORIGIN'] = query_params['origin']
            if 'destination' in query_params:
                rfc_params['DESTINATION'] = query_params['destination']
            if 'carrier' in query_params:
                rfc_params['CARRIER'] = query_params['carrier']
            
            # Add other parameters from query_params
            for key, value in query_params.items():
                if key not in ['function_name', 'date_from', 'date_to', 'origin', 'destination', 'carrier']:
                    rfc_params[key.upper()] = value
            
            # Execute the RFC call
            logger.info(f"Fetching freight data from SAP ERP using {rfc_function}")
            result = self.execute_rfc(rfc_function, rfc_params)
            
            # Extract the freight data table from the result
            # The actual table name depends on the RFC implementation
            table_name = query_params.get('result_table', 'ET_FREIGHT_DATA')
            if table_name not in result:
                raise ERPQueryError(f"Result table {table_name} not found in RFC result")
            
            freight_data = result[table_name]
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(freight_data)
            
            # If no data was returned, return an empty DataFrame with correct columns
            if df.empty:
                logger.warning("No freight data found in SAP ERP system")
                # Create empty DataFrame with columns from field_mapping
                columns = list(field_mapping.keys())
                return pd.DataFrame(columns=columns)
            
            # Map SAP field names to standardized field names
            if field_mapping:
                df = df.rename(columns=field_mapping)
            
            # Validate the data
            validate_erp_data(df)
            
            # Apply limit if specified
            if limit and len(df) > limit:
                df = df.head(limit)
            
            logger.info(f"Retrieved {len(df)} freight data records from SAP ERP")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching freight data from SAP ERP: {str(e)}")
            if isinstance(e, (ERPQueryError, DataValidationError)):
                raise
            raise ERPQueryError(f"Error fetching freight data from SAP ERP: {str(e)}")

class OracleERPConnector(ERPConnector):
    """
    Connector for Oracle ERP systems.
    """
    
    def __init__(self, connection_params):
        """
        Initializes a new OracleERPConnector instance.
        
        Args:
            connection_params (dict): Dictionary containing connection parameters
        """
        super().__init__('oracle_erp', connection_params)
        
        # Validate Oracle ERP-specific connection parameters
        required_params = ['host', 'port', 'service_name', 'user', 'password']
        missing_params = [param for param in required_params if param not in connection_params]
        
        if missing_params:
            raise ValueError(f"Missing required Oracle ERP connection parameters: {', '.join(missing_params)}")
        
        self.db_connector = None
    
    def connect(self, timeout=None):
        """
        Establishes a connection to the Oracle ERP system.
        
        Args:
            timeout (int, optional): Connection timeout in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ERPConnectionError: If connection fails
        """
        if timeout is None:
            timeout = getattr(settings, 'ERP_CONNECTION_TIMEOUT', 30)
            
        try:
            host = self.connection_params['host']
            port = self.connection_params['port']
            service_name = self.connection_params['service_name']
            
            logger.info(f"Connecting to Oracle ERP at {host}:{port}/{service_name}")
            
            # Create an Oracle connection string
            conn_str = f"oracle+cx_oracle://{self.connection_params['user']}:{self.connection_params['password']}@{host}:{port}/{service_name}"
            
            # Create a DatabaseConnector instance
            self.db_connector = DatabaseConnector(database_url=conn_str, database_type='oracle')
            
            # Connect to the database
            result = self.db_connector.connect()
            
            self.connected = result
            if result:
                logger.info(f"Successfully connected to Oracle ERP at {host}:{port}/{service_name}")
            else:
                logger.error(f"Failed to connect to Oracle ERP at {host}:{port}/{service_name}")
            
            return result
            
        except Exception as e:
            self.db_connector = None
            self.connected = False
            logger.error(f"Failed to connect to Oracle ERP: {str(e)}")
            raise ERPConnectionError(f"Failed to connect to Oracle ERP: {str(e)}")
    
    def disconnect(self):
        """
        Closes the Oracle ERP system connection.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.db_connector and self.connected:
                result = self.db_connector.disconnect()
                logger.info("Disconnected from Oracle ERP")
                self.connected = False
                return result
            
            self.connected = False
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Oracle ERP: {str(e)}")
            return False
    
    def fetch_freight_data(self, query_params=None, field_mapping=None, limit=None):
        """
        Fetches freight data from the Oracle ERP system.
        
        Args:
            query_params (dict, optional): Parameters for filtering the data
            field_mapping (dict, optional): Mapping of Oracle field names to standardized field names
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pandas.DataFrame: Freight data as a DataFrame
            
        Raises:
            ERPQueryError: If data retrieval fails
            DataValidationError: If data validation fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Construct the SQL query
            base_query = query_params.get('base_query', """
                SELECT * FROM FREIGHT_RATES
                WHERE 1=1
            """)
            
            # Add filters based on query_params
            filters = []
            params = {}
            
            if 'date_from' in query_params:
                filters.append("RATE_DATE >= :date_from")
                params['date_from'] = query_params['date_from']
                
            if 'date_to' in query_params:
                filters.append("RATE_DATE <= :date_to")
                params['date_to'] = query_params['date_to']
                
            if 'origin' in query_params:
                filters.append("ORIGIN = :origin")
                params['origin'] = query_params['origin']
                
            if 'destination' in query_params:
                filters.append("DESTINATION = :destination")
                params['destination'] = query_params['destination']
                
            if 'carrier' in query_params:
                filters.append("CARRIER = :carrier")
                params['carrier'] = query_params['carrier']
            
            # Add any additional filters from query_params
            for key, value in query_params.items():
                if key not in ['base_query', 'date_from', 'date_to', 'origin', 'destination', 'carrier'] and key.startswith('filter_'):
                    column = key[7:]  # Remove 'filter_' prefix
                    filters.append(f"{column} = :{key}")
                    params[key] = value
            
            # Construct the final query
            sql_query = base_query
            if filters:
                sql_query += " AND " + " AND ".join(filters)
            
            # Add ORDER BY clause if specified
            if 'order_by' in query_params:
                sql_query += f" ORDER BY {query_params['order_by']}"
            
            # Add LIMIT clause if specified
            if limit:
                sql_query += f" FETCH FIRST {limit} ROWS ONLY"
            
            # Execute the query
            logger.info(f"Fetching freight data from Oracle ERP with query: {sql_query}")
            df = self.db_connector.execute_query_df(sql_query, params)
            
            # If no data was returned, return an empty DataFrame with correct columns
            if df.empty:
                logger.warning("No freight data found in Oracle ERP system")
                # Create empty DataFrame with columns from field_mapping
                columns = list(field_mapping.keys())
                return pd.DataFrame(columns=columns)
            
            # Map Oracle field names to standardized field names
            if field_mapping:
                df = df.rename(columns=field_mapping)
            
            # Validate the data
            validate_erp_data(df)
            
            logger.info(f"Retrieved {len(df)} freight data records from Oracle ERP")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching freight data from Oracle ERP: {str(e)}")
            if isinstance(e, (ERPQueryError, DataValidationError)):
                raise
            raise ERPQueryError(f"Error fetching freight data from Oracle ERP: {str(e)}")

class MicrosoftDynamicsConnector(ERPConnector):
    """
    Connector for Microsoft Dynamics ERP systems.
    """
    
    def __init__(self, connection_params):
        """
        Initializes a new MicrosoftDynamicsConnector instance.
        
        Args:
            connection_params (dict): Dictionary containing connection parameters
        """
        super().__init__('ms_dynamics', connection_params)
        
        # Validate Microsoft Dynamics-specific connection parameters
        required_params = ['api_url', 'tenant_id', 'client_id', 'client_secret']
        missing_params = [param for param in required_params if param not in connection_params]
        
        if missing_params:
            raise ValueError(f"Missing required Microsoft Dynamics connection parameters: {', '.join(missing_params)}")
        
        self.api_connector = None
    
    def connect(self, timeout=None):
        """
        Establishes a connection to the Microsoft Dynamics system.
        
        Args:
            timeout (int, optional): Connection timeout in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ERPConnectionError: If connection fails
        """
        if timeout is None:
            timeout = getattr(settings, 'ERP_CONNECTION_TIMEOUT', 30)
            
        try:
            api_url = self.connection_params['api_url']
            logger.info(f"Connecting to Microsoft Dynamics at {api_url}")
            
            # Prepare connection parameters for API connector
            api_connection_params = {
                'api_url': api_url,
                'auth_type': 'oauth2',
                'token_url': f"https://login.microsoftonline.com/{self.connection_params['tenant_id']}/oauth2/v2.0/token",
                'client_id': self.connection_params['client_id'],
                'client_secret': self.connection_params['client_secret'],
                'scope': self.connection_params.get('scope', 'https://api.businesscentral.dynamics.com/.default')
            }
            
            # Create an API connector
            self.api_connector = GenericAPIConnector(api_connection_params)
            
            # Connect to the API
            result = self.api_connector.connect(timeout)
            
            self.connected = result
            if result:
                logger.info(f"Successfully connected to Microsoft Dynamics at {api_url}")
            else:
                logger.error(f"Failed to connect to Microsoft Dynamics at {api_url}")
            
            return result
            
        except Exception as e:
            self.api_connector = None
            self.connected = False
            logger.error(f"Failed to connect to Microsoft Dynamics: {str(e)}")
            raise ERPConnectionError(f"Failed to connect to Microsoft Dynamics: {str(e)}")
    
    def disconnect(self):
        """
        Closes the Microsoft Dynamics system connection.
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.api_connector and self.connected:
                result = self.api_connector.disconnect()
                logger.info("Disconnected from Microsoft Dynamics")
                self.connected = False
                return result
            
            self.connected = False
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Microsoft Dynamics: {str(e)}")
            return False
    
    def get_access_token(self):
        """
        Obtains an OAuth access token for Microsoft Dynamics API.
        
        Returns:
            str: OAuth access token
            
        Raises:
            ERPConnectionError: If token acquisition fails
        """
        try:
            token_url = f"https://login.microsoftonline.com/{self.connection_params['tenant_id']}/oauth2/v2.0/token"
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.connection_params['client_id'],
                'client_secret': self.connection_params['client_secret'],
                'scope': self.connection_params.get('scope', 'https://api.businesscentral.dynamics.com/.default')
            }
            
            response = requests.post(token_url, data=payload)
            
            if response.status_code != 200:
                raise ERPConnectionError(f"Failed to obtain access token: {response.text}")
            
            token_data = response.json()
            return token_data['access_token']
            
        except Exception as e:
            logger.error(f"Error obtaining access token: {str(e)}")
            raise ERPConnectionError(f"Error obtaining access token: {str(e)}")
    
    def fetch_freight_data(self, query_params=None, field_mapping=None, limit=None):
        """
        Fetches freight data from the Microsoft Dynamics system.
        
        Args:
            query_params (dict, optional): Parameters for filtering the data
            field_mapping (dict, optional): Mapping of Dynamics field names to standardized field names
            limit (int, optional): Maximum number of records to return
            
        Returns:
            pandas.DataFrame: Freight data as a DataFrame
            
        Raises:
            ERPQueryError: If data retrieval fails
            DataValidationError: If data validation fails
        """
        if not self.connected:
            self.connect()
        
        try:
            query_params = query_params or {}
            field_mapping = field_mapping or {}
            
            # Construct the API endpoint
            endpoint = query_params.get('endpoint', 'FreightRates')
            
            # Add query parameters for filtering
            api_params = {}
            
            # OData filtering
            filters = []
            
            if 'date_from' in query_params:
                filters.append(f"RateDate ge {query_params['date_from']}")
                
            if 'date_to' in query_params:
                filters.append(f"RateDate le {query_params['date_to']}")
                
            if 'origin' in query_params:
                filters.append(f"Origin eq '{query_params['origin']}'")
                
            if 'destination' in query_params:
                filters.append(f"Destination eq '{query_params['destination']}'")
                
            if 'carrier' in query_params:
                filters.append(f"Carrier eq '{query_params['carrier']}'")
            
            # Add any additional filters from query_params
            for key, value in query_params.items():
                if key not in ['endpoint', 'date_from', 'date_to', 'origin', 'destination', 'carrier'] and key.startswith('filter_'):
                    column = key[7:]  # Remove 'filter_' prefix
                    if isinstance(value, str):
                        filters.append(f"{column} eq '{value}'")
                    else:
                        filters.append(f"{column} eq {value}")
            
            # Construct the $filter parameter
            if filters:
                api_params['$filter'] = " and ".join(filters)
            
            # Add $orderby parameter if specified
            if 'order_by' in query_params:
                api_params['$orderby'] = query_params['order_by']
            
            # Add $top parameter if limit is specified
            if limit:
                api_params['$top'] = str(limit)
            
            # Execute the API request
            logger.info(f"Fetching freight data from Microsoft Dynamics with endpoint: {endpoint}")
            response = self.api_connector.get_data(endpoint, params=api_params)
            
            # Extract the data from the response
            # Dynamics typically returns data in a 'value' array
            if 'value' in response:
                dynamics_data = response['value']
            else:
                dynamics_data = [response]  # Single item response
            
            # If no data was returned, return an empty DataFrame with correct columns
            if not dynamics_data:
                logger.warning("No freight data found in Microsoft Dynamics system")
                # Create empty DataFrame with columns from field_mapping
                columns = list(field_mapping.keys())
                return pd.DataFrame(columns=columns)
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(dynamics_data)
            
            # Map Dynamics field names to standardized field names
            if field_mapping:
                df = df.rename(columns=field_mapping)
            
            # Validate the data
            validate_erp_data(df)
            
            logger.info(f"Retrieved {len(df)} freight data records from Microsoft Dynamics")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching freight data from Microsoft Dynamics: {str(e)}")
            if isinstance(e, (ERPQueryError, DataValidationError)):
                raise
            raise ERPQueryError(f"Error fetching freight data from Microsoft Dynamics: {str(e)}")