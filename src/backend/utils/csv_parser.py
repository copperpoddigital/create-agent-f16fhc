#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility module for parsing, validating, and transforming CSV data in the Freight Price Movement Agent.

This module provides functionality to read CSV files, map columns to standardized schema,
validate data integrity, and prepare freight data for analysis. It implements robust error handling
and data quality checks to ensure the integrity of freight data used in price movement analysis.
"""

# Internal imports
from ..core.logging import get_logger
from ..core.exceptions import ValidationException
from .date_utils import parse_date, format_date
from .currency import is_valid_currency_code
from .validators import validate_required_fields, validate_numeric, validate_transport_mode

# External imports
import pandas as pd  # version ^1.5.0
import numpy as np  # version ^1.23.0
import os
from typing import Dict, List, Optional, Union, Any
from decimal import Decimal

# Initialize logger
logger = get_logger(__name__)

# Constants
REQUIRED_FREIGHT_FIELDS = ['record_date', 'origin', 'destination', 'carrier', 'freight_charge', 'currency_code', 'transport_mode']
DEFAULT_DELIMITER = ','
DEFAULT_ENCODING = 'utf-8'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'


def read_csv_file(file_path: str, 
                 delimiter: Optional[str] = None, 
                 encoding: Optional[str] = None,
                 has_header: Optional[bool] = None,
                 usecols: Optional[list] = None) -> pd.DataFrame:
    """
    Reads a CSV file into a pandas DataFrame with error handling.
    
    Args:
        file_path: Path to the CSV file
        delimiter: Column delimiter (default: DEFAULT_DELIMITER)
        encoding: File encoding (default: DEFAULT_ENCODING)
        has_header: Whether the file has a header row (default: True)
        usecols: List of columns to use (default: None, use all columns)
        
    Returns:
        DataFrame containing the CSV data
        
    Raises:
        ValidationException: If the file does not exist or cannot be read
    """
    # Validate file_path
    if file_path is None or not file_path.strip():
        raise ValidationException("File path is required")
    
    if not os.path.exists(file_path):
        raise ValidationException(f"File does not exist: {file_path}")
    
    # Set default values if not provided
    delimiter = delimiter or DEFAULT_DELIMITER
    encoding = encoding or DEFAULT_ENCODING
    has_header = True if has_header is None else has_header
    
    try:
        # Read CSV file into pandas DataFrame
        df = pd.read_csv(
            file_path, 
            delimiter=delimiter, 
            encoding=encoding,
            header=0 if has_header else None,
            usecols=usecols
        )
        
        # Log successful file reading
        logger.info(f"Successfully read CSV file: {file_path}, {len(df)} rows")
        return df
        
    except pd.errors.EmptyDataError:
        raise ValidationException(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValidationException(
            f"Error parsing CSV file: {file_path}", 
            details={"error": str(e)}
        )
    except UnicodeDecodeError as e:
        raise ValidationException(
            f"Error decoding CSV file: {file_path}. Try a different encoding.", 
            details={"error": str(e), "specified_encoding": encoding}
        )
    except PermissionError as e:
        raise ValidationException(
            f"Permission denied when reading file: {file_path}", 
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error reading CSV file: {file_path}", exc_info=True)
        raise ValidationException(
            f"Failed to read CSV file: {file_path}", 
            details={"error": str(e)}
        )


def validate_csv_structure(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validates the structure of a CSV DataFrame against expected columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present
        
    Returns:
        True if structure is valid, raises exception otherwise
        
    Raises:
        ValidationException: If DataFrame is invalid or missing required columns
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Validate that required_columns is not None and is a list
    if required_columns is None or not isinstance(required_columns, list):
        raise ValidationException("Required columns must be a non-empty list")
    
    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValidationException(
            f"CSV structure validation failed: Missing required columns", 
            details={"missing_columns": missing_columns}
        )
    
    logger.debug(f"CSV structure validation successful: All required columns present")
    return True


def map_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Maps source DataFrame columns to standardized column names.
    
    Args:
        df: DataFrame with source column names
        column_mapping: Dictionary mapping source column names to standardized names
        
    Returns:
        DataFrame with standardized column names
        
    Raises:
        ValidationException: If DataFrame or mapping is invalid
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Validate that column_mapping is a dictionary
    if column_mapping is None or not isinstance(column_mapping, dict):
        raise ValidationException("Column mapping must be a dictionary")
    
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        mapped_df = df.copy()
        
        # Filter the mapping to only include columns that exist in the DataFrame
        valid_mapping = {src: dest for src, dest in column_mapping.items() if src in mapped_df.columns}
        
        # Rename columns according to the mapping
        mapped_df = mapped_df.rename(columns=valid_mapping)
        
        # Log column mapping operation
        if valid_mapping:
            logger.info(f"Mapped {len(valid_mapping)} columns: {valid_mapping}")
        else:
            logger.warning("No columns were mapped: no matching source columns found")
        
        return mapped_df
        
    except Exception as e:
        logger.error(f"Error during column mapping", exc_info=True)
        raise ValidationException(
            "Failed to map columns", 
            details={"error": str(e)}
        )


def standardize_date_format(df: pd.DataFrame, 
                           date_columns: Union[str, List[str]], 
                           source_format: Optional[str] = None, 
                           target_format: Optional[str] = None) -> pd.DataFrame:
    """
    Converts date columns in the DataFrame to a standardized format.
    
    Args:
        df: DataFrame containing date columns
        date_columns: Column name(s) to standardize
        source_format: Optional format string for parsing (if None, uses flexible parsing)
        target_format: Optional format string for output (default: DEFAULT_DATE_FORMAT)
        
    Returns:
        DataFrame with standardized date columns
        
    Raises:
        ValidationException: If DataFrame is invalid or date conversion fails
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Convert single column name to list
    if isinstance(date_columns, str):
        date_columns = [date_columns]
    
    # Set default target format if not provided
    target_format = target_format or DEFAULT_DATE_FORMAT
    
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Process each date column
        for column in date_columns:
            # Check if column exists
            if column not in result_df.columns:
                logger.warning(f"Date column '{column}' not found in DataFrame, skipping")
                continue
            
            # Convert the date column
            if source_format:
                # If source format is specified, use pandas to_datetime with format
                result_df[column] = pd.to_datetime(result_df[column], format=source_format, errors='coerce')
            else:
                # If no source format, use flexible parsing
                try:
                    result_df[column] = result_df[column].apply(
                        lambda x: parse_date(x) if pd.notna(x) else None
                    )
                except Exception as e:
                    logger.warning(f"Error parsing dates in column '{column}': {str(e)}")
                    # Fallback to pandas to_datetime with flexible parsing
                    result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
            
            # Format dates to target format
            try:
                result_df[column] = result_df[column].apply(
                    lambda x: format_date(x, target_format) if pd.notna(x) else None
                )
            except Exception as e:
                logger.warning(f"Error formatting dates in column '{column}': {str(e)}")
                # In case of error, leave as pandas datetime
        
        logger.info(f"Standardized date format for columns: {date_columns}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error standardizing date format", exc_info=True)
        raise ValidationException(
            "Failed to standardize date format", 
            details={"error": str(e), "columns": date_columns}
        )


def validate_freight_data(df: pd.DataFrame, required_fields: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Validates freight data in a DataFrame against business rules.
    
    Args:
        df: DataFrame containing freight data
        required_fields: Optional list of required fields (default: REQUIRED_FREIGHT_FIELDS)
        
    Returns:
        Validated DataFrame with data quality flags
        
    Raises:
        ValidationException: If DataFrame is invalid or validation fails
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Set default required fields if not provided
    required_fields = required_fields or REQUIRED_FREIGHT_FIELDS
    
    # Validate CSV structure
    validate_csv_structure(df, required_fields)
    
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Add data quality flag column initialized to 'VALID'
        result_df['data_quality_flag'] = 'VALID'
        
        # Validate record_date is not in the future
        if 'record_date' in result_df.columns:
            result_df['record_date'] = pd.to_datetime(result_df['record_date'], errors='coerce')
            future_dates = result_df['record_date'] > pd.Timestamp.now()
            if future_dates.any():
                result_df.loc[future_dates, 'data_quality_flag'] = 'INVALID'
                logger.warning(f"Found {future_dates.sum()} records with future dates")
        
        # Validate freight_charge is a positive number
        if 'freight_charge' in result_df.columns:
            # Convert to numeric, force errors to NaN
            result_df['freight_charge'] = pd.to_numeric(result_df['freight_charge'], errors='coerce')
            
            # Find invalid or negative values
            invalid_charges = result_df['freight_charge'].isna() | (result_df['freight_charge'] <= 0)
            if invalid_charges.any():
                result_df.loc[invalid_charges, 'data_quality_flag'] = 'INVALID'
                logger.warning(f"Found {invalid_charges.sum()} records with invalid freight charges")
        
        # Validate currency_code
        if 'currency_code' in result_df.columns:
            # Apply currency code validation
            invalid_currency = []
            for idx, code in result_df['currency_code'].items():
                if pd.isna(code):
                    invalid_currency.append(idx)
                    continue
                
                try:
                    if not is_valid_currency_code(str(code)):
                        invalid_currency.append(idx)
                except Exception:
                    invalid_currency.append(idx)
            
            if invalid_currency:
                result_df.loc[invalid_currency, 'data_quality_flag'] = 'INVALID'
                logger.warning(f"Found {len(invalid_currency)} records with invalid currency codes")
        
        # Validate transport_mode
        if 'transport_mode' in result_df.columns:
            # Apply transport mode validation
            invalid_modes = []
            for idx, mode in result_df['transport_mode'].items():
                if pd.isna(mode):
                    invalid_modes.append(idx)
                    continue
                
                try:
                    validate_transport_mode(str(mode))
                except Exception:
                    invalid_modes.append(idx)
            
            if invalid_modes:
                result_df.loc[invalid_modes, 'data_quality_flag'] = 'INVALID'
                logger.warning(f"Found {len(invalid_modes)} records with invalid transport modes")
        
        # Count validation results
        valid_count = (result_df['data_quality_flag'] == 'VALID').sum()
        warning_count = (result_df['data_quality_flag'] == 'WARNING').sum()
        invalid_count = (result_df['data_quality_flag'] == 'INVALID').sum()
        
        logger.info(
            f"Freight data validation complete: "
            f"{valid_count} valid, {warning_count} warnings, {invalid_count} invalid"
        )
        
        return result_df
        
    except Exception as e:
        logger.error(f"Error validating freight data", exc_info=True)
        raise ValidationException(
            "Failed to validate freight data", 
            details={"error": str(e)}
        )


def clean_freight_data(df: pd.DataFrame, remove_invalid: Optional[bool] = False) -> pd.DataFrame:
    """
    Cleans and standardizes freight data for analysis.
    
    Args:
        df: DataFrame containing freight data
        remove_invalid: Whether to remove records with INVALID quality flag (default: False)
        
    Returns:
        Cleaned and standardized DataFrame
        
    Raises:
        ValidationException: If DataFrame is invalid or cleaning fails
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Remove duplicate records
        original_count = len(result_df)
        result_df = result_df.drop_duplicates()
        duplicate_count = original_count - len(result_df)
        if duplicate_count > 0:
            logger.info(f"Removed {duplicate_count} duplicate records")
        
        # Handle missing values
        # For numeric columns, replace NaN with 0
        numeric_cols = result_df.select_dtypes(include=['number']).columns
        result_df[numeric_cols] = result_df[numeric_cols].fillna(0)
        
        # For string columns, replace NaN with empty string
        string_cols = result_df.select_dtypes(include=['object']).columns
        result_df[string_cols] = result_df[string_cols].fillna('')
        
        # Convert data types
        if 'freight_charge' in result_df.columns:
            result_df['freight_charge'] = pd.to_numeric(result_df['freight_charge'], errors='coerce')
        
        if 'record_date' in result_df.columns and result_df['record_date'].dtype != 'datetime64[ns]':
            result_df['record_date'] = pd.to_datetime(result_df['record_date'], errors='coerce')
        
        # Remove invalid records if requested
        if remove_invalid and 'data_quality_flag' in result_df.columns:
            invalid_count = (result_df['data_quality_flag'] == 'INVALID').sum()
            if invalid_count > 0:
                result_df = result_df[result_df['data_quality_flag'] != 'INVALID']
                logger.info(f"Removed {invalid_count} invalid records")
        
        # Log cleaning statistics
        logger.info(
            f"Data cleaning complete: "
            f"{duplicate_count} duplicates removed, "
            f"final record count: {len(result_df)}"
        )
        
        return result_df
        
    except Exception as e:
        logger.error(f"Error cleaning freight data", exc_info=True)
        raise ValidationException(
            "Failed to clean freight data", 
            details={"error": str(e)}
        )


def detect_csv_dialect(file_path: str, sample_size: Optional[int] = None) -> dict:
    """
    Detects the dialect (delimiter, quoting, etc.) of a CSV file.
    
    Args:
        file_path: Path to the CSV file
        sample_size: Number of bytes to sample from the beginning of the file
        
    Returns:
        Dictionary with detected CSV dialect parameters
        
    Raises:
        ValidationException: If the file does not exist or dialect detection fails
    """
    # Validate file_path
    if file_path is None or not file_path.strip():
        raise ValidationException("File path is required")
    
    if not os.path.exists(file_path):
        raise ValidationException(f"File does not exist: {file_path}")
    
    # Default sample size if not provided
    sample_size = sample_size or 1000
    
    try:
        # Read a sample of the file
        with open(file_path, 'r', newline='') as f:
            sample = f.read(sample_size)
        
        # Use csv.Sniffer to detect the dialect
        import csv
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        has_header = sniffer.has_header(sample)
        
        # Extract dialect parameters
        dialect_params = {
            'delimiter': dialect.delimiter,
            'quotechar': dialect.quotechar,
            'escapechar': dialect.escapechar,
            'has_header': has_header
        }
        
        logger.info(
            f"Detected CSV dialect: delimiter='{dialect.delimiter}', "
            f"quotechar='{dialect.quotechar}', has_header={has_header}"
        )
        
        return dialect_params
        
    except csv.Error as e:
        logger.warning(f"Failed to detect CSV dialect: {str(e)}")
        # Default to standard CSV parameters
        default_params = {
            'delimiter': DEFAULT_DELIMITER,
            'quotechar': '"',
            'escapechar': None,
            'has_header': True
        }
        logger.info(f"Using default CSV parameters: {default_params}")
        return default_params
        
    except Exception as e:
        logger.error(f"Error detecting CSV dialect", exc_info=True)
        raise ValidationException(
            "Failed to detect CSV dialect", 
            details={"error": str(e)}
        )


def infer_column_types(df: pd.DataFrame) -> dict:
    """
    Infers the data types of columns in a DataFrame.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary mapping column names to inferred types
        
    Raises:
        ValidationException: If DataFrame is invalid
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    try:
        column_types = {}
        
        # Analyze each column
        for column in df.columns:
            # Skip completely empty columns
            if df[column].isna().all():
                column_types[column] = 'string'
                continue
            
            # Get a sample of non-null values
            sample = df[column].dropna().head(100)
            
            # Empty column after dropping NAs
            if len(sample) == 0:
                column_types[column] = 'string'
                continue
            
            # Try to infer type based on pandas dtype
            dtype = df[column].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                # Check if integer or float
                if pd.api.types.is_integer_dtype(dtype) or all(float(x).is_integer() for x in sample if pd.notna(x)):
                    column_types[column] = 'integer'
                else:
                    column_types[column] = 'float'
            elif pd.api.types.is_datetime64_dtype(dtype):
                column_types[column] = 'date'
            else:
                # For object dtypes, try to determine if it's a date
                try:
                    pd.to_datetime(sample, errors='raise')
                    column_types[column] = 'date'
                except:
                    # Check if boolean-like
                    if all(str(x).lower() in ('true', 'false', '0', '1', 'yes', 'no', 'y', 'n') for x in sample):
                        column_types[column] = 'boolean'
                    else:
                        column_types[column] = 'string'
        
        logger.info(f"Inferred column types: {column_types}")
        return column_types
        
    except Exception as e:
        logger.error(f"Error inferring column types", exc_info=True)
        raise ValidationException(
            "Failed to infer column types", 
            details={"error": str(e)}
        )


def convert_column_types(df: pd.DataFrame, type_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Converts DataFrame columns to specified data types.
    
    Args:
        df: DataFrame to convert
        type_mapping: Dictionary mapping column names to desired types
        
    Returns:
        DataFrame with converted column types
        
    Raises:
        ValidationException: If DataFrame is invalid or conversion fails
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Validate that type_mapping is a dictionary
    if type_mapping is None or not isinstance(type_mapping, dict):
        raise ValidationException("Type mapping must be a dictionary")
    
    try:
        # Create a copy of the DataFrame to avoid modifying the original
        result_df = df.copy()
        
        # Convert each column according to the mapping
        for column, target_type in type_mapping.items():
            # Skip columns that don't exist in the DataFrame
            if column not in result_df.columns:
                logger.warning(f"Column '{column}' not found in DataFrame, skipping type conversion")
                continue
            
            # Convert based on target type
            if target_type == 'integer':
                result_df[column] = pd.to_numeric(result_df[column], errors='coerce').astype('Int64')
            elif target_type == 'float':
                result_df[column] = pd.to_numeric(result_df[column], errors='coerce')
            elif target_type == 'boolean':
                # Handle various boolean representations
                result_df[column] = result_df[column].map({
                    'true': True, 'True': True, '1': True, 1: True, 'yes': True, 'Yes': True, 'Y': True, 'y': True,
                    'false': False, 'False': False, '0': False, 0: False, 'no': False, 'No': False, 'N': False, 'n': False
                })
            elif target_type == 'date':
                result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
            elif target_type == 'string':
                result_df[column] = result_df[column].astype(str)
            else:
                logger.warning(f"Unknown target type '{target_type}' for column '{column}', leaving as-is")
        
        logger.info(f"Converted column types according to mapping")
        return result_df
        
    except Exception as e:
        logger.error(f"Error converting column types", exc_info=True)
        raise ValidationException(
            "Failed to convert column types", 
            details={"error": str(e)}
        )


def export_to_csv(df: pd.DataFrame, 
                 file_path: str, 
                 delimiter: Optional[str] = None, 
                 encoding: Optional[str] = None, 
                 include_header: Optional[bool] = None) -> bool:
    """
    Exports a DataFrame to a CSV file.
    
    Args:
        df: DataFrame to export
        file_path: Path to the output CSV file
        delimiter: Column delimiter (default: DEFAULT_DELIMITER)
        encoding: File encoding (default: DEFAULT_ENCODING)
        include_header: Whether to include a header row (default: True)
        
    Returns:
        True if export successful, False otherwise
    """
    # Validate that df is a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValidationException("Invalid DataFrame: None or not a pandas DataFrame")
    
    # Validate file_path
    if file_path is None or not file_path.strip():
        raise ValidationException("File path is required")
    
    # Set default values if not provided
    delimiter = delimiter or DEFAULT_DELIMITER
    encoding = encoding or DEFAULT_ENCODING
    include_header = True if include_header is None else include_header
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Export DataFrame to CSV
        df.to_csv(
            file_path,
            sep=delimiter,
            encoding=encoding,
            index=False,
            header=include_header
        )
        
        logger.info(f"Successfully exported {len(df)} rows to CSV file: {file_path}")
        return True
        
    except PermissionError as e:
        logger.error(f"Permission denied when writing to file: {file_path}")
        raise ValidationException(
            f"Permission denied when writing to file: {file_path}", 
            details={"error": str(e)}
        )
    except Exception as e:
        logger.error(f"Error exporting to CSV file: {file_path}", exc_info=True)
        raise ValidationException(
            f"Failed to export to CSV file: {file_path}", 
            details={"error": str(e)}
        )


class CSVValidator:
    """
    Class that provides comprehensive CSV validation capabilities.
    
    This validator checks that CSV data conforms to expected structure
    and business rules for freight data.
    """
    
    def __init__(self, required_fields: Optional[List[str]] = None):
        """
        Initializes a new CSVValidator instance.
        
        Args:
            required_fields: List of required fields (default: REQUIRED_FREIGHT_FIELDS)
        """
        self._validation_errors = {}
        self._required_fields = required_fields or REQUIRED_FREIGHT_FIELDS
    
    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validates a DataFrame against freight data requirements.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False if validation errors exist
        """
        # Clear previous validation errors
        self._validation_errors = {}
        
        # Validate basic structure
        try:
            validate_csv_structure(df, self._required_fields)
        except ValidationException as e:
            self.add_error('structure', str(e))
            return False
        
        # Validate each required field
        for field in self._required_fields:
            self.validate_field(df, field)
        
        # Return True if no errors, False otherwise
        return not self.has_errors()
    
    def add_error(self, field: str, message: str) -> None:
        """
        Adds a validation error to the errors collection.
        
        Args:
            field: Field name where the error occurred
            message: Error message
        """
        if field not in self._validation_errors:
            self._validation_errors[field] = []
        
        self._validation_errors[field].append(message)
    
    def get_errors(self) -> dict:
        """
        Returns all validation errors.
        
        Returns:
            Dictionary of validation errors by field
        """
        return self._validation_errors.copy()
    
    def has_errors(self) -> bool:
        """
        Checks if there are any validation errors.
        
        Returns:
            True if there are errors, False otherwise
        """
        return len(self._validation_errors) > 0
    
    def validate_field(self, df: pd.DataFrame, field_name: str) -> bool:
        """
        Validates a single field in the DataFrame.
        
        Args:
            df: DataFrame containing the field
            field_name: Name of the field to validate
            
        Returns:
            True if field is valid, False otherwise
        """
        # Check if field exists in DataFrame
        if field_name not in df.columns:
            self.add_error(field_name, f"Field '{field_name}' is missing from the data")
            return False
        
        # Get field values
        values = df[field_name]
        
        # Check for null values
        null_count = values.isna().sum()
        if null_count > 0:
            self.add_error(field_name, f"Field '{field_name}' has {null_count} null values")
        
        # Field-specific validation
        if field_name == 'record_date':
            # Convert to datetime and check for future dates
            dates = pd.to_datetime(values, errors='coerce')
            
            # Count null dates after conversion
            invalid_date_count = dates.isna().sum()
            if invalid_date_count > 0:
                self.add_error(field_name, f"Field '{field_name}' has {invalid_date_count} invalid date values")
            
            # Check for future dates
            future_dates = dates > pd.Timestamp.now()
            future_date_count = future_dates.sum()
            if future_date_count > 0:
                self.add_error(field_name, f"Field '{field_name}' has {future_date_count} future dates")
        
        elif field_name == 'freight_charge':
            # Convert to numeric and check for positive values
            charges = pd.to_numeric(values, errors='coerce')
            
            # Count null charges after conversion
            invalid_charge_count = charges.isna().sum()
            if invalid_charge_count > 0:
                self.add_error(field_name, f"Field '{field_name}' has {invalid_charge_count} non-numeric values")
            
            # Check for non-positive values
            non_positive_count = (charges <= 0).sum()
            if non_positive_count > 0:
                self.add_error(field_name, f"Field '{field_name}' has {non_positive_count} non-positive values")
        
        elif field_name == 'currency_code':
            # Check currency code validity
            invalid_currency_codes = []
            for code in values.dropna().unique():
                try:
                    if not is_valid_currency_code(str(code)):
                        invalid_currency_codes.append(code)
                except Exception:
                    invalid_currency_codes.append(code)
            
            if invalid_currency_codes:
                self.add_error(
                    field_name, 
                    f"Field '{field_name}' has invalid currency codes: {', '.join(map(str, invalid_currency_codes))}"
                )
        
        elif field_name == 'transport_mode':
            # Check transport mode validity
            invalid_modes = []
            for mode in values.dropna().unique():
                try:
                    validate_transport_mode(str(mode))
                except Exception:
                    invalid_modes.append(mode)
            
            if invalid_modes:
                self.add_error(
                    field_name, 
                    f"Field '{field_name}' has invalid transport modes: {', '.join(map(str, invalid_modes))}"
                )
        
        # Return True if no errors were added for this field
        return field_name not in self._validation_errors


class CSVProcessor:
    """
    Class that handles end-to-end CSV processing for freight data.
    
    This processor manages the complete workflow of loading, validating, 
    transforming, and exporting freight data from CSV files.
    """
    
    def __init__(self, column_mapping: Optional[dict] = None, required_fields: Optional[List[str]] = None):
        """
        Initializes a new CSVProcessor instance.
        
        Args:
            column_mapping: Dictionary mapping source columns to standardized names
            required_fields: List of required fields (default: REQUIRED_FREIGHT_FIELDS)
        """
        self._data = None
        self._column_mapping = column_mapping or {}
        self._validator = CSVValidator(required_fields)
    
    def load_file(self, file_path: str, csv_options: Optional[dict] = None) -> bool:
        """
        Loads a CSV file into the processor.
        
        Args:
            file_path: Path to the CSV file
            csv_options: Dictionary of options for CSV reading
            
        Returns:
            True if file loaded successfully, False otherwise
        """
        try:
            # Set default options if not provided
            if csv_options is None:
                # Detect CSV dialect
                dialect = detect_csv_dialect(file_path)
                csv_options = {
                    'delimiter': dialect['delimiter'],
                    'encoding': DEFAULT_ENCODING,
                    'has_header': dialect['has_header']
                }
            
            # Read the CSV file
            self._data = read_csv_file(
                file_path,
                delimiter=csv_options.get('delimiter', DEFAULT_DELIMITER),
                encoding=csv_options.get('encoding', DEFAULT_ENCODING),
                has_header=csv_options.get('has_header', True),
                usecols=csv_options.get('usecols')
            )
            
            logger.info(f"Loaded CSV file with {len(self._data)} rows and {len(self._data.columns)} columns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSV file: {file_path}", exc_info=True)
            return False
    
    def process(self) -> pd.DataFrame:
        """
        Processes the loaded CSV data with validation and transformation.
        
        Returns:
            Processed DataFrame
            
        Raises:
            ValidationException: If data is not loaded or processing fails
        """
        if self._data is None:
            raise ValidationException("No data loaded. Call load_file() first.")
        
        try:
            # Apply column mapping if provided
            if self._column_mapping:
                self._data = map_columns(self._data, self._column_mapping)
            
            # Standardize date columns
            date_columns = [col for col in self._data.columns if 'date' in col.lower()]
            if date_columns:
                self._data = standardize_date_format(self._data, date_columns)
            
            # Validate the data
            validation_result = self._validator.validate(self._data)
            if not validation_result:
                logger.warning(
                    f"Data validation found errors: {self._validator.get_errors()}"
                )
            
            # Clean the data
            self._data = clean_freight_data(self._data)
            
            logger.info("CSV processing completed successfully")
            return self._data
            
        except Exception as e:
            logger.error("CSV processing failed", exc_info=True)
            raise ValidationException(
                "Failed to process CSV data", 
                details={"error": str(e)}
            )
    
    def set_column_mapping(self, column_mapping: dict) -> None:
        """
        Sets the column mapping for CSV processing.
        
        Args:
            column_mapping: Dictionary mapping source columns to standardized names
        """
        if not isinstance(column_mapping, dict):
            raise ValidationException("Column mapping must be a dictionary")
        
        self._column_mapping = column_mapping
        logger.debug(f"Set column mapping: {column_mapping}")
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Returns the current DataFrame.
        
        Returns:
            Current DataFrame or None if not loaded
        """
        if self._data is None:
            return None
        
        return self._data.copy()
    
    def export(self, file_path: str, csv_options: Optional[dict] = None) -> bool:
        """
        Exports the processed data to a CSV file.
        
        Args:
            file_path: Path to the output CSV file
            csv_options: Dictionary of options for CSV export
            
        Returns:
            True if export successful, False otherwise
        """
        if self._data is None:
            logger.error("Cannot export: No data loaded")
            return False
        
        try:
            # Set default options if not provided
            if csv_options is None:
                csv_options = {
                    'delimiter': DEFAULT_DELIMITER,
                    'encoding': DEFAULT_ENCODING,
                    'include_header': True
                }
            
            # Export to CSV
            return export_to_csv(
                self._data,
                file_path,
                delimiter=csv_options.get('delimiter', DEFAULT_DELIMITER),
                encoding=csv_options.get('encoding', DEFAULT_ENCODING),
                include_header=csv_options.get('include_header', True)
            )
            
        except Exception as e:
            logger.error(f"Failed to export CSV data: {file_path}", exc_info=True)
            return False
    
    def get_validation_errors(self) -> dict:
        """
        Returns validation errors from the validator.
        
        Returns:
            Dictionary of validation errors by field
        """
        return self._validator.get_errors()
    
    def get_statistics(self) -> dict:
        """
        Returns statistics about the processed data.
        
        Returns:
            Dictionary with data statistics
        """
        if self._data is None:
            return {}
        
        try:
            # Calculate basic statistics
            stats = {
                'row_count': len(self._data),
                'column_count': len(self._data.columns),
                'columns': list(self._data.columns)
            }
            
            # Add data quality statistics if available
            if 'data_quality_flag' in self._data.columns:
                quality_counts = self._data['data_quality_flag'].value_counts().to_dict()
                stats['quality'] = {
                    'valid': quality_counts.get('VALID', 0),
                    'warning': quality_counts.get('WARNING', 0),
                    'invalid': quality_counts.get('INVALID', 0)
                }
            
            # Add date range if record_date is available
            if 'record_date' in self._data.columns:
                dates = pd.to_datetime(self._data['record_date'], errors='coerce')
                min_date = dates.min()
                max_date = dates.max()
                
                if pd.notna(min_date) and pd.notna(max_date):
                    stats['date_range'] = {
                        'min_date': min_date.strftime('%Y-%m-%d'),
                        'max_date': max_date.strftime('%Y-%m-%d')
                    }
            
            return stats
            
        except Exception as e:
            logger.error("Error calculating data statistics", exc_info=True)
            return {'error': str(e)}