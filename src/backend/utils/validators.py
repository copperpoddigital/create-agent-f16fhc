"""
Utility module providing data validation functions for the Freight Price Movement Agent.

This module implements validators for various data types, formats, and business rules
to ensure data integrity throughout the application.
"""

import re
import decimal
from decimal import Decimal
import datetime
import html
import ipaddress
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.exceptions import ValidationException
from ..models.enums import TransportMode, GranularityType, DataSourceType, OutputFormat
from ..core.logging import logger
from .date_utils import is_future_date, is_past_date

# Regular expression patterns for validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_REGEX = re.compile(r'^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$')
CURRENCY_CODE_REGEX = re.compile(r'^[A-Z]{3}$')

# Lists of valid enum values
TRANSPORT_MODE_VALUES = [mode.name for mode in TransportMode]
ALLOWED_GRANULARITY_VALUES = [granularity.name for granularity in GranularityType]
ALLOWED_OUTPUT_FORMATS = [output_format.name for output_format in OutputFormat]
ALLOWED_DATA_SOURCE_TYPES = [source_type.name for source_type in DataSourceType]


def validate_required_fields(data: dict, required_fields: List[str]) -> bool:
    """
    Validates that all required fields are present in the data.
    
    Args:
        data: Dictionary containing data to validate
        required_fields: List of field names that must be present
        
    Returns:
        True if all required fields are present
        
    Raises:
        ValidationException: If any required fields are missing
    """
    if data is None or not isinstance(data, dict):
        raise ValidationException("Data is required and must be a dictionary")
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationException(
            f"Missing required fields: {', '.join(missing_fields)}",
            {"missing_fields": missing_fields}
        )
    
    return True


def validate_numeric(value: Any, min_value: Optional[Union[int, float, Decimal]] = None, 
                     max_value: Optional[Union[int, float, Decimal]] = None) -> Decimal:
    """
    Validates that a value is numeric and within specified range.
    
    Args:
        value: The value to validate
        min_value: Optional minimum value (inclusive)
        max_value: Optional maximum value (inclusive)
        
    Returns:
        Validated numeric value as Decimal
        
    Raises:
        ValidationException: If value is not numeric or out of range
    """
    if value is None:
        raise ValidationException("Value is required")
    
    try:
        # Convert to Decimal for precise comparison
        decimal_value = Decimal(str(value))
    except (decimal.InvalidOperation, ValueError, TypeError):
        raise ValidationException(f"Value '{value}' is not a valid number")
    
    if min_value is not None and decimal_value < Decimal(str(min_value)):
        raise ValidationException(
            f"Value {decimal_value} is less than minimum allowed value {min_value}"
        )
    
    if max_value is not None and decimal_value > Decimal(str(max_value)):
        raise ValidationException(
            f"Value {decimal_value} is greater than maximum allowed value {max_value}"
        )
    
    return decimal_value


def validate_string(value: Any, min_length: Optional[int] = None, 
                    max_length: Optional[int] = None) -> str:
    """
    Validates that a value is a string with length within specified range.
    
    Args:
        value: The value to validate
        min_length: Optional minimum length (inclusive)
        max_length: Optional maximum length (inclusive)
        
    Returns:
        Validated string value
        
    Raises:
        ValidationException: If value is not a string or length is out of range
    """
    if value is None:
        raise ValidationException("Value is required")
    
    # Convert to string if not already
    str_value = str(value)
    
    if min_length is not None and len(str_value) < min_length:
        raise ValidationException(
            f"String length {len(str_value)} is less than minimum allowed length {min_length}"
        )
    
    if max_length is not None and len(str_value) > max_length:
        raise ValidationException(
            f"String length {len(str_value)} is greater than maximum allowed length {max_length}"
        )
    
    return str_value


def validate_email(value: str) -> bool:
    """
    Validates that a value is a properly formatted email address.
    
    Args:
        value: The value to validate
        
    Returns:
        True if email is valid
        
    Raises:
        ValidationException: If value is not a valid email address
    """
    if not value or not isinstance(value, str):
        raise ValidationException("Email address is required and must be a string")
    
    if not EMAIL_REGEX.match(value):
        raise ValidationException(f"'{value}' is not a valid email address")
    
    return True


def validate_url(value: str) -> bool:
    """
    Validates that a value is a properly formatted URL.
    
    Args:
        value: The value to validate
        
    Returns:
        True if URL is valid
        
    Raises:
        ValidationException: If value is not a valid URL
    """
    if not value or not isinstance(value, str):
        raise ValidationException("URL is required and must be a string")
    
    if not URL_REGEX.match(value):
        raise ValidationException(f"'{value}' is not a valid URL")
    
    return True


def validate_ip_address(value: str) -> bool:
    """
    Validates that a value is a properly formatted IP address (IPv4 or IPv6).
    
    Args:
        value: The value to validate
        
    Returns:
        True if IP address is valid
        
    Raises:
        ValidationException: If value is not a valid IP address
    """
    if not value or not isinstance(value, str):
        raise ValidationException("IP address is required and must be a string")
    
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        raise ValidationException(f"'{value}' is not a valid IP address")


def validate_enum_value(value: Any, allowed_values: List[str], 
                        case_sensitive: bool = True) -> bool:
    """
    Validates that a value is one of the allowed enum values.
    
    Args:
        value: The value to validate
        allowed_values: List of valid values
        case_sensitive: Whether comparison is case-sensitive
        
    Returns:
        True if value is in allowed_values
        
    Raises:
        ValidationException: If value is not in allowed_values
    """
    if value is None:
        raise ValidationException("Value is required")
    
    # Convert to string if not already
    str_value = str(value)
    
    # For case-insensitive comparison, convert everything to uppercase
    if not case_sensitive:
        str_value = str_value.upper()
        allowed_values = [v.upper() for v in allowed_values]
    
    if str_value not in allowed_values:
        raise ValidationException(
            f"Value '{value}' is not one of the allowed values: {', '.join(allowed_values)}"
        )
    
    return True


def validate_transport_mode(value: str) -> bool:
    """
    Validates that a value is a valid transport mode.
    
    Args:
        value: The value to validate
        
    Returns:
        True if transport mode is valid
        
    Raises:
        ValidationException: If value is not a valid transport mode
    """
    return validate_enum_value(value, TRANSPORT_MODE_VALUES)


def validate_granularity(value: str) -> bool:
    """
    Validates that a value is a valid time granularity.
    
    Args:
        value: The value to validate
        
    Returns:
        True if granularity is valid
        
    Raises:
        ValidationException: If value is not a valid granularity
    """
    return validate_enum_value(value, ALLOWED_GRANULARITY_VALUES)


def validate_output_format(value: str) -> bool:
    """
    Validates that a value is a valid output format.
    
    Args:
        value: The value to validate
        
    Returns:
        True if output format is valid
        
    Raises:
        ValidationException: If value is not a valid output format
    """
    return validate_enum_value(value, ALLOWED_OUTPUT_FORMATS)


def validate_currency_code(value: str) -> bool:
    """
    Validates that a value is a valid 3-letter currency code.
    
    Args:
        value: The value to validate
        
    Returns:
        True if currency code is valid
        
    Raises:
        ValidationException: If value is not a valid currency code
    """
    if not value or not isinstance(value, str):
        raise ValidationException("Currency code is required and must be a string")
    
    if not CURRENCY_CODE_REGEX.match(value):
        raise ValidationException(
            f"'{value}' is not a valid currency code. Must be 3 uppercase letters."
        )
    
    return True


def validate_date(value: Union[str, datetime.date, datetime.datetime], 
                  allow_future: bool = False) -> datetime.datetime:
    """
    Validates that a value is a valid date or datetime.
    
    Args:
        value: The value to validate
        allow_future: Whether future dates are allowed
        
    Returns:
        Validated datetime object
        
    Raises:
        ValidationException: If value is not a valid date or violates constraints
    """
    if value is None:
        raise ValidationException("Date is required")
    
    # Convert string to datetime
    if isinstance(value, str):
        try:
            from dateutil import parser
            dt_value = parser.parse(value)
        except (ValueError, TypeError):
            raise ValidationException(f"'{value}' is not a valid date format")
    # Convert date to datetime
    elif isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        dt_value = datetime.datetime.combine(value, datetime.time())
    # Use as is if already datetime
    elif isinstance(value, datetime.datetime):
        dt_value = value
    else:
        raise ValidationException(f"Value '{value}' cannot be converted to a date")
    
    # Check if future date is allowed
    if not allow_future and is_future_date(dt_value):
        raise ValidationException("Future dates are not allowed")
    
    return dt_value


def validate_freight_data(data: dict) -> dict:
    """
    Validates freight data record against business rules.
    
    Args:
        data: Dictionary containing freight data to validate
        
    Returns:
        Validated and potentially enriched freight data
        
    Raises:
        ValidationException: If validation fails
    """
    # Define required fields for freight data
    required_fields = [
        'record_date', 
        'origin', 
        'destination', 
        'freight_charge', 
        'currency_code', 
        'transport_mode'
    ]
    
    # Validate required fields
    validate_required_fields(data, required_fields)
    
    # Validate individual fields
    data['record_date'] = validate_date(data['record_date'])
    data['freight_charge'] = validate_numeric(data['freight_charge'], min_value=0)
    validate_currency_code(data['currency_code'])
    validate_transport_mode(data['transport_mode'])
    
    # Additional business validation
    # Check for potential data quality issues
    
    # Unusually high freight charge (example threshold)
    if data['freight_charge'] > 100000:
        logger.warning(
            f"Unusually high freight charge detected: {data['freight_charge']} {data['currency_code']}",
            extra={
                'data_quality_warning': 'high_freight_charge', 
                'record_id': data.get('id', 'unknown')
            }
        )
        # Flag for review but don't reject
        data['data_quality_flag'] = 'REVIEW_HIGH_CHARGE'
    
    # Unusually low freight charge
    if data['freight_charge'] < 1:
        logger.warning(
            f"Unusually low freight charge detected: {data['freight_charge']} {data['currency_code']}",
            extra={
                'data_quality_warning': 'low_freight_charge', 
                'record_id': data.get('id', 'unknown')
            }
        )
        data['data_quality_flag'] = 'REVIEW_LOW_CHARGE'
    
    # Validate origin and destination are not the same
    if data['origin'] == data['destination']:
        logger.warning(
            f"Origin and destination are the same: {data['origin']}",
            extra={
                'data_quality_warning': 'same_origin_destination', 
                'record_id': data.get('id', 'unknown')
            }
        )
        data['data_quality_flag'] = 'REVIEW_SAME_LOCATIONS'
    
    return data


def validate_time_period(start_date: Union[str, datetime.date, datetime.datetime],
                         end_date: Union[str, datetime.date, datetime.datetime],
                         granularity: Optional[str] = None) -> bool:
    """
    Validates time period parameters for analysis.
    
    Args:
        start_date: The start date of the period
        end_date: The end date of the period
        granularity: Optional time granularity
        
    Returns:
        True if time period is valid
        
    Raises:
        ValidationException: If validation fails
    """
    # Validate date formats
    start_dt = validate_date(start_date)
    end_dt = validate_date(end_date)
    
    # Ensure start date is before end date
    if start_dt >= end_dt:
        raise ValidationException(
            "Start date must be earlier than end date",
            {"start_date": start_date, "end_date": end_date}
        )
    
    # Validate granularity if provided
    if granularity:
        validate_granularity(granularity)
    
    return True


def validate_data_source_config(config: dict) -> bool:
    """
    Validates data source configuration parameters.
    
    Args:
        config: Dictionary containing configuration parameters
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValidationException: If validation fails
    """
    # Common required fields for all data sources
    common_required = ['name', 'source_type', 'description']
    validate_required_fields(config, common_required)
    
    # Validate source type
    source_type = config['source_type']
    validate_enum_value(source_type, ALLOWED_DATA_SOURCE_TYPES)
    
    # Specific validation based on source type
    if source_type == 'CSV':
        # CSV specific fields
        csv_required = ['file_path', 'date_format', 'field_mapping']
        validate_required_fields(config, csv_required)
        
        # Validate file path exists
        validate_string(config['file_path'])
        
        # Validate date format
        validate_string(config['date_format'])
        
        # Validate field mapping exists and has required mappings
        field_mapping = config.get('field_mapping', {})
        if not isinstance(field_mapping, dict):
            raise ValidationException("Field mapping must be a dictionary")
        
        required_mappings = ['freight_charge', 'origin', 'destination', 'date', 'currency']
        missing_mappings = []
        for field in required_mappings:
            if field not in field_mapping:
                missing_mappings.append(field)
        
        if missing_mappings:
            raise ValidationException(
                f"Missing required field mappings: {', '.join(missing_mappings)}",
                {"missing_mappings": missing_mappings}
            )
    
    elif source_type == 'DATABASE':
        # Database specific fields
        db_required = ['connection_string', 'query', 'field_mapping']
        validate_required_fields(config, db_required)
        
        # Validate connection string
        validate_string(config['connection_string'])
        
        # Validate query
        validate_string(config['query'])
        
        # Validate field mapping as above
        field_mapping = config.get('field_mapping', {})
        if not isinstance(field_mapping, dict):
            raise ValidationException("Field mapping must be a dictionary")
        
        required_mappings = ['freight_charge', 'origin', 'destination', 'date', 'currency']
        missing_mappings = []
        for field in required_mappings:
            if field not in field_mapping:
                missing_mappings.append(field)
        
        if missing_mappings:
            raise ValidationException(
                f"Missing required field mappings: {', '.join(missing_mappings)}",
                {"missing_mappings": missing_mappings}
            )
    
    elif source_type == 'API':
        # API specific fields
        api_required = ['url', 'auth_params', 'field_mapping']
        validate_required_fields(config, api_required)
        
        # Validate URL
        validate_url(config['url'])
        
        # Validate auth params
        auth_params = config.get('auth_params', {})
        if not isinstance(auth_params, dict):
            raise ValidationException("Auth parameters must be a dictionary")
        
        # Validate field mapping
        field_mapping = config.get('field_mapping', {})
        if not isinstance(field_mapping, dict):
            raise ValidationException("Field mapping must be a dictionary")
        
        required_mappings = ['freight_charge', 'origin', 'destination', 'date', 'currency']
        missing_mappings = []
        for field in required_mappings:
            if field not in field_mapping:
                missing_mappings.append(field)
        
        if missing_mappings:
            raise ValidationException(
                f"Missing required field mappings: {', '.join(missing_mappings)}",
                {"missing_mappings": missing_mappings}
            )
    
    elif source_type in ['TMS', 'ERP']:
        # TMS/ERP specific fields
        ext_required = ['connection_params', 'field_mapping']
        validate_required_fields(config, ext_required)
        
        # Validate connection params
        conn_params = config.get('connection_params', {})
        if not isinstance(conn_params, dict):
            raise ValidationException("Connection parameters must be a dictionary")
        
        # Validate specific connection params based on the system type
        if source_type == 'TMS':
            tms_required = ['system_type', 'api_key', 'endpoint']
            missing_params = []
            for param in tms_required:
                if param not in conn_params:
                    missing_params.append(param)
            
            if missing_params:
                raise ValidationException(
                    f"Missing required TMS connection parameters: {', '.join(missing_params)}",
                    {"missing_params": missing_params}
                )
        
        elif source_type == 'ERP':
            erp_required = ['system_type', 'credentials', 'endpoint']
            missing_params = []
            for param in erp_required:
                if param not in conn_params:
                    missing_params.append(param)
            
            if missing_params:
                raise ValidationException(
                    f"Missing required ERP connection parameters: {', '.join(missing_params)}",
                    {"missing_params": missing_params}
                )
        
        # Validate field mapping
        field_mapping = config.get('field_mapping', {})
        if not isinstance(field_mapping, dict):
            raise ValidationException("Field mapping must be a dictionary")
        
        required_mappings = ['freight_charge', 'origin', 'destination', 'date', 'currency']
        missing_mappings = []
        for field in required_mappings:
            if field not in field_mapping:
                missing_mappings.append(field)
        
        if missing_mappings:
            raise ValidationException(
                f"Missing required field mappings: {', '.join(missing_mappings)}",
                {"missing_mappings": missing_mappings}
            )
    
    return True


def validate_analysis_params(params: dict) -> bool:
    """
    Validates analysis parameters for price movement calculation.
    
    Args:
        params: Dictionary containing analysis parameters
        
    Returns:
        True if parameters are valid
        
    Raises:
        ValidationException: If validation fails
    """
    # Required parameters
    required_fields = ['start_date', 'end_date']
    validate_required_fields(params, required_fields)
    
    # Validate time period
    validate_time_period(
        params['start_date'], 
        params['end_date'], 
        params.get('granularity')
    )
    
    # Validate filters if provided
    filters = params.get('filters', {})
    if filters and not isinstance(filters, dict):
        raise ValidationException("Filters must be a dictionary")
    
    # Validate specific filter types
    for filter_name, filter_value in filters.items():
        if filter_name == 'routes' and not isinstance(filter_value, list):
            raise ValidationException("Routes filter must be a list")
        
        if filter_name == 'carriers' and not isinstance(filter_value, list):
            raise ValidationException("Carriers filter must be a list")
        
        if filter_name == 'transport_modes':
            if not isinstance(filter_value, list):
                raise ValidationException("Transport modes filter must be a list")
            
            # Validate each transport mode
            for mode in filter_value:
                validate_transport_mode(mode)
    
    # Validate output format if provided
    if 'output_format' in params:
        validate_output_format(params['output_format'])
    
    return True


def sanitize_input(value: str) -> str:
    """
    Sanitizes input strings to prevent injection attacks.
    
    Args:
        value: The input string to sanitize
        
    Returns:
        Sanitized string
    """
    if value is None:
        return ""
    
    # Convert to string if not already
    if not isinstance(value, str):
        value = str(value)
    
    # Escape HTML special characters
    sanitized = html.escape(value)
    
    # Remove potentially dangerous patterns
    sanitized = re.sub(r'[\'";`]', '', sanitized)  # Remove quote characters
    
    return sanitized


class DataValidator:
    """
    Class for schema-based validation of complex data structures.
    
    This validator uses a schema to validate data against type, format, 
    and business rule constraints.
    """
    
    def __init__(self, schema: dict):
        """
        Initializes the DataValidator with a validation schema.
        
        Args:
            schema: Dictionary defining the validation rules for each field
        """
        self._schema = schema
        self._errors = {}
        self._validated_data = {}
    
    def validate(self, data: dict) -> bool:
        """
        Validates data against the schema.
        
        Args:
            data: Dictionary containing data to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        # Reset errors and validated data
        self._errors = {}
        self._validated_data = {}
        
        # Check if data is None or not a dictionary
        if data is None or not isinstance(data, dict):
            self._errors['__all__'] = "Data is required and must be a dictionary"
            return False
        
        # Validate each field against schema
        for field_name, rules in self._schema.items():
            # Get field value, using None if field is missing
            value = data.get(field_name)
            
            # Check if field is required
            if rules.get('required', False) and (value is None or value == ''):
                self._errors[field_name] = f"{field_name} is required"
                continue
            
            # Skip validation for optional fields that are None
            if value is None and not rules.get('required', False):
                continue
            
            # Validate field
            is_valid, processed_value, error = self._validate_field(field_name, value, rules)
            
            if is_valid:
                self._validated_data[field_name] = processed_value
            else:
                self._errors[field_name] = error
        
        # Return True if no errors
        return len(self._errors) == 0
    
    def get_errors(self) -> dict:
        """
        Returns validation errors.
        
        Returns:
            Dictionary of validation errors by field
        """
        return self._errors
    
    def has_errors(self) -> bool:
        """
        Checks if validation has errors.
        
        Returns:
            True if errors exist, False otherwise
        """
        return len(self._errors) > 0
    
    def get_validated_data(self) -> dict:
        """
        Returns the validated data.
        
        Returns:
            Dictionary of validated data
        """
        return self._validated_data
    
    def _validate_field(self, field_name: str, value: Any, 
                       rules: dict) -> Tuple[bool, Any, Optional[str]]:
        """
        Validates a single field against its rules.
        
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            rules: Dictionary of validation rules
            
        Returns:
            Tuple of (is_valid, processed_value, error_message)
        """
        field_type = rules.get('type', 'string')
        
        try:
            # Type-specific validation
            if field_type == 'string':
                min_length = rules.get('min_length')
                max_length = rules.get('max_length')
                processed_value = validate_string(value, min_length, max_length)
                
                # Pattern validation if specified
                if 'pattern' in rules and not re.match(rules['pattern'], processed_value):
                    return False, None, f"{field_name} does not match required pattern"
                
            elif field_type == 'numeric':
                min_value = rules.get('min_value')
                max_value = rules.get('max_value')
                processed_value = validate_numeric(value, min_value, max_value)
                
            elif field_type == 'boolean':
                if isinstance(value, bool):
                    processed_value = value
                elif isinstance(value, str):
                    processed_value = value.lower() in ('true', 't', '1', 'yes', 'y')
                else:
                    processed_value = bool(value)
                
            elif field_type == 'date':
                allow_future = rules.get('allow_future', False)
                processed_value = validate_date(value, allow_future)
                
            elif field_type == 'email':
                validate_email(value)
                processed_value = value
                
            elif field_type == 'url':
                validate_url(value)
                processed_value = value
                
            elif field_type == 'enum':
                choices = rules.get('choices', [])
                case_sensitive = rules.get('case_sensitive', True)
                validate_enum_value(value, choices, case_sensitive)
                processed_value = value
                
            else:
                # Unknown type, treat as string
                processed_value = str(value)
            
            # Custom validation function if provided
            if 'validator' in rules and callable(rules['validator']):
                custom_validator = rules['validator']
                custom_result = custom_validator(processed_value)
                
                # If validator returns False or raises ValidationException
                if custom_result is False:
                    return False, None, f"{field_name} failed custom validation"
            
            return True, processed_value, None
            
        except ValidationException as e:
            # Capture validation error
            return False, None, str(e)
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error validating {field_name}: {str(e)}")
            return False, None, f"Validation error: {str(e)}"