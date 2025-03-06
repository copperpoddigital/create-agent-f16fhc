#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File connector module for the Freight Price Movement Agent.

This module provides connector classes for reading, parsing, and validating
freight pricing data from CSV files and other supported file formats. It implements
the functionality required for F-001-RQ-001 (CSV File Import) and serves as part
of the Data Collection & Ingestion feature.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List, Any, Union

import pandas as pd  # version 1.5.x

from ..core.logging import get_logger
from ..core.exceptions import DataSourceException, ValidationException
from ..utils.csv_parser import (
    read_csv_file,
    validate_freight_data,
    map_columns,
    standardize_date_format,
)

# Initialize logger
logger = get_logger(__name__)

# Define supported file types
SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls']


class FileConnector:
    """
    Connector class for file-based data sources that handles reading and processing various file formats.
    
    This base class provides common functionality for validating, reading, and processing
    files containing freight price data.
    """
    
    def __init__(self, file_path: str, config: Optional[Dict] = None):
        """
        Initialize the FileConnector with file path and configuration.
        
        Args:
            file_path: Path to the file containing freight data
            config: Optional configuration dictionary with processing parameters
            
        Raises:
            DataSourceException: If file_path is not provided
        """
        if not file_path:
            raise DataSourceException("File path is required")
        
        self.file_path = file_path
        self.config = config or {}
        
        logger.info(f"Initialized FileConnector for {file_path}")
    
    def validate_file(self) -> bool:
        """
        Validates that the file exists and has a supported format.
        
        Returns:
            True if file is valid
            
        Raises:
            DataSourceException: If file doesn't exist or has unsupported format
        """
        # Check if file exists
        if not os.path.exists(self.file_path):
            raise DataSourceException(
                f"File does not exist: {self.file_path}",
                details={"file_path": self.file_path}
            )
        
        # Check file extension
        extension = self.get_file_extension()
        if extension not in SUPPORTED_FILE_TYPES:
            raise DataSourceException(
                f"Unsupported file type: {extension}. Supported types: {', '.join(SUPPORTED_FILE_TYPES)}",
                details={"file_path": self.file_path, "extension": extension}
            )
        
        logger.debug(f"File validation successful: {self.file_path}")
        return True
    
    def read_file(self) -> pd.DataFrame:
        """
        Reads the file and returns its contents as a pandas DataFrame.
        
        Returns:
            DataFrame containing the file data
            
        Raises:
            DataSourceException: If file reading fails
        """
        try:
            # Validate the file first
            self.validate_file()
            
            # Determine the file type from extension
            extension = self.get_file_extension()
            
            if extension == 'csv':
                # Use CSV parser for CSV files
                df = read_csv_file(
                    self.file_path,
                    delimiter=self.config.get('delimiter'),
                    encoding=self.config.get('encoding'),
                    has_header=self.config.get('has_header', True)
                )
            elif extension in ['xlsx', 'xls']:
                # Use pandas for Excel files
                df = pd.read_excel(
                    self.file_path,
                    sheet_name=self.config.get('sheet_name', 0),
                    header=0 if self.config.get('has_header', True) else None
                )
            else:
                # This shouldn't happen due to validate_file, but just in case
                raise DataSourceException(f"Unsupported file type: {extension}")
            
            logger.info(f"Successfully read file {self.file_path} with {len(df)} rows")
            return df
            
        except ValidationException as e:
            # Re-raise validation errors as data source exceptions
            raise DataSourceException(
                f"File validation error: {str(e)}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )
        except Exception as e:
            logger.error(f"Error reading file: {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to read file: {self.file_path}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )
    
    def fetch_freight_data(self, column_mapping: Optional[Dict] = None, date_format: Optional[str] = None) -> pd.DataFrame:
        """
        Fetches freight data from the file, applying validation and transformation.
        
        Args:
            column_mapping: Optional mapping of source columns to standardized names
            date_format: Optional date format for standardizing date fields
            
        Returns:
            Processed and validated freight data as DataFrame
            
        Raises:
            DataSourceException: If data processing fails
        """
        try:
            # Read the file
            df = self.read_file()
            
            # Apply column mapping if provided
            if column_mapping:
                df = map_columns(df, column_mapping)
            elif self.config.get('column_mapping'):
                df = map_columns(df, self.config['column_mapping'])
            
            # Standardize date format if provided
            date_column = self.config.get('date_column', 'record_date')
            format_to_use = date_format or self.config.get('date_format')
            
            if date_column in df.columns and format_to_use:
                df = standardize_date_format(df, date_column, format_to_use)
            
            # Validate the freight data
            df = validate_freight_data(df)
            
            # Log successful processing
            valid_count = (df['data_quality_flag'] == 'VALID').sum() if 'data_quality_flag' in df.columns else len(df)
            logger.info(f"Successfully processed {len(df)} records, {valid_count} valid")
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing freight data from {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to process freight data from file: {self.file_path}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )
    
    def get_file_extension(self) -> str:
        """
        Extracts the file extension from the file path.
        
        Returns:
            File extension (lowercase, without the dot)
        """
        # Use pathlib for reliable extension extraction
        extension = Path(self.file_path).suffix.lower()
        
        # Remove the leading dot
        if extension.startswith('.'):
            extension = extension[1:]
            
        return extension
    
    def get_file_info(self) -> Dict:
        """
        Returns metadata about the file.
        
        Returns:
            Dictionary with file metadata including size, modification time, etc.
            
        Raises:
            DataSourceException: If file doesn't exist or metadata retrieval fails
        """
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                raise DataSourceException(f"File does not exist: {self.file_path}")
            
            # Get file stats
            file_stats = os.stat(self.file_path)
            file_path = Path(self.file_path)
            
            # Compile file info
            info = {
                'file_name': file_path.name,
                'extension': self.get_file_extension(),
                'size_bytes': file_stats.st_size,
                'size_human': self._format_file_size(file_stats.st_size),
                'modified_time': file_stats.st_mtime,
                'modified_time_human': self._format_timestamp(file_stats.st_mtime),
                'absolute_path': str(file_path.absolute()),
                'is_valid': True
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info: {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to get file info: {self.file_path}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formats file size in a human-readable format.
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Human-readable file size (e.g., "2.5 MB")
        """
        # Define size units
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        # Convert to the appropriate unit
        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1
        
        # Format with up to 2 decimal places
        if unit_index == 0:
            # For bytes, use integer format
            return f"{int(size_bytes)} {units[unit_index]}"
        else:
            # For larger units, use decimal format
            return f"{size_bytes:.2f} {units[unit_index]}"
    
    def _format_timestamp(self, timestamp: float) -> str:
        """
        Formats a timestamp in a human-readable format.
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Human-readable datetime string
        """
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')


class CSVConnector(FileConnector):
    """
    Specialized connector for CSV files with additional CSV-specific functionality.
    
    This connector handles reading and processing CSV files with options for
    delimiters, encoding, and header configuration.
    """
    
    def __init__(self, file_path: str, config: Optional[Dict] = None):
        """
        Initialize the CSVConnector with file path and configuration.
        
        Args:
            file_path: Path to the CSV file
            config: Optional configuration dictionary with CSV processing parameters
        """
        # Call parent constructor
        super().__init__(file_path, config)
        
        # Set default CSV-specific options if not already specified
        if 'delimiter' not in self.config:
            self.config['delimiter'] = ','
        if 'encoding' not in self.config:
            self.config['encoding'] = 'utf-8'
        if 'has_header' not in self.config:
            self.config['has_header'] = True
        
        logger.info(f"Initialized CSVConnector for {file_path}")
    
    def read_file(self) -> pd.DataFrame:
        """
        Reads the CSV file with CSV-specific options.
        
        Returns:
            CSV file contents as a DataFrame
            
        Raises:
            DataSourceException: If file reading fails
        """
        try:
            # Validate the file first
            self.validate_file()
            
            # Extract CSV-specific options from config
            delimiter = self.config.get('delimiter', ',')
            encoding = self.config.get('encoding', 'utf-8')
            has_header = self.config.get('has_header', True)
            
            # Use CSV parser to read the file
            df = read_csv_file(
                self.file_path,
                delimiter=delimiter,
                encoding=encoding,
                has_header=has_header,
                usecols=self.config.get('usecols')
            )
            
            logger.info(f"Successfully read CSV file {self.file_path} with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to read CSV file: {self.file_path}",
                details={
                    "file_path": self.file_path,
                    "delimiter": self.config.get('delimiter'),
                    "encoding": self.config.get('encoding'),
                    "error": str(e)
                },
                original_exception=e
            )
    
    def preview_data(self, n_rows: int = 5) -> pd.DataFrame:
        """
        Returns a preview of the CSV data (first n rows).
        
        Args:
            n_rows: Number of rows to preview
            
        Returns:
            Preview of the CSV data
            
        Raises:
            DataSourceException: If preview generation fails
        """
        try:
            # Read the file
            df = self.read_file()
            
            # Return first n rows
            return df.head(n_rows)
            
        except Exception as e:
            logger.error(f"Error generating preview for {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to generate preview for file: {self.file_path}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )


class ExcelConnector(FileConnector):
    """
    Specialized connector for Excel files with additional Excel-specific functionality.
    
    This connector handles reading and processing Excel files with options for
    sheet selection and header configuration.
    """
    
    def __init__(self, file_path: str, config: Optional[Dict] = None):
        """
        Initialize the ExcelConnector with file path and configuration.
        
        Args:
            file_path: Path to the Excel file
            config: Optional configuration dictionary with Excel processing parameters
        """
        # Call parent constructor
        super().__init__(file_path, config)
        
        # Set default Excel-specific options if not already specified
        if 'sheet_name' not in self.config:
            self.config['sheet_name'] = 0  # First sheet by default
        if 'has_header' not in self.config:
            self.config['has_header'] = True
        
        logger.info(f"Initialized ExcelConnector for {file_path}")
    
    def read_file(self) -> pd.DataFrame:
        """
        Reads the Excel file with Excel-specific options.
        
        Returns:
            Excel file contents as a DataFrame
            
        Raises:
            DataSourceException: If file reading fails
        """
        try:
            # Validate the file first
            self.validate_file()
            
            # Extract Excel-specific options from config
            sheet_name = self.config.get('sheet_name', 0)
            header = 0 if self.config.get('has_header', True) else None
            
            # Use pandas to read the Excel file
            df = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name,
                header=header,
                engine='openpyxl'  # Use openpyxl engine for better .xlsx support
            )
            
            logger.info(f"Successfully read Excel file {self.file_path}, sheet '{sheet_name}' with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error reading Excel file: {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to read Excel file: {self.file_path}",
                details={
                    "file_path": self.file_path,
                    "sheet_name": self.config.get('sheet_name'),
                    "error": str(e)
                },
                original_exception=e
            )
    
    def get_sheet_names(self) -> List[str]:
        """
        Returns a list of sheet names in the Excel file.
        
        Returns:
            List of sheet names
            
        Raises:
            DataSourceException: If sheet name retrieval fails
        """
        try:
            # Validate the file first
            self.validate_file()
            
            # Use pandas ExcelFile to get sheet names
            with pd.ExcelFile(self.file_path, engine='openpyxl') as excel_file:
                sheet_names = excel_file.sheet_names
            
            logger.debug(f"Found {len(sheet_names)} sheets in {self.file_path}: {sheet_names}")
            return sheet_names
            
        except Exception as e:
            logger.error(f"Error getting sheet names for {self.file_path}", exc_info=True)
            raise DataSourceException(
                f"Failed to get sheet names for file: {self.file_path}",
                details={"file_path": self.file_path, "error": str(e)},
                original_exception=e
            )


def create_file_connector(file_path: str, config: Optional[Dict] = None) -> FileConnector:
    """
    Factory function to create the appropriate file connector based on file type.
    
    Args:
        file_path: Path to the file
        config: Optional configuration dictionary
        
    Returns:
        Appropriate FileConnector instance for the file type
        
    Raises:
        DataSourceException: If file type is not supported or file doesn't exist
    """
    if not file_path:
        raise DataSourceException("File path is required")
    
    if not os.path.exists(file_path):
        raise DataSourceException(
            f"File does not exist: {file_path}",
            details={"file_path": file_path}
        )
    
    # Determine file type from extension
    file_extension = Path(file_path).suffix.lower().lstrip('.')
    
    if file_extension == 'csv':
        return CSVConnector(file_path, config)
    elif file_extension in ['xlsx', 'xls']:
        return ExcelConnector(file_path, config)
    else:
        raise DataSourceException(
            f"Unsupported file type: {file_extension}. Supported types: {', '.join(SUPPORTED_FILE_TYPES)}",
            details={"file_path": file_path, "extension": file_extension}
        )