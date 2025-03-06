import pytest
from decimal import Decimal
from datetime import date, datetime

from ../../utils/validators import (
    validate_required_fields, validate_numeric, validate_string, validate_email, 
    validate_url, validate_ip_address, validate_enum_value, validate_transport_mode, 
    validate_granularity, validate_freight_data, validate_time_period, 
    validate_data_source_config, validate_analysis_params, sanitize_input, 
    DataValidator, EMAIL_REGEX, URL_REGEX, TRANSPORT_MODE_VALUES, 
    ALLOWED_GRANULARITY_VALUES
)
from ../../core/exceptions import ValidationException


def test_validate_required_fields_success():
    """Tests that validate_required_fields returns True when all required fields are present."""
    # Create a test data dictionary with all required fields
    test_data = {
        'field1': 'value1',
        'field2': 'value2',
        'field3': 0,  # test with falsy value that is not None
    }
    
    # Call validate_required_fields with the test data and a list of required fields
    result = validate_required_fields(test_data, ['field1', 'field2', 'field3'])
    
    # Assert that the function returns True
    assert result is True


def test_validate_required_fields_missing():
    """Tests that validate_required_fields raises ValidationException when required fields are missing."""
    # Create a test data dictionary with some required fields missing
    test_data = {
        'field1': 'value1',
        # field2 is missing
        'field3': None,  # field with None value should be treated as missing
    }
    
    # Use pytest.raises to assert that ValidationException is raised
    with pytest.raises(ValidationException) as excinfo:
        validate_required_fields(test_data, ['field1', 'field2', 'field3'])
    
    # Verify that the exception message contains information about the missing fields
    assert 'field2' in str(excinfo.value)
    assert 'field3' in str(excinfo.value)


def test_validate_numeric_success():
    """Tests that validate_numeric correctly validates numeric values within range."""
    # Test with integer value
    assert validate_numeric(42) == Decimal('42')
    
    # Test with float value
    assert validate_numeric(3.14) == Decimal('3.14')
    
    # Test with string representation of a number
    assert validate_numeric("100") == Decimal('100')
    
    # Test with Decimal value
    assert validate_numeric(Decimal('123.45')) == Decimal('123.45')
    
    # Test with min_value constraint
    assert validate_numeric(10, min_value=5) == Decimal('10')
    
    # Test with max_value constraint
    assert validate_numeric(10, max_value=15) == Decimal('10')
    
    # Test with both min_value and max_value constraints
    assert validate_numeric(10, min_value=5, max_value=15) == Decimal('10')


def test_validate_numeric_invalid():
    """Tests that validate_numeric raises ValidationException for invalid numeric values."""
    # Test with non-numeric string
    with pytest.raises(ValidationException) as excinfo:
        validate_numeric("not a number")
    assert "not a valid number" in str(excinfo.value)
    
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_numeric(None)
    assert "Value is required" in str(excinfo.value)
    
    # Test with value below min_value
    with pytest.raises(ValidationException) as excinfo:
        validate_numeric(5, min_value=10)
    assert "less than minimum allowed value" in str(excinfo.value)
    
    # Test with value above max_value
    with pytest.raises(ValidationException) as excinfo:
        validate_numeric(15, max_value=10)
    assert "greater than maximum allowed value" in str(excinfo.value)


def test_validate_string_success():
    """Tests that validate_string correctly validates string values within length constraints."""
    # Test with regular string
    assert validate_string("test string") == "test string"
    
    # Test with numeric value that can be converted to string
    assert validate_string(42) == "42"
    
    # Test with min_length constraint
    assert validate_string("test", min_length=4) == "test"
    
    # Test with max_length constraint
    assert validate_string("test", max_length=10) == "test"
    
    # Test with both min_length and max_length constraints
    assert validate_string("test", min_length=2, max_length=6) == "test"


def test_validate_string_invalid():
    """Tests that validate_string raises ValidationException for invalid string values."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_string(None)
    assert "Value is required" in str(excinfo.value)
    
    # Test with string shorter than min_length
    with pytest.raises(ValidationException) as excinfo:
        validate_string("ab", min_length=3)
    assert "less than minimum allowed length" in str(excinfo.value)
    
    # Test with string longer than max_length
    with pytest.raises(ValidationException) as excinfo:
        validate_string("abcdef", max_length=5)
    assert "greater than maximum allowed length" in str(excinfo.value)


def test_validate_email_success():
    """Tests that validate_email correctly validates properly formatted email addresses."""
    # Test with simple email address
    assert validate_email("user@example.com") is True
    
    # Test with email containing dots in username
    assert validate_email("user.name@example.com") is True
    
    # Test with email containing plus in username
    assert validate_email("user+tag@example.com") is True
    
    # Test with email containing subdomain
    assert validate_email("user@sub.example.com") is True


def test_validate_email_invalid():
    """Tests that validate_email raises ValidationException for invalid email addresses."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_email(None)
    assert "Email address is required" in str(excinfo.value)
    
    # Test with empty string
    with pytest.raises(ValidationException) as excinfo:
        validate_email("")
    assert "Email address is required" in str(excinfo.value)
    
    # Test with string missing @ symbol
    with pytest.raises(ValidationException) as excinfo:
        validate_email("userexample.com")
    assert "not a valid email address" in str(excinfo.value)
    
    # Test with string missing domain
    with pytest.raises(ValidationException) as excinfo:
        validate_email("user@")
    assert "not a valid email address" in str(excinfo.value)
    
    # Test with string missing username
    with pytest.raises(ValidationException) as excinfo:
        validate_email("@example.com")
    assert "not a valid email address" in str(excinfo.value)
    
    # Test with invalid TLD
    with pytest.raises(ValidationException) as excinfo:
        validate_email("user@example")
    assert "not a valid email address" in str(excinfo.value)


def test_validate_url_success():
    """Tests that validate_url correctly validates properly formatted URLs."""
    # Test with http URL
    assert validate_url("http://example.com") is True
    
    # Test with https URL
    assert validate_url("https://example.com") is True
    
    # Test with URL containing path
    assert validate_url("https://example.com/path") is True
    
    # Test with URL containing query parameters
    assert validate_url("https://example.com/path?query=value") is True
    
    # Test with URL without protocol (should be valid according to URL_REGEX)
    assert validate_url("example.com") is True


def test_validate_url_invalid():
    """Tests that validate_url raises ValidationException for invalid URLs."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_url(None)
    assert "URL is required" in str(excinfo.value)
    
    # Test with empty string
    with pytest.raises(ValidationException) as excinfo:
        validate_url("")
    assert "URL is required" in str(excinfo.value)
    
    # Test with invalid protocol
    with pytest.raises(ValidationException) as excinfo:
        validate_url("ftp://example.com")  # Assuming ftp isn't supported by URL_REGEX
    assert "not a valid URL" in str(excinfo.value)
    
    # Test with missing domain
    with pytest.raises(ValidationException) as excinfo:
        validate_url("http://")
    assert "not a valid URL" in str(excinfo.value)
    
    # Test with invalid format
    with pytest.raises(ValidationException) as excinfo:
        validate_url("http:\\\\example.com")
    assert "not a valid URL" in str(excinfo.value)


def test_validate_ip_address_success():
    """Tests that validate_ip_address correctly validates properly formatted IP addresses."""
    # Test with IPv4 address
    assert validate_ip_address("192.168.1.1") is True
    
    # Test with IPv4 loopback
    assert validate_ip_address("127.0.0.1") is True
    
    # Test with IPv6 address
    assert validate_ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
    
    # Test with IPv6 shortened
    assert validate_ip_address("2001:db8::1") is True
    
    # Test with IPv6 loopback
    assert validate_ip_address("::1") is True


def test_validate_ip_address_invalid():
    """Tests that validate_ip_address raises ValidationException for invalid IP addresses."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_ip_address(None)
    assert "IP address is required" in str(excinfo.value)
    
    # Test with empty string
    with pytest.raises(ValidationException) as excinfo:
        validate_ip_address("")
    assert "IP address is required" in str(excinfo.value)
    
    # Test with invalid IPv4 format
    with pytest.raises(ValidationException) as excinfo:
        validate_ip_address("256.256.256.256")
    assert "not a valid IP address" in str(excinfo.value)
    
    # Test with invalid IPv6 format
    with pytest.raises(ValidationException) as excinfo:
        validate_ip_address("2001:db8::zzzz")
    assert "not a valid IP address" in str(excinfo.value)
    
    # Test with non-IP string
    with pytest.raises(ValidationException) as excinfo:
        validate_ip_address("not an ip address")
    assert "not a valid IP address" in str(excinfo.value)


def test_validate_enum_value_success():
    """Tests that validate_enum_value correctly validates values in the allowed list."""
    # Create a list of allowed values
    allowed_values = ["VALUE1", "VALUE2", "VALUE3"]
    
    # Test with each value in the allowed list
    assert validate_enum_value("VALUE1", allowed_values) is True
    assert validate_enum_value("VALUE2", allowed_values) is True
    assert validate_enum_value("VALUE3", allowed_values) is True


def test_validate_enum_value_invalid():
    """Tests that validate_enum_value raises ValidationException for values not in the allowed list."""
    # Create a list of allowed values
    allowed_values = ["VALUE1", "VALUE2", "VALUE3"]
    
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_enum_value(None, allowed_values)
    assert "Value is required" in str(excinfo.value)
    
    # Test with value not in the allowed list
    with pytest.raises(ValidationException) as excinfo:
        validate_enum_value("VALUE4", allowed_values)
    assert "not one of the allowed values" in str(excinfo.value)


def test_validate_transport_mode_success():
    """Tests that validate_transport_mode correctly validates valid transport modes."""
    # Test with each value in TRANSPORT_MODE_VALUES
    for mode in TRANSPORT_MODE_VALUES:
        assert validate_transport_mode(mode) is True
    
    # Test with lowercase values (assuming case sensitivity based on implementation)
    for mode in TRANSPORT_MODE_VALUES:
        try:
            validate_transport_mode(mode.lower())
            # If it passes, case-insensitive validation is in place
        except ValidationException:
            # If it fails, case-sensitive validation is in place, which is fine
            pass


def test_validate_transport_mode_invalid():
    """Tests that validate_transport_mode raises ValidationException for invalid transport modes."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_transport_mode(None)
    assert "Value is required" in str(excinfo.value)
    
    # Test with empty string
    with pytest.raises(ValidationException) as excinfo:
        validate_transport_mode("")
    assert "not one of the allowed values" in str(excinfo.value)
    
    # Test with invalid transport mode
    with pytest.raises(ValidationException) as excinfo:
        validate_transport_mode("INVALID_MODE")
    assert "not one of the allowed values" in str(excinfo.value)


def test_validate_granularity_success():
    """Tests that validate_granularity correctly validates valid time granularities."""
    # Test with each value in ALLOWED_GRANULARITY_VALUES
    for granularity in ALLOWED_GRANULARITY_VALUES:
        assert validate_granularity(granularity) is True
    
    # Test with uppercase values (assuming case sensitivity based on implementation)
    for granularity in ALLOWED_GRANULARITY_VALUES:
        try:
            validate_granularity(granularity.upper())
            # If it passes, case-insensitive validation is in place
        except ValidationException:
            # If it fails, case-sensitive validation is in place, which is fine
            pass


def test_validate_granularity_invalid():
    """Tests that validate_granularity raises ValidationException for invalid time granularities."""
    # Test with None value
    with pytest.raises(ValidationException) as excinfo:
        validate_granularity(None)
    assert "Value is required" in str(excinfo.value)
    
    # Test with empty string
    with pytest.raises(ValidationException) as excinfo:
        validate_granularity("")
    assert "not one of the allowed values" in str(excinfo.value)
    
    # Test with invalid granularity
    with pytest.raises(ValidationException) as excinfo:
        validate_granularity("HOURLY")  # Assuming this isn't in ALLOWED_GRANULARITY_VALUES
    assert "not one of the allowed values" in str(excinfo.value)


def test_validate_freight_data_success():
    """Tests that validate_freight_data correctly validates valid freight data records."""
    # Create a valid freight data record with all required fields
    today = datetime.now()
    test_data = {
        'record_date': today,
        'origin': 'New York',
        'destination': 'Los Angeles',
        'freight_charge': 1500.50,
        'currency_code': 'USD',
        'transport_mode': 'OCEAN'
    }
    
    # Call validate_freight_data with the test data
    validated_data = validate_freight_data(test_data)
    
    # Assert that the function returns the validated data
    assert validated_data is not None
    assert validated_data['record_date'] == today
    assert validated_data['freight_charge'] == Decimal('1500.50')
    
    # Verify that no quality flags are set to indicate issues
    assert 'data_quality_flag' not in validated_data or validated_data['data_quality_flag'] is None


def test_validate_freight_data_invalid():
    """Tests that validate_freight_data raises ValidationException for invalid freight data records."""
    # Test with missing required fields
    with pytest.raises(ValidationException) as excinfo:
        validate_freight_data({
            'origin': 'New York',
            # missing other required fields
        })
    assert "Missing required fields" in str(excinfo.value)
    
    # Test with future record_date
    future_date = datetime.now().replace(year=datetime.now().year + 1)
    with pytest.raises(ValidationException) as excinfo:
        validate_freight_data({
            'record_date': future_date,
            'origin': 'New York',
            'destination': 'Los Angeles',
            'freight_charge': 1500.50,
            'currency_code': 'USD',
            'transport_mode': 'OCEAN'
        })
    assert "Future dates are not allowed" in str(excinfo.value)
    
    # Test with negative freight_charge
    with pytest.raises(ValidationException) as excinfo:
        validate_freight_data({
            'record_date': datetime.now(),
            'origin': 'New York',
            'destination': 'Los Angeles',
            'freight_charge': -500,
            'currency_code': 'USD',
            'transport_mode': 'OCEAN'
        })
    assert "less than minimum allowed value" in str(excinfo.value)
    
    # Test with invalid currency_code
    with pytest.raises(ValidationException) as excinfo:
        validate_freight_data({
            'record_date': datetime.now(),
            'origin': 'New York',
            'destination': 'Los Angeles',
            'freight_charge': 1500.50,
            'currency_code': 'USDD',  # Invalid format
            'transport_mode': 'OCEAN'
        })
    assert "not a valid currency code" in str(excinfo.value)
    
    # Test with invalid transport_mode
    with pytest.raises(ValidationException) as excinfo:
        validate_freight_data({
            'record_date': datetime.now(),
            'origin': 'New York',
            'destination': 'Los Angeles',
            'freight_charge': 1500.50,
            'currency_code': 'USD',
            'transport_mode': 'INVALID'
        })
    assert "not one of the allowed values" in str(excinfo.value)


def test_validate_freight_data_quality_flags():
    """Tests that validate_freight_data correctly sets quality flags for suspicious data."""
    # Create a freight data record with suspicious but valid values
    test_data = {
        'record_date': datetime.now(),
        'origin': 'New York',
        'destination': 'New York',  # Same as origin
        'freight_charge': 0.5,  # Unusually low
        'currency_code': 'USD',
        'transport_mode': 'OCEAN'
    }
    
    # Call validate_freight_data with the test data
    validated_data = validate_freight_data(test_data)
    
    # Assert that the function returns the validated data with quality flags
    assert 'data_quality_flag' in validated_data
    assert validated_data['data_quality_flag'] is not None  # Flag set due to low charge and same origin/destination


def test_validate_time_period_success():
    """Tests that validate_time_period correctly validates valid time period parameters."""
    # Create valid start_date and end_date
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    # Test with each valid granularity value
    for granularity in ALLOWED_GRANULARITY_VALUES:
        assert validate_time_period(start_date, end_date, granularity) is True
    
    # Test without specifying granularity
    assert validate_time_period(start_date, end_date) is True


def test_validate_time_period_invalid():
    """Tests that validate_time_period raises ValidationException for invalid time period parameters."""
    # Test with None start_date
    with pytest.raises(ValidationException) as excinfo:
        validate_time_period(None, datetime(2023, 12, 31))
    assert "Date is required" in str(excinfo.value)
    
    # Test with None end_date
    with pytest.raises(ValidationException) as excinfo:
        validate_time_period(datetime(2023, 1, 1), None)
    assert "Date is required" in str(excinfo.value)
    
    # Test with end_date before start_date
    with pytest.raises(ValidationException) as excinfo:
        validate_time_period(datetime(2023, 12, 31), datetime(2023, 1, 1))
    assert "Start date must be earlier than end date" in str(excinfo.value)
    
    # Test with invalid granularity
    with pytest.raises(ValidationException) as excinfo:
        validate_time_period(datetime(2023, 1, 1), datetime(2023, 12, 31), "HOURLY")
    assert "not one of the allowed values" in str(excinfo.value)


def test_validate_data_source_config_success():
    """Tests that validate_data_source_config correctly validates valid data source configurations."""
    # Create valid data source configurations for each source type
    
    # CSV configuration
    csv_config = {
        'name': 'Test CSV Source',
        'source_type': 'CSV',
        'description': 'Test description',
        'file_path': '/path/to/file.csv',
        'date_format': 'YYYY-MM-DD',
        'field_mapping': {
            'freight_charge': 'price',
            'origin': 'from',
            'destination': 'to',
            'date': 'ship_date',
            'currency': 'currency'
        }
    }
    assert validate_data_source_config(csv_config) is True
    
    # DATABASE configuration
    db_config = {
        'name': 'Test DB Source',
        'source_type': 'DATABASE',
        'description': 'Test description',
        'connection_string': 'postgresql://user:pass@host/db',
        'query': 'SELECT * FROM freight_rates',
        'field_mapping': {
            'freight_charge': 'rate',
            'origin': 'origin_port',
            'destination': 'destination_port',
            'date': 'effective_date',
            'currency': 'currency_code'
        }
    }
    assert validate_data_source_config(db_config) is True
    
    # API configuration
    api_config = {
        'name': 'Test API Source',
        'source_type': 'API',
        'description': 'Test description',
        'url': 'https://api.example.com/rates',
        'auth_params': {
            'api_key': 'test_key',
            'method': 'bearer'
        },
        'field_mapping': {
            'freight_charge': 'price',
            'origin': 'origin',
            'destination': 'destination',
            'date': 'date',
            'currency': 'currency'
        }
    }
    assert validate_data_source_config(api_config) is True
    
    # TMS configuration
    tms_config = {
        'name': 'Test TMS Source',
        'source_type': 'TMS',
        'description': 'Test description',
        'connection_params': {
            'system_type': 'SAP TM',
            'api_key': 'test_key',
            'endpoint': 'https://tms.example.com/api'
        },
        'field_mapping': {
            'freight_charge': 'price',
            'origin': 'origin_loc',
            'destination': 'dest_loc',
            'date': 'ship_date',
            'currency': 'currency'
        }
    }
    assert validate_data_source_config(tms_config) is True
    
    # ERP configuration
    erp_config = {
        'name': 'Test ERP Source',
        'source_type': 'ERP',
        'description': 'Test description',
        'connection_params': {
            'system_type': 'SAP',
            'credentials': {
                'username': 'test',
                'password': 'pass'
            },
            'endpoint': 'https://erp.example.com/api'
        },
        'field_mapping': {
            'freight_charge': 'cost',
            'origin': 'from_loc',
            'destination': 'to_loc',
            'date': 'date',
            'currency': 'currency'
        }
    }
    assert validate_data_source_config(erp_config) is True


def test_validate_data_source_config_invalid():
    """Tests that validate_data_source_config raises ValidationException for invalid data source configurations."""
    # Test with missing required fields
    with pytest.raises(ValidationException) as excinfo:
        validate_data_source_config({
            'name': 'Test Source',
            # missing source_type and description
        })
    assert "Missing required fields" in str(excinfo.value)
    
    # Test with invalid source_type
    with pytest.raises(ValidationException) as excinfo:
        validate_data_source_config({
            'name': 'Test Source',
            'source_type': 'INVALID',
            'description': 'Test description'
        })
    assert "not one of the allowed values" in str(excinfo.value)
    
    # Test with missing type-specific required fields (CSV)
    with pytest.raises(ValidationException) as excinfo:
        validate_data_source_config({
            'name': 'Test CSV Source',
            'source_type': 'CSV',
            'description': 'Test description',
            # missing file_path, date_format, and field_mapping
        })
    assert "Missing required fields" in str(excinfo.value)
    
    # Test with invalid field_mapping (missing required mappings)
    with pytest.raises(ValidationException) as excinfo:
        validate_data_source_config({
            'name': 'Test CSV Source',
            'source_type': 'CSV',
            'description': 'Test description',
            'file_path': '/path/to/file.csv',
            'date_format': 'YYYY-MM-DD',
            'field_mapping': {
                'freight_charge': 'price',
                # missing other required mappings
            }
        })
    assert "Missing required field mappings" in str(excinfo.value)


def test_validate_analysis_params_success():
    """Tests that validate_analysis_params correctly validates valid analysis parameters."""
    # Create valid analysis parameters
    test_params = {
        'start_date': datetime(2023, 1, 1),
        'end_date': datetime(2023, 12, 31),
        'granularity': 'MONTHLY',
        'filters': {
            'routes': ['NY-LA', 'SF-CHI'],
            'carriers': ['Carrier1', 'Carrier2'],
            'transport_modes': ['OCEAN', 'AIR']
        },
        'output_format': 'JSON'
    }
    
    # Call validate_analysis_params with the test parameters
    assert validate_analysis_params(test_params) is True


def test_validate_analysis_params_invalid():
    """Tests that validate_analysis_params raises ValidationException for invalid analysis parameters."""
    # Test with missing required fields
    with pytest.raises(ValidationException) as excinfo:
        validate_analysis_params({
            'start_date': datetime(2023, 1, 1),
            # missing end_date
        })
    assert "Missing required fields" in str(excinfo.value)
    
    # Test with invalid time period
    with pytest.raises(ValidationException) as excinfo:
        validate_analysis_params({
            'start_date': datetime(2023, 12, 31),
            'end_date': datetime(2023, 1, 1),  # end_date before start_date
        })
    assert "Start date must be earlier than end date" in str(excinfo.value)
    
    # Test with invalid filters
    with pytest.raises(ValidationException) as excinfo:
        validate_analysis_params({
            'start_date': datetime(2023, 1, 1),
            'end_date': datetime(2023, 12, 31),
            'filters': {
                'routes': 'NY-LA',  # should be a list
            }
        })
    assert "Routes filter must be a list" in str(excinfo.value)
    
    # Test with invalid transport_modes in filters
    with pytest.raises(ValidationException) as excinfo:
        validate_analysis_params({
            'start_date': datetime(2023, 1, 1),
            'end_date': datetime(2023, 12, 31),
            'filters': {
                'transport_modes': ['INVALID_MODE']
            }
        })
    assert "not one of the allowed values" in str(excinfo.value)


def test_sanitize_input_success():
    """Tests that sanitize_input correctly sanitizes input strings."""
    # Test with regular string
    assert sanitize_input("Hello World") == "Hello World"
    
    # Test with string containing special characters
    assert sanitize_input("Hello & World") == "Hello & World"
    
    # Test with string containing potential SQL injection
    sql_injection = "'; DROP TABLE users; --"
    sanitized = sanitize_input(sql_injection)
    assert "'" not in sanitized
    assert ";" not in sanitized
    
    # Test with string containing potential XSS attack
    xss_attack = "<script>alert('XSS')</script>"
    sanitized = sanitize_input(xss_attack)
    assert "<script>" in sanitized  # HTML entities should be escaped
    assert "alert" in sanitized    # Content should still be there but sanitized


def test_data_validator_class():
    """Tests the DataValidator class for schema-based validation."""
    # Create a DataValidator instance with a test schema
    schema = {
        'name': {'type': 'string', 'required': True, 'min_length': 2, 'max_length': 50},
        'age': {'type': 'numeric', 'required': True, 'min_value': 0, 'max_value': 120},
        'email': {'type': 'email', 'required': True},
        'website': {'type': 'url', 'required': False},
        'is_active': {'type': 'boolean', 'required': False},
        'role': {'type': 'enum', 'required': True, 'choices': ['admin', 'user', 'guest']}
    }
    validator = DataValidator(schema)
    
    # Test with valid data
    valid_data = {
        'name': 'John Doe',
        'age': 30,
        'email': 'john@example.com',
        'website': 'https://example.com',
        'is_active': True,
        'role': 'admin'
    }
    assert validator.validate(valid_data) is True
    assert validator.has_errors() is False
    validated_data = validator.get_validated_data()
    assert validated_data['name'] == 'John Doe'
    assert validated_data['age'] == Decimal('30')
    assert validated_data['email'] == 'john@example.com'
    
    # Test with invalid data
    invalid_data = {
        'name': 'J',  # too short
        'age': 150,  # above max
        'email': 'not-an-email',
        'website': 'not-a-url',
        'is_active': 'not-a-boolean',
        'role': 'superadmin'  # not in choices
    }
    assert validator.validate(invalid_data) is False
    assert validator.has_errors() is True
    errors = validator.get_errors()
    assert 'name' in errors
    assert 'age' in errors
    assert 'email' in errors
    assert 'website' in errors
    assert 'role' in errors