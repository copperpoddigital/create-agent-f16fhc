#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the CSV parser utility that handles reading, validating, and
transforming freight pricing data from CSV files.
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import datetime
from datetime import datetime as dt

# Internal imports
from ...utils.csv_parser import (
    read_csv_file, validate_freight_data, map_columns, standardize_date_format,
    process_csv_file, REQUIRED_FREIGHT_FIELDS as REQUIRED_COLUMNS, DEFAULT_DATE_FORMAT
)
from ...core.exceptions import (
    FileReadError, DataValidationError
)

# Sample CSV contents for testing
SAMPLE_CSV_CONTENT = """origin,destination,price,currency,quote_date
Shanghai,Rotterdam,4500,USD,2023-01-15
Los Angeles,New York,2300,USD,2023-01-16
Hamburg,Singapore,3800,EUR,2023-01-17"""

INVALID_CSV_CONTENT = """origin,destination,invalid_price,currency,quote_date
Shanghai,Rotterdam,not_a_number,USD,2023-01-15"""

MISSING_COLUMNS_CSV_CONTENT = """origin,destination,currency
Shanghai,Rotterdam,USD"""

# Column mapping for standardized names
COLUMN_MAPPING = {
    "origin": "origin", 
    "destination": "destination", 
    "price": "freight_charge", 
    "currency": "currency_code", 
    "quote_date": "record_date"
}

def create_temp_csv_file(content: str) -> str:
    """
    Creates a temporary CSV file with the given content for testing.
    
    Args:
        content: String content to write to the CSV file
        
    Returns:
        Path to the created temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    with open(temp_file.name, "w") as f:
        f.write(content)
    return temp_file.name

def test_read_csv_file_success():
    """Tests that read_csv_file successfully reads a valid CSV file."""
    # Create a temporary CSV file
    temp_file_path = create_temp_csv_file(SAMPLE_CSV_CONTENT)
    
    try:
        # Call the function under test
        df = read_csv_file(temp_file_path)
        
        # Assert the DataFrame has the expected shape and columns
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 3  # 3 rows
        assert df.shape[1] == 5  # 5 columns
        assert list(df.columns) == ["origin", "destination", "price", "currency", "quote_date"]
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_read_csv_file_nonexistent():
    """Tests that read_csv_file raises FileReadError for a nonexistent file."""
    with pytest.raises(FileReadError) as excinfo:
        read_csv_file("nonexistent_file.csv")
    
    # Check that the error message contains appropriate information
    assert "File does not exist" in str(excinfo.value)
    assert "nonexistent_file.csv" in str(excinfo.value)

def test_read_csv_file_invalid_extension():
    """Tests that read_csv_file raises FileReadError for a file with invalid extension."""
    # Create a temporary file with non-CSV extension
    temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    temp_file_path = temp_file.name
    
    try:
        with pytest.raises(FileReadError) as excinfo:
            read_csv_file(temp_file_path)
        
        # Check that the error message mentions invalid file extension
        assert "invalid file extension" in str(excinfo.value).lower() or "file format" in str(excinfo.value).lower()
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_validate_freight_data_success():
    """Tests that validate_freight_data successfully validates correct data."""
    # Create test data
    data = pd.DataFrame({
        "origin": ["Shanghai", "Los Angeles"],
        "destination": ["Rotterdam", "New York"],
        "freight_charge": [4500, 2300],
        "currency_code": ["USD", "USD"],
        "record_date": [dt(2023, 1, 15), dt(2023, 1, 16)],
        "transport_mode": ["OCEAN", "ROAD"]
    })
    
    # Call the function under test
    result = validate_freight_data(data)
    
    # Assert the function returns true for valid data
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert "data_quality_flag" in result.columns
    assert (result["data_quality_flag"] == "VALID").all()

def test_validate_freight_data_empty():
    """Tests that validate_freight_data raises DataValidationError for empty data."""
    # Create empty DataFrame
    empty_df = pd.DataFrame()
    
    with pytest.raises(DataValidationError) as excinfo:
        validate_freight_data(empty_df)
    
    # Check that the error message mentions empty data
    assert "empty" in str(excinfo.value).lower() or "invalid dataframe" in str(excinfo.value).lower()

def test_validate_freight_data_missing_columns():
    """Tests that validate_freight_data raises DataValidationError for data with missing required columns."""
    # Create test data with missing required columns
    data = pd.DataFrame({
        "origin": ["Shanghai", "Los Angeles"],
        "destination": ["Rotterdam", "New York"],
        # Missing freight_charge, currency_code, etc.
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        validate_freight_data(data)
    
    # Check that the error message mentions missing columns
    assert "missing" in str(excinfo.value).lower() or "required columns" in str(excinfo.value).lower()

def test_validate_freight_data_invalid_numeric():
    """Tests that validate_freight_data raises DataValidationError for non-numeric freight charges."""
    # Create test data with non-numeric freight charges
    data = pd.DataFrame({
        "origin": ["Shanghai"],
        "destination": ["Rotterdam"],
        "freight_charge": ["not_a_number"],
        "currency_code": ["USD"],
        "record_date": [dt(2023, 1, 15)],
        "transport_mode": ["OCEAN"]
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        validate_freight_data(data)
    
    # Check that the error message mentions invalid numeric values
    assert "numeric" in str(excinfo.value).lower() or "invalid freight charge" in str(excinfo.value).lower()

def test_validate_freight_data_negative_charges():
    """Tests that validate_freight_data raises DataValidationError for negative freight charges."""
    # Create test data with negative freight charges
    data = pd.DataFrame({
        "origin": ["Shanghai"],
        "destination": ["Rotterdam"],
        "freight_charge": [-100],
        "currency_code": ["USD"],
        "record_date": [dt(2023, 1, 15)],
        "transport_mode": ["OCEAN"]
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        validate_freight_data(data)
    
    # Check that the error message mentions negative values
    assert "negative" in str(excinfo.value).lower() or "positive" in str(excinfo.value).lower()

def test_validate_freight_data_invalid_dates():
    """Tests that validate_freight_data raises DataValidationError for invalid dates."""
    # Create test data with invalid dates
    data = pd.DataFrame({
        "origin": ["Shanghai"],
        "destination": ["Rotterdam"],
        "freight_charge": [4500],
        "currency_code": ["USD"],
        "record_date": ["invalid_date"],
        "transport_mode": ["OCEAN"]
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        validate_freight_data(data)
    
    # Check that the error message mentions invalid date values
    assert "date" in str(excinfo.value).lower() or "invalid" in str(excinfo.value).lower()

def test_map_columns_success():
    """Tests that map_columns successfully maps columns according to the mapping."""
    # Create test data with source column names
    data = pd.DataFrame({
        "origin": ["Shanghai", "Los Angeles"],
        "destination": ["Rotterdam", "New York"],
        "price": [4500, 2300],
        "currency": ["USD", "USD"],
        "quote_date": ["2023-01-15", "2023-01-16"]
    })
    
    # Call the function under test
    result = map_columns(data, COLUMN_MAPPING)
    
    # Assert that column names are correctly mapped
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert "freight_charge" in result.columns
    assert "currency_code" in result.columns
    assert "record_date" in result.columns
    assert list(result.columns) == ["origin", "destination", "freight_charge", "currency_code", "record_date"]

def test_map_columns_missing_mapping():
    """Tests that map_columns raises DataValidationError when mapping is missing required columns."""
    # Create test data with source column names
    data = pd.DataFrame({
        "origin": ["Shanghai", "Los Angeles"],
        "destination": ["Rotterdam", "New York"],
        "price": [4500, 2300],
        "currency": ["USD", "USD"],
        "quote_date": ["2023-01-15", "2023-01-16"]
    })
    
    # Define incomplete column mapping missing required columns
    incomplete_mapping = {
        "origin": "origin",
        "destination": "destination"
        # Missing price, currency, quote_date mappings
    }
    
    with pytest.raises(DataValidationError) as excinfo:
        map_columns(data, incomplete_mapping)
    
    # Check that the error message mentions missing required columns in mapping
    assert "missing" in str(excinfo.value).lower() or "required" in str(excinfo.value).lower()

def test_standardize_date_format_success():
    """Tests that standardize_date_format successfully converts dates to standard format."""
    # Create test data with dates in various formats
    data = pd.DataFrame({
        "date1": ["2023-01-15", "2023/01/16", "Jan 17, 2023"],
        "date2": ["15-01-2023", "16/01/2023", "17-Jan-2023"]
    })
    
    # Call the function under test for date1 column
    result = standardize_date_format(data, "date1")
    
    # Assert that dates are standardized
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    
    # Check that all dates are standardized properly
    expected_dates = ["2023-01-15", "2023-01-16", "2023-01-17"]
    for i, date_str in enumerate(result["date1"]):
        assert date_str == expected_dates[i]

def test_standardize_date_format_invalid_column():
    """Tests that standardize_date_format raises DataValidationError for invalid date column."""
    # Create test data without the specified date column
    data = pd.DataFrame({
        "other_column": ["value1", "value2"]
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        standardize_date_format(data, "non_existent_column")
    
    # Check that the error message mentions the missing column
    assert "column" in str(excinfo.value).lower() and "non_existent_column" in str(excinfo.value)

def test_standardize_date_format_invalid_dates():
    """Tests that standardize_date_format raises DataValidationError for invalid date values."""
    # Create test data with invalid date values
    data = pd.DataFrame({
        "date_column": ["not_a_date", "also_not_a_date"]
    })
    
    with pytest.raises(DataValidationError) as excinfo:
        standardize_date_format(data, "date_column")
    
    # Check that the error message mentions invalid date format
    assert "date" in str(excinfo.value).lower() or "invalid" in str(excinfo.value).lower()

def test_process_csv_file_success():
    """Tests that process_csv_file successfully processes a valid CSV file."""
    # Create a temporary CSV file
    temp_file_path = create_temp_csv_file(SAMPLE_CSV_CONTENT)
    
    try:
        # Call the function under test
        result = process_csv_file(temp_file_path, COLUMN_MAPPING)
        
        # Assert that the result is as expected
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert "freight_charge" in result.columns
        assert "currency_code" in result.columns
        assert "record_date" in result.columns
        
        # Check specific values
        assert result.iloc[0]["freight_charge"] == 4500
        assert result.iloc[0]["currency_code"] == "USD"
        assert result.iloc[0]["origin"] == "Shanghai"
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

def test_process_csv_file_invalid_data():
    """Tests that process_csv_file raises appropriate exceptions for invalid data."""
    # Create a temporary CSV file with invalid content
    temp_file_path = create_temp_csv_file(INVALID_CSV_CONTENT)
    
    try:
        with pytest.raises(DataValidationError) as excinfo:
            process_csv_file(temp_file_path, COLUMN_MAPPING)
        
        # Check that the error message contains appropriate information
        assert "invalid" in str(excinfo.value).lower() or "validation" in str(excinfo.value).lower()
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)