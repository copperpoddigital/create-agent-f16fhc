import pytest  # version ^7.0.0
from unittest.mock import patch, MagicMock, Mock  # version: standard library
import pandas  # version 1.5.x
import json  # version: standard library

from ...connectors.tms_connector import TMSConnector, SAPTMConnector, OracleTMSConnector, JDATMSConnector, create_tms_connector, validate_tms_connection_params, map_tms_response  # src/backend/connectors/tms_connector.py
from ...core.exceptions import DataSourceException, IntegrationException  # src/backend/core/exceptions.py
from ...utils.api_client import APIClient  # src/backend/utils/api_client.py

VALID_SAP_CONNECTION_PARAMS = '{"tms_type": "sap", "api_url": "https://sap-tm-api.example.com", "auth_type": "basic", "username": "test_user", "password": "test_password", "system_id": "PRD", "client_number": "100"}'
VALID_ORACLE_CONNECTION_PARAMS = '{"tms_type": "oracle", "api_url": "https://oracle-tms-api.example.com", "auth_type": "oauth2", "client_id": "test_client", "client_secret": "test_secret", "token_url": "https://oracle-tms-api.example.com/oauth/token", "instance_id": "PROD"}'
VALID_JDA_CONNECTION_PARAMS = '{"tms_type": "jda", "api_url": "https://jda-tms-api.example.com", "auth_type": "api_key", "api_key": "test_api_key", "header_name": "X-API-Key", "environment": "production"}'
INVALID_CONNECTION_PARAMS = '{"tms_type": "unknown", "api_url": "https://unknown-tms.example.com"}'
MOCK_FREIGHT_DATA = '[{"origin": "New York", "destination": "Los Angeles", "carrier": "Test Carrier", "freight_charge": 1500.0, "currency": "USD", "timestamp": "2023-01-01T00:00:00Z"}]'


def mock_api_client(response_data: dict) -> MagicMock:
    """Creates a mock API client for testing TMS connectors"""
    mock = MagicMock()
    mock.get_json.return_value = response_data
    mock.post_json.return_value = response_data
    return mock


class TestTMSConnectorValidation:
    """Test class for TMS connector validation functions"""

    def test_validate_tms_connection_params_valid_sap(self):
        """Tests that validate_tms_connection_params accepts valid SAP TM connection parameters"""
        assert validate_tms_connection_params(json.loads(VALID_SAP_CONNECTION_PARAMS)) is True

    def test_validate_tms_connection_params_valid_oracle(self):
        """Tests that validate_tms_connection_params accepts valid Oracle TMS connection parameters"""
        assert validate_tms_connection_params(json.loads(VALID_ORACLE_CONNECTION_PARAMS)) is True

    def test_validate_tms_connection_params_valid_jda(self):
        """Tests that validate_tms_connection_params accepts valid JDA TMS connection parameters"""
        assert validate_tms_connection_params(json.loads(VALID_JDA_CONNECTION_PARAMS)) is True

    def test_validate_tms_connection_params_missing_required(self):
        """Tests that validate_tms_connection_params raises an exception when required parameters are missing"""
        invalid_params = json.loads(VALID_SAP_CONNECTION_PARAMS)
        del invalid_params['username']
        with pytest.raises(DataSourceException):
            validate_tms_connection_params(invalid_params)

    def test_validate_tms_connection_params_invalid_auth(self):
        """Tests that validate_tms_connection_params raises an exception when auth parameters are invalid"""
        invalid_params = json.loads(VALID_SAP_CONNECTION_PARAMS)
        invalid_params['auth_type'] = 'invalid'
        with pytest.raises(DataSourceException):
            validate_tms_connection_params(invalid_params)

    def test_validate_tms_connection_params_invalid_tms_type(self):
        """Tests that validate_tms_connection_params raises an exception when tms_type is invalid"""
        with pytest.raises(DataSourceException):
            validate_tms_connection_params(json.loads(INVALID_CONNECTION_PARAMS))


class TestCreateTMSConnector:
    """Test class for the create_tms_connector factory function"""

    def test_create_tms_connector_sap(self):
        """Tests that create_tms_connector returns a SAPTMConnector instance for SAP TMS"""
        connector = create_tms_connector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        assert isinstance(connector, SAPTMConnector)
        assert connector.tms_type == 'sap'
        assert connector.system_id == 'PRD'
        assert connector.client_number == '100'

    def test_create_tms_connector_oracle(self):
        """Tests that create_tms_connector returns an OracleTMSConnector instance for Oracle TMS"""
        connector = create_tms_connector(json.loads(VALID_ORACLE_CONNECTION_PARAMS))
        assert isinstance(connector, OracleTMSConnector)
        assert connector.tms_type == 'oracle'
        assert connector.instance_id == 'PROD'

    def test_create_tms_connector_jda(self):
        """Tests that create_tms_connector returns a JDATMSConnector instance for JDA TMS"""
        connector = create_tms_connector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        assert isinstance(connector, JDATMSConnector)
        assert connector.tms_type == 'jda'
        assert connector.environment == 'production'

    def test_create_tms_connector_invalid(self):
        """Tests that create_tms_connector raises an exception for invalid TMS type"""
        with pytest.raises(DataSourceException):
            create_tms_connector(json.loads(INVALID_CONNECTION_PARAMS))

    def test_create_tms_connector_validation_error(self):
        """Tests that create_tms_connector raises an exception when validation fails"""
        invalid_params = json.loads(VALID_SAP_CONNECTION_PARAMS)
        del invalid_params['username']
        with pytest.raises(DataSourceException):
            create_tms_connector(invalid_params)


class TestTMSConnectorBase:
    """Test class for the base TMSConnector class"""

    def test_init(self):
        """Tests that the TMSConnector initializes correctly with valid connection parameters"""
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        assert connector.connection_params == json.loads(VALID_SAP_CONNECTION_PARAMS)
        assert connector.tms_type == 'sap'
        assert connector.api_url == 'https://sap-tm-api.example.com'
        assert connector.auth_type == 'basic'
        assert connector.connected is False

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_connect(self, MockAPIClient):
        """Tests that the connect method establishes a connection to the TMS"""
        mock_api_client_instance = MockAPIClient.return_value
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        assert connector.connected is True
        assert connector.api_client == mock_api_client_instance

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_connect_failure(self, MockAPIClient):
        """Tests that the connect method handles connection failures"""
        MockAPIClient.side_effect = requests.exceptions.RequestException("Connection failed")
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        with pytest.raises(DataSourceException):
            connector.connect()
        assert connector.connected is False

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_disconnect(self, MockAPIClient):
        """Tests that the disconnect method closes the TMS connection"""
        mock_api_client_instance = MockAPIClient.return_value
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        connector.disconnect()
        assert connector.connected is False
        mock_api_client_instance.close.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_test_connection(self, MockAPIClient):
        """Tests that the test_connection method correctly tests the TMS connection"""
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.test_connection()
        assert connector.test_connection() is True
        MockAPIClient.assert_called_once()

    def test_fetch_freight_data_not_implemented(self):
        """Tests that the base fetch_freight_data method raises NotImplementedError"""
        connector = TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        with pytest.raises(NotImplementedError):
            connector.fetch_freight_data()

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_context_manager(self, MockAPIClient):
        """Tests that the TMSConnector works as a context manager"""
        mock_api_client_instance = MockAPIClient.return_value
        with TMSConnector(json.loads(VALID_SAP_CONNECTION_PARAMS)) as connector:
            assert connector.connected is True
        assert connector.connected is False
        mock_api_client_instance.close.assert_called_once()


class TestSAPTMConnector:
    """Test class for the SAPTMConnector specialized class"""

    def test_init(self):
        """Tests that the SAPTMConnector initializes correctly with valid connection parameters"""
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        assert connector.connection_params == json.loads(VALID_SAP_CONNECTION_PARAMS)
        assert connector.tms_type == 'sap'
        assert connector.system_id == 'PRD'
        assert connector.client_number == '100'

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_connect(self, MockAPIClient):
        """Tests that the connect method adds SAP-specific headers"""
        mock_api_client_instance = MockAPIClient.return_value
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        assert connector.connected is True
        assert 'x-sap-client' in mock_api_client_instance.default_headers
        assert 'x-sap-system-id' in mock_api_client_instance.default_headers

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_fetch_freight_data(self, mock_get_json):
        """Tests that fetch_freight_data correctly retrieves and processes SAP TM data"""
        mock_get_json.return_value = json.loads('{"d": {"results": [{"origin": "New York", "destination": "Los Angeles", "carrier": "Test Carrier", "freight_charge": 1500.0, "currency": "USD", "timestamp": "2023-01-01T00:00:00Z"}]}}')
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        df = connector.fetch_freight_data()
        assert isinstance(df, pandas.DataFrame)
        assert df['origin'][0] == 'New York'
        mock_get_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_fetch_freight_data_with_mapping(self, mock_get_json):
        """Tests that fetch_freight_data correctly applies field mapping"""
        mock_get_json.return_value = json.loads('{"d": {"results": [{"OriginLocation": "New York", "DestinationLocation": "Los Angeles", "CarrierID": "Test Carrier", "FreightCharge": 1500.0, "Currency": "USD", "EffectiveDate": "2023-01-01T00:00:00Z"}]}}')
        field_mapping = {'OriginLocation': 'origin', 'DestinationLocation': 'destination', 'CarrierID': 'carrier', 'FreightCharge': 'freight_charge', 'Currency': 'currency', 'EffectiveDate': 'timestamp'}
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        df = connector.fetch_freight_data(field_mapping=field_mapping)
        assert isinstance(df, pandas.DataFrame)
        assert 'origin' in df.columns
        assert df['origin'][0] == 'New York'

    def test_fetch_freight_data_not_connected(self):
        """Tests that fetch_freight_data raises an exception when not connected"""
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        with pytest.raises(DataSourceException):
            connector.fetch_freight_data()

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_get_freight_orders(self, mock_get_json):
        """Tests that get_freight_orders correctly retrieves freight orders from SAP TM"""
        mock_get_json.return_value = json.loads('{"d": {"results": [{"FreightOrderID": "FO123", "TotalGrossWeight": 1000.0, "TransportationMode": "Road"}]}}')
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_freight_orders()
        assert isinstance(df, pandas.DataFrame)
        assert df['FreightOrderID'][0] == 'FO123'
        mock_get_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_get_freight_rates(self, mock_get_json):
        """Tests that get_freight_rates correctly retrieves freight rates from SAP TM"""
        mock_get_json.return_value = json.loads('{"d": {"results": [{"FreightCharge": 1500.0, "Currency": "USD", "OriginLocation": "New York"}]}}')
        connector = SAPTMConnector(json.loads(VALID_SAP_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_freight_rates()
        assert isinstance(df, pandas.DataFrame)
        assert df['FreightCharge'][0] == 1500.0
        mock_get_json.assert_called_once()


class TestOracleTMSConnector:
    """Test class for the OracleTMSConnector specialized class"""

    def test_init(self):
        """Tests that the OracleTMSConnector initializes correctly with valid connection parameters"""
        connector = OracleTMSConnector(json.loads(VALID_ORACLE_CONNECTION_PARAMS))
        assert connector.connection_params == json.loads(VALID_ORACLE_CONNECTION_PARAMS)
        assert connector.tms_type == 'oracle'
        assert connector.instance_id == 'PROD'

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_fetch_freight_data(self, mock_get_json):
        """Tests that fetch_freight_data correctly retrieves and processes Oracle TMS data"""
        mock_get_json.return_value = json.loads('{"RateList": [{"FREIGHT_COST": 1500.0, "CURRENCY_CODE": "USD", "ORIGIN_LOCATION_CODE": "NYC"}]}')
        connector = OracleTMSConnector(json.loads(VALID_ORACLE_CONNECTION_PARAMS))
        connector.connect()
        df = connector.fetch_freight_data()
        assert isinstance(df, pandas.DataFrame)
        assert df['FREIGHT_COST'][0] == 1500.0
        mock_get_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_get_rate_records(self, mock_get_json):
        """Tests that get_rate_records correctly retrieves rate records from Oracle TMS"""
        mock_get_json.return_value = json.loads('{"RateRecordList": [{"RATE_ID": "R123", "FREIGHT_COST": 1500.0, "CURRENCY_CODE": "USD"}]}')
        connector = OracleTMSConnector(json.loads(VALID_ORACLE_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_rate_records()
        assert isinstance(df, pandas.DataFrame)
        assert df['RATE_ID'][0] == 'R123'
        mock_get_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.get_json', autospec=True)
    def test_get_shipments(self, mock_get_json):
        """Tests that get_shipments correctly retrieves shipments from Oracle TMS"""
        mock_get_json.return_value = json.loads('{"ShipmentList": [{"SHIPMENT_ID": "S456", "TOTAL_WEIGHT": 1200.0, "STATUS": "Shipped"}]}')
        connector = OracleTMSConnector(json.loads(VALID_ORACLE_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_shipments()
        assert isinstance(df, pandas.DataFrame)
        assert df['SHIPMENT_ID'][0] == 'S456'
        mock_get_json.assert_called_once()


class TestJDATMSConnector:
    """Test class for the JDATMSConnector specialized class"""

    def test_init(self):
        """Tests that the JDATMSConnector initializes correctly with valid connection parameters"""
        connector = JDATMSConnector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        assert connector.connection_params == json.loads(VALID_JDA_CONNECTION_PARAMS)
        assert connector.tms_type == 'jda'
        assert connector.environment == 'production'

    @patch('src.backend.connectors.tms_connector.APIClient', autospec=True)
    def test_connect(self, MockAPIClient):
        """Tests that the connect method adds JDA-specific headers"""
        mock_api_client_instance = MockAPIClient.return_value
        connector = JDATMSConnector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        connector.connect()
        assert connector.connected is True
        assert connector.connection_params['api_key'] in mock_api_client_instance.default_headers.values()

    @patch('src.backend.connectors.tms_connector.APIClient.post_json', autospec=True)
    def test_fetch_freight_data(self, mock_post_json):
        """Tests that fetch_freight_data correctly retrieves and processes JDA TMS data"""
        mock_post_json.return_value = json.loads('{"carrierRates": [{"origin": "New York", "destination": "Los Angeles", "carrierId": "Test Carrier", "freightRate": 1500.0, "currencyCode": "USD", "effectiveDate": "2023-01-01T00:00:00Z"}]}')
        connector = JDATMSConnector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        connector.connect()
        df = connector.fetch_freight_data()
        assert isinstance(df, pandas.DataFrame)
        assert df['origin'][0] == 'New York'
        mock_post_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.post_json', autospec=True)
    def test_get_carrier_rates(self, mock_post_json):
        """Tests that get_carrier_rates correctly retrieves carrier rates from JDA TMS"""
        mock_post_json.return_value = json.loads('{"carrierRates": [{"carrierId": "C123", "freightRate": 1500.0, "currencyCode": "USD"}]}')
        connector = JDATMSConnector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_carrier_rates()
        assert isinstance(df, pandas.DataFrame)
        assert df['carrierId'][0] == 'C123'
        mock_post_json.assert_called_once()

    @patch('src.backend.connectors.tms_connector.APIClient.post_json', autospec=True)
    def test_get_load_tenders(self, mock_post_json):
        """Tests that get_load_tenders correctly retrieves load tenders from JDA TMS"""
        mock_post_json.return_value = json.loads('{"loadTenders": [{"loadId": "L456", "totalCost": 1200.0, "status": "Accepted"}]}')
        connector = JDATMSConnector(json.loads(VALID_JDA_CONNECTION_PARAMS))
        connector.connect()
        df = connector.get_load_tenders()
        assert isinstance(df, pandas.DataFrame)
        assert df['loadId'][0] == 'L456'
        mock_post_json.assert_called_once()


class TestMapTMSResponse:
    """Test class for the map_tms_response function"""

    def test_map_tms_response_sap(self):
        """Tests that map_tms_response correctly maps SAP TM response fields"""
        sap_response = {"FreightCharge": 1500.0, "Currency": "USD", "OriginLocation": "New York", "DestinationLocation": "Los Angeles", "CarrierID": "Test Carrier", "EffectiveDate": "2023-01-01T00:00:00Z"}
        field_mapping = {'FreightCharge': 'freight_charge', 'Currency': 'currency', 'OriginLocation': 'origin', 'DestinationLocation': 'destination', 'CarrierID': 'carrier', 'EffectiveDate': 'timestamp'}
        mapped_response = map_tms_response(sap_response, 'sap', field_mapping)
        assert mapped_response['freight_charge'] == 1500.0
        assert mapped_response['origin'] == 'New York'

    def test_map_tms_response_oracle(self):
        """Tests that map_tms_response correctly maps Oracle TMS response fields"""
        oracle_response = {"FREIGHT_COST": 1500.0, "CURRENCY_CODE": "USD", "ORIGIN_LOCATION_CODE": "NYC", "DESTINATION_LOCATION_CODE": "LAX", "CARRIER_CODE": "CR001", "EFFECTIVE_DATE": "2023-01-01"}
        field_mapping = {'FREIGHT_COST': 'freight_charge', 'CURRENCY_CODE': 'currency', 'ORIGIN_LOCATION_CODE': 'origin', 'DESTINATION_LOCATION_CODE': 'destination', 'CARRIER_CODE': 'carrier', 'EFFECTIVE_DATE': 'timestamp'}
        mapped_response = map_tms_response(oracle_response, 'oracle', field_mapping)
        assert mapped_response['freight_charge'] == 1500.0
        assert mapped_response['origin'] == 'NYC'

    def test_map_tms_response_jda(self):
        """Tests that map_tms_response correctly maps JDA TMS response fields"""
        jda_response = {"freightRate": 1500.0, "currencyCode": "USD", "origin": "New York", "destination": "Los Angeles", "carrierId": "Test Carrier", "effectiveDate": "2023-01-01T00:00:00Z"}
        field_mapping = {'freightRate': 'freight_charge', 'currencyCode': 'currency', 'origin': 'origin', 'destination': 'destination', 'carrierId': 'carrier', 'effectiveDate': 'timestamp'}
        mapped_response = map_tms_response(jda_response, 'jda', field_mapping)
        assert mapped_response['freight_charge'] == 1500.0
        assert mapped_response['origin'] == 'New York'

    def test_map_tms_response_default_mapping(self):
        """Tests that map_tms_response uses default mapping when none is provided"""
        sap_response = {"FreightCharge": 1500.0, "Currency": "USD", "OriginLocation": "New York", "DestinationLocation": "Los Angeles", "CarrierID": "Test Carrier", "EffectiveDate": "2023-01-01T00:00:00Z"}
        mapped_response = map_tms_response(sap_response, 'sap')
        assert mapped_response['freight_charge'] == 1500.0
        assert mapped_response['origin'] == 'New York'

    def test_map_tms_response_missing_fields(self):
        """Tests that map_tms_response handles missing fields gracefully"""
        sap_response = {"FreightCharge": 1500.0, "Currency": "USD", "OriginLocation": "New York"}
        field_mapping = {'FreightCharge': 'freight_charge', 'Currency': 'currency', 'OriginLocation': 'origin', 'DestinationLocation': 'destination', 'CarrierID': 'carrier', 'EffectiveDate': 'timestamp'}
        mapped_response = map_tms_response(sap_response, 'sap', field_mapping)
        assert mapped_response['freight_charge'] == 1500.0
        assert mapped_response['origin'] == 'New York'
        assert 'destination' not in mapped_response
        assert 'carrier' not in mapped_response
        assert 'timestamp' not in mapped_response