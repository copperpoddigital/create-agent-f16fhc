"""Test module for the Integration Service of the Freight Price Movement Agent.
Contains unit tests to verify the functionality of connecting to various
external systems, retrieving freight pricing data, and handling error conditions.
"""

import pytest  # version 7.3.x
from unittest import mock  # standard library
import pandas as pd  # version 1.5.x

from src.backend.services.integration import IntegrationService, DataSourceType, create_connector  # Internal import
from src.backend.connectors.tms_connector import TMSConnector  # Internal import
from src.backend.connectors.erp_connector import ERPConnector  # Internal import
from src.backend.connectors.database_connector import DatabaseConnector  # Internal import
from src.backend.connectors.file_connector import FileConnector  # Internal import
from src.backend.connectors.generic_api_connector import GenericAPIConnector  # Internal import
from src.backend.core.exceptions import DataSourceException, IntegrationException  # Internal import


@pytest.fixture
def integration_service():
    """Pytest fixture that provides an IntegrationService instance for testing"""
    # Create a new IntegrationService instance
    service = IntegrationService()
    yield service
    # Ensure all connections are closed after the test
    service.close_all_connections()


@pytest.fixture
def mock_tms_connector():
    """Pytest fixture that provides a mock TMSConnector for testing"""
    # Create a MagicMock instance for TMSConnector
    mock = mock.MagicMock(spec=TMSConnector)
    # Configure the mock to return appropriate values for connect, disconnect, and fetch_freight_data methods
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    mock.fetch_freight_data.return_value = pd.DataFrame()
    return mock


@pytest.fixture
def mock_erp_connector():
    """Pytest fixture that provides a mock ERPConnector for testing"""
    # Create a MagicMock instance for ERPConnector
    mock = mock.MagicMock(spec=ERPConnector)
    # Configure the mock to return appropriate values for connect, disconnect, and fetch_freight_data methods
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    mock.fetch_freight_data.return_value = pd.DataFrame()
    return mock


@pytest.fixture
def mock_db_connector():
    """Pytest fixture that provides a mock DatabaseConnector for testing"""
    # Create a MagicMock instance for DatabaseConnector
    mock = mock.MagicMock(spec=DatabaseConnector)
    # Configure the mock to return appropriate values for connect, disconnect, and fetch_freight_data methods
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    mock.fetch_freight_data.return_value = pd.DataFrame()
    return mock


@pytest.fixture
def mock_file_connector():
    """Pytest fixture that provides a mock FileConnector for testing"""
    # Create a MagicMock instance for FileConnector
    mock = mock.MagicMock(spec=FileConnector)
    # Configure the mock to return appropriate values for fetch_freight_data method
    mock.fetch_freight_data.return_value = pd.DataFrame()
    return mock


@pytest.fixture
def mock_api_connector():
    """Pytest fixture that provides a mock GenericAPIConnector for testing"""
    # Create a MagicMock instance for GenericAPIConnector
    mock = mock.MagicMock(spec=GenericAPIConnector)
    # Configure the mock to return appropriate values for connect, disconnect, and fetch_freight_data methods
    mock.connect.return_value = True
    mock.disconnect.return_value = True
    mock.fetch_freight_data.return_value = pd.DataFrame()
    return mock


@pytest.fixture
def sample_freight_data():
    """Pytest fixture that provides sample freight data for testing"""
    # Create a pandas DataFrame with sample freight data
    data = {
        'origin': ['New York', 'Los Angeles'],
        'destination': ['London', 'Tokyo'],
        'freight_charge': [100.0, 200.0],
        'date': ['2023-01-01', '2023-01-02']
    }
    # Include columns for origin, destination, freight_charge, date, etc.
    df = pd.DataFrame(data)
    return df


def test_integration_service_initialization(integration_service):
    """Test that the IntegrationService initializes correctly"""
    # Verify that the instance is created successfully
    assert isinstance(integration_service, IntegrationService)
    # Verify that active_connections is initialized as an empty dictionary
    assert integration_service.active_connections == {}
    # Verify that error_handler is initialized
    assert integration_service.error_handler is not None


def test_connect_to_tms(integration_service, mock_tms_connector):
    """Test connecting to a TMS data source"""
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Define TMS connection parameters
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        # Call integration_service.connect_to_source with TMS parameters
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Verify that the connection was successful
        assert success is True
        # Verify that the connection is stored in active_connections
        assert connection_id in integration_service.active_connections
        # Verify that the mock_tms_connector.connect method was called
        mock_tms_connector.connect.assert_called_once()


def test_connect_to_erp(integration_service, mock_erp_connector):
    """Test connecting to an ERP data source"""
    # Patch create_connector to return the mock_erp_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_erp_connector):
        # Define ERP connection parameters
        connection_params = {'erp_type': 'test', 'api_url': 'http://example.com'}
        # Call integration_service.connect_to_source with ERP parameters
        success, connection_id = integration_service.connect_to_source('erp', connection_params)
        # Verify that the connection was successful
        assert success is True
        # Verify that the connection is stored in active_connections
        assert connection_id in integration_service.active_connections
        # Verify that the mock_erp_connector.connect method was called
        mock_erp_connector.connect.assert_called_once()


def test_connect_to_database(integration_service, mock_db_connector):
    """Test connecting to a database data source"""
    # Patch create_connector to return the mock_db_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_db_connector):
        # Define database connection parameters
        connection_params = {'host': 'localhost', 'port': 5432, 'database': 'test', 'username': 'user', 'password': 'password'}
        # Call integration_service.connect_to_source with database parameters
        success, connection_id = integration_service.connect_to_source('database', connection_params)
        # Verify that the connection was successful
        assert success is True
        # Verify that the connection is stored in active_connections
        assert connection_id in integration_service.active_connections
        # Verify that the mock_db_connector.connect method was called
        mock_db_connector.connect.assert_called_once()


def test_connect_to_file(integration_service, mock_file_connector):
    """Test connecting to a file data source"""
    # Patch create_connector to return the mock_file_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_file_connector):
        # Define file connection parameters
        connection_params = {'file_path': '/path/to/file.csv'}
        # Call integration_service.connect_to_source with file parameters
        success, connection_id = integration_service.connect_to_source('file', connection_params)
        # Verify that the connection was successful
        assert success is True
        # Verify that the connection is stored in active_connections
        assert connection_id in integration_service.active_connections


def test_connect_to_api(integration_service, mock_api_connector):
    """Test connecting to an API data source"""
    # Patch create_connector to return the mock_api_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_api_connector):
        # Define API connection parameters
        connection_params = {'api_url': 'http://example.com'}
        # Call integration_service.connect_to_source with API parameters
        success, connection_id = integration_service.connect_to_source('api', connection_params)
        # Verify that the connection was successful
        assert success is True
        # Verify that the connection is stored in active_connections
        assert connection_id in integration_service.active_connections
        # Verify that the mock_api_connector.connect method was called
        mock_api_connector.connect.assert_called_once()


def test_disconnect_from_source(integration_service, mock_tms_connector):
    """Test disconnecting from a data source"""
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Connect to a TMS data source
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Call integration_service.disconnect_from_source with the connection ID
        success = integration_service.disconnect_from_source(connection_id)
        # Verify that the disconnection was successful
        assert success is True
        # Verify that the connection is removed from active_connections
        assert connection_id not in integration_service.active_connections
        # Verify that the mock_tms_connector.disconnect method was called
        mock_tms_connector.disconnect.assert_called_once()


def test_fetch_freight_data(integration_service, mock_tms_connector, sample_freight_data):
    """Test fetching freight data from a connected data source"""
    # Configure mock_tms_connector to return sample_freight_data
    mock_tms_connector.fetch_freight_data.return_value = sample_freight_data
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Connect to a TMS data source
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Call integration_service.fetch_freight_data with the connection ID
        data = integration_service.fetch_freight_data(connection_id)
        # Verify that the data is fetched successfully
        assert isinstance(data, pd.DataFrame)
        # Verify that the returned data matches sample_freight_data
        pd.testing.assert_frame_equal(data, sample_freight_data)
        # Verify that the mock_tms_connector.fetch_freight_data method was called
        mock_tms_connector.fetch_freight_data.assert_called_once()


def test_fetch_freight_data_with_params(integration_service, mock_tms_connector, sample_freight_data):
    """Test fetching freight data with query parameters"""
    # Configure mock_tms_connector to return sample_freight_data
    mock_tms_connector.fetch_freight_data.return_value = sample_freight_data
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Connect to a TMS data source
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Define query parameters (date range, filters, etc.)
        query_params = {'start_date': '2023-01-01', 'end_date': '2023-01-02'}
        # Call integration_service.fetch_freight_data with the connection ID and query parameters
        data = integration_service.fetch_freight_data(connection_id, query_params=query_params)
        # Verify that the data is fetched successfully
        assert isinstance(data, pd.DataFrame)
        # Verify that the mock_tms_connector.fetch_freight_data was called with the query parameters
        mock_tms_connector.fetch_freight_data.assert_called_with(query_params=query_params, field_mapping=None, limit=None)


def test_get_active_connections(integration_service, mock_tms_connector, mock_erp_connector):
    """Test retrieving information about active connections"""
    # Patch create_connector to return appropriate mocks
    with mock.patch('src.backend.services.integration.create_connector') as mock_create_connector:
        mock_create_connector.side_effect = [mock_tms_connector, mock_erp_connector]
        # Connect to multiple data sources
        connection_params_tms = {'tms_type': 'test', 'api_url': 'http://example.com/tms'}
        success_tms, connection_id_tms = integration_service.connect_to_source('tms', connection_params_tms)
        connection_params_erp = {'erp_type': 'test', 'api_url': 'http://example.com/erp'}
        success_erp, connection_id_erp = integration_service.connect_to_source('erp', connection_params_erp)
        # Call integration_service.get_active_connections
        active_connections = integration_service.get_active_connections()
        # Verify that the returned information includes all active connections
        assert connection_id_tms in active_connections
        assert connection_id_erp in active_connections
        # Verify that the connection details are correct
        assert active_connections[connection_id_tms]['source_type'] == 'MagicMock'
        assert active_connections[connection_id_erp]['source_type'] == 'MagicMock'


def test_close_all_connections(integration_service, mock_tms_connector, mock_erp_connector):
    """Test closing all active connections"""
    # Patch create_connector to return appropriate mocks
    with mock.patch('src.backend.services.integration.create_connector') as mock_create_connector:
        mock_create_connector.side_effect = [mock_tms_connector, mock_erp_connector]
        # Connect to multiple data sources
        connection_params_tms = {'tms_type': 'test', 'api_url': 'http://example.com/tms'}
        success_tms, connection_id_tms = integration_service.connect_to_source('tms', connection_params_tms)
        connection_params_erp = {'erp_type': 'test', 'api_url': 'http://example.com/erp'}
        success_erp, connection_id_erp = integration_service.connect_to_source('erp', connection_params_erp)
        # Call integration_service.close_all_connections
        results = integration_service.close_all_connections()
        # Verify that all connections are closed
        assert connection_id_tms in results
        assert connection_id_erp in results
        assert results[connection_id_tms]['success'] is True
        assert results[connection_id_erp]['success'] is True
        # Verify that active_connections is empty
        assert integration_service.active_connections == {}
        # Verify that disconnect was called on each connector
        mock_tms_connector.disconnect.assert_called_once()
        mock_erp_connector.disconnect.assert_called_once()


def test_test_connection(integration_service, mock_tms_connector):
    """Test the connection testing functionality"""
    # Configure mock_tms_connector to return success for connect
    mock_tms_connector.connect.return_value = True
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Define TMS connection parameters
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        # Call integration_service.test_connection with TMS parameters
        success, message = integration_service.test_connection('tms', connection_params)
        # Verify that the test was successful
        assert success is True
        # Verify that the mock_tms_connector.connect and disconnect methods were called
        mock_tms_connector.connect.assert_called_once()
        mock_tms_connector.disconnect.assert_called_once()


def test_connection_failure(integration_service, mock_tms_connector):
    """Test handling of connection failures"""
    # Configure mock_tms_connector to raise an exception during connect
    mock_tms_connector.connect.side_effect = DataSourceException("Connection failed")
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Define TMS connection parameters
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        # Call integration_service.connect_to_source with TMS parameters
        success, message = integration_service.connect_to_source('tms', connection_params)
        # Verify that the connection attempt fails
        assert success is False
        # Verify that the appropriate exception is handled
        assert "Connection failed" in message
        # Verify that the connection is not added to active_connections
        assert integration_service.active_connections == {}


def test_fetch_data_failure(integration_service, mock_tms_connector):
    """Test handling of data fetch failures"""
    # Configure mock_tms_connector to raise an exception during fetch_freight_data
    mock_tms_connector.fetch_freight_data.side_effect = DataSourceException("Data fetch failed")
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Connect to a TMS data source
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Call integration_service.fetch_freight_data with the connection ID
        with pytest.raises(DataSourceException) as exc_info:
            integration_service.fetch_freight_data(connection_id)
        # Verify that the fetch attempt fails
        assert "Data fetch failed" in str(exc_info.value)
        # Verify that the appropriate exception is raised
        assert isinstance(exc_info.value, DataSourceException)
        # Verify that the error is properly handled
        assert "Data fetch failed" in str(exc_info.value)


def test_invalid_connection_id(integration_service):
    """Test handling of invalid connection IDs"""
    # Call integration_service.fetch_freight_data with a non-existent connection ID
    with pytest.raises(DataSourceException) as exc_info:
        integration_service.fetch_freight_data("invalid_id")
    # Verify that the appropriate exception is raised
    assert "Connection ID not found" in str(exc_info.value)

    # Call integration_service.disconnect_from_source with a non-existent connection ID
    success = integration_service.disconnect_from_source("invalid_id")
    # Verify that the method returns False
    assert success is False


def test_retry_mechanism(integration_service, mock_tms_connector):
    """Test the retry mechanism for transient failures"""
    # Configure mock_tms_connector to fail on first attempt but succeed on retry
    mock_tms_connector.connect.side_effect = [DataSourceException("Connection failed"), True]
    # Patch create_connector to return the mock_tms_connector
    with mock.patch('src.backend.services.integration.create_connector', return_value=mock_tms_connector):
        # Define TMS connection parameters
        connection_params = {'tms_type': 'test', 'api_url': 'http://example.com'}
        # Call integration_service.connect_to_source with TMS parameters
        success, connection_id = integration_service.connect_to_source('tms', connection_params)
        # Verify that the connection eventually succeeds
        assert success is True
        # Verify that the connect method was called multiple times
        assert mock_tms_connector.connect.call_count == 2