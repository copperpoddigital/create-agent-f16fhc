import os
import pytest
import pandas as pd
import pathlib
import tempfile

from ../../connectors.file_connector import FileConnector, CSVConnector, ExcelConnector
from ../../core.exceptions import DataSourceException, ValidationException

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), '../test_data')

def create_test_csv(temp_dir: str, filename: str) -> str:
    """Creates a temporary CSV file with test freight data for testing"""
    # Create a pandas DataFrame with sample freight data
    data = {
        'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'origin': ['Port A', 'Port B', 'Port C'],
        'destination': ['Port X', 'Port Y', 'Port Z'],
        'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
        'freight_charge': [1000.50, 2000.75, 1500.25],
        'currency_code': ['USD', 'EUR', 'USD'],
        'transport_mode': ['OCEAN', 'AIR', 'ROAD']
    }
    df = pd.DataFrame(data)
    
    # Define the file path in the temporary directory
    file_path = os.path.join(temp_dir, filename)
    
    # Write the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
    
    return file_path

def create_test_excel(temp_dir: str, filename: str) -> str:
    """Creates a temporary Excel file with test freight data for testing"""
    # Create a pandas DataFrame with sample freight data
    data = {
        'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'origin': ['Port A', 'Port B', 'Port C'],
        'destination': ['Port X', 'Port Y', 'Port Z'],
        'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
        'freight_charge': [1000.50, 2000.75, 1500.25],
        'currency_code': ['USD', 'EUR', 'USD'],
        'transport_mode': ['OCEAN', 'AIR', 'ROAD']
    }
    df = pd.DataFrame(data)
    
    # Define the file path in the temporary directory
    file_path = os.path.join(temp_dir, filename)
    
    # Write the DataFrame to an Excel file
    df.to_excel(file_path, index=False)
    
    return file_path

class TestFileConnector:
    """Test class for the FileConnector base class"""
    
    def test_init(self, tmp_path):
        """Tests that the FileConnector initializes correctly with a valid file path"""
        # Create a temporary test file
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(test_file)
        
        # Assert that the file_path attribute is set correctly
        assert connector.file_path == test_file
        
        # Assert that the config attribute is initialized with default values if not provided
        assert connector.config == {}
    
    def test_init_with_config(self, tmp_path):
        """Tests that the FileConnector initializes correctly with a custom configuration"""
        # Create a temporary test file
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Define a custom configuration dictionary
        config = {
            'delimiter': ';',
            'encoding': 'utf-8',
            'has_header': True
        }
        
        # Initialize a FileConnector with the test file path and custom config
        connector = FileConnector(test_file, config)
        
        # Assert that the config attribute contains the custom values
        assert connector.config == config
        assert connector.config.get('delimiter') == ';'
        assert connector.config.get('encoding') == 'utf-8'
        assert connector.config.get('has_header') is True
    
    def test_init_invalid_path(self):
        """Tests that the FileConnector raises an exception when initialized with an invalid file path"""
        # Use pytest.raises to assert that DataSourceException is raised
        with pytest.raises(DataSourceException):
            FileConnector("/path/to/nonexistent/file.csv")
    
    def test_validate_file(self, tmp_path):
        """Tests that validate_file correctly validates existing files with supported extensions"""
        # Create temporary test files with supported extensions (CSV, Excel)
        csv_file = create_test_csv(tmp_path, "test_file.csv")
        excel_file = create_test_excel(tmp_path, "test_file.xlsx")
        
        # Create file with unsupported extension
        txt_file = os.path.join(tmp_path, "test_file.txt")
        with open(txt_file, 'w') as f:
            f.write("This is a test file with unsupported extension.")
        
        # Initialize FileConnector instances with the test file paths
        csv_connector = FileConnector(csv_file)
        excel_connector = FileConnector(excel_file)
        txt_connector = FileConnector(txt_file)
        
        # Assert that validate_file returns True for valid files
        assert csv_connector.validate_file() is True
        assert excel_connector.validate_file() is True
        
        # Use pytest.raises to assert that DataSourceException is raised for invalid files
        with pytest.raises(DataSourceException):
            txt_connector.validate_file()
    
    def test_get_file_extension(self, tmp_path):
        """Tests that get_file_extension correctly extracts the file extension"""
        # Create temporary test files with different extensions
        csv_file = create_test_csv(tmp_path, "test_file.csv")
        excel_file = create_test_excel(tmp_path, "test_file.xlsx")
        
        # Initialize FileConnector instances with the test file paths
        csv_connector = FileConnector(csv_file)
        excel_connector = FileConnector(excel_file)
        
        # Assert that get_file_extension returns the correct extension for each file
        assert csv_connector.get_file_extension() == "csv"
        assert excel_connector.get_file_extension() == "xlsx"
    
    def test_get_file_info(self, tmp_path):
        """Tests that get_file_info returns correct metadata about the file"""
        # Create a temporary test file
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(test_file)
        
        # Call get_file_info and store the result
        info = connector.get_file_info()
        
        # Assert that the result is a dictionary containing expected keys
        assert isinstance(info, dict)
        assert 'file_name' in info
        assert 'extension' in info
        assert 'size_bytes' in info
        assert 'size_human' in info
        assert 'modified_time' in info
        assert 'modified_time_human' in info
        assert 'absolute_path' in info
        assert 'is_valid' in info
        
        # Assert that the values are of the expected types
        assert info['file_name'] == "test_file.csv"
        assert info['extension'] == "csv"
        assert isinstance(info['size_bytes'], int)
        assert isinstance(info['size_human'], str)
        assert isinstance(info['modified_time'], float)
        assert isinstance(info['modified_time_human'], str)
        assert isinstance(info['absolute_path'], str)
        assert info['is_valid'] is True
    
    def test_read_file(self, tmp_path):
        """Tests that read_file correctly reads and returns file contents as a DataFrame"""
        # Create a temporary test CSV file with known content
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(test_file)
        
        # Call read_file and store the result
        df = connector.read_file()
        
        # Assert that the result is a pandas DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Assert that the DataFrame contains the expected data
        assert len(df) == 3  # 3 rows
        assert 'record_date' in df.columns
        assert 'origin' in df.columns
        assert 'destination' in df.columns
        assert 'carrier' in df.columns
        assert 'freight_charge' in df.columns
        assert 'currency_code' in df.columns
        assert 'transport_mode' in df.columns
    
    def test_read_file_unsupported(self, tmp_path):
        """Tests that read_file raises an exception for unsupported file types"""
        # Create a temporary file with an unsupported extension (e.g., .txt)
        txt_file = os.path.join(tmp_path, "test_file.txt")
        with open(txt_file, 'w') as f:
            f.write("This is a test file with unsupported extension.")
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(txt_file)
        
        # Use pytest.raises to assert that DataSourceException is raised when calling read_file
        with pytest.raises(DataSourceException):
            connector.read_file()
    
    def test_fetch_freight_data(self, tmp_path):
        """Tests that fetch_freight_data correctly processes and returns freight data"""
        # Create a temporary test CSV file with valid freight data
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(test_file)
        
        # Call fetch_freight_data and store the result
        df = connector.fetch_freight_data()
        
        # Assert that the result is a pandas DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Assert that the DataFrame contains the expected columns and data
        assert len(df) == 3  # 3 rows
        assert 'record_date' in df.columns
        assert 'origin' in df.columns
        assert 'destination' in df.columns
        assert 'carrier' in df.columns
        assert 'freight_charge' in df.columns
        assert 'currency_code' in df.columns
        assert 'transport_mode' in df.columns
        
        # Assert that the data has been properly validated and transformed
        assert 'data_quality_flag' in df.columns
    
    def test_fetch_freight_data_with_mapping(self, tmp_path):
        """Tests that fetch_freight_data correctly applies column mapping"""
        # Create a temporary test CSV file with columns using non-standard names
        data = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'from': ['Port A', 'Port B', 'Port C'],
            'to': ['Port X', 'Port Y', 'Port Z'],
            'shipping_company': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
            'price': [1000.50, 2000.75, 1500.25],
            'currency': ['USD', 'EUR', 'USD'],
            'mode': ['OCEAN', 'AIR', 'ROAD']
        }
        df = pd.DataFrame(data)
        file_path = os.path.join(tmp_path, "test_mapping.csv")
        df.to_csv(file_path, index=False)
        
        # Define a column mapping dictionary to map source columns to standard names
        column_mapping = {
            'date': 'record_date',
            'from': 'origin',
            'to': 'destination',
            'shipping_company': 'carrier',
            'price': 'freight_charge',
            'currency': 'currency_code',
            'mode': 'transport_mode'
        }
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(file_path)
        
        # Call fetch_freight_data with the column mapping and store the result
        df = connector.fetch_freight_data(column_mapping=column_mapping)
        
        # Assert that the result contains the standardized column names
        assert 'record_date' in df.columns
        assert 'origin' in df.columns
        assert 'destination' in df.columns
        assert 'carrier' in df.columns
        assert 'freight_charge' in df.columns
        assert 'currency_code' in df.columns
        assert 'transport_mode' in df.columns
        
        # Assert that the data has been properly mapped and validated
        assert 'data_quality_flag' in df.columns
    
    def test_fetch_freight_data_invalid(self, tmp_path):
        """Tests that fetch_freight_data raises appropriate exceptions for invalid data"""
        # Create a temporary test CSV file with invalid freight data (missing required columns)
        data = {
            'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'origin': ['Port A', 'Port B', 'Port C'],
            # Missing required columns: destination, carrier, freight_charge, currency_code, transport_mode
        }
        df = pd.DataFrame(data)
        file_path = os.path.join(tmp_path, "test_invalid.csv")
        df.to_csv(file_path, index=False)
        
        # Initialize a FileConnector with the test file path
        connector = FileConnector(file_path)
        
        # Use pytest.raises to assert that ValidationException is raised when calling fetch_freight_data
        with pytest.raises(ValidationException):
            connector.fetch_freight_data()

class TestCSVConnector:
    """Test class for the CSVConnector specialized class"""
    
    def test_init(self, tmp_path):
        """Tests that the CSVConnector initializes correctly with a valid CSV file path"""
        # Create a temporary test CSV file
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a CSVConnector with the test file path
        connector = CSVConnector(test_file)
        
        # Assert that the file_path attribute is set correctly
        assert connector.file_path == test_file
        
        # Assert that the config attribute is initialized with CSV-specific default values
        assert connector.config.get('delimiter') == ','
        assert connector.config.get('encoding') == 'utf-8'
        assert connector.config.get('has_header') is True
    
    def test_read_file(self, tmp_path):
        """Tests that read_file correctly reads and returns CSV file contents as a DataFrame"""
        # Create a temporary test CSV file with known content
        test_file = create_test_csv(tmp_path, "test_file.csv")
        
        # Initialize a CSVConnector with the test file path
        connector = CSVConnector(test_file)
        
        # Call read_file and store the result
        df = connector.read_file()
        
        # Assert that the result is a pandas DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Assert that the DataFrame contains the expected data
        assert len(df) == 3  # 3 rows
        assert 'record_date' in df.columns
        assert 'origin' in df.columns
        assert 'destination' in df.columns
        assert 'carrier' in df.columns
        assert 'freight_charge' in df.columns
        assert 'currency_code' in df.columns
        assert 'transport_mode' in df.columns
        
        # Assert that CSV-specific options (delimiter, encoding, header) are applied correctly
        assert df.iloc[0]['origin'] == 'Port A'
        assert df.iloc[1]['destination'] == 'Port Y'
    
    def test_read_file_custom_options(self, tmp_path):
        """Tests that read_file correctly applies custom CSV options"""
        # Create a temporary test CSV file with custom delimiter and no header
        data = {
            'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'origin': ['Port A', 'Port B', 'Port C'],
            'destination': ['Port X', 'Port Y', 'Port Z'],
            'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
            'freight_charge': [1000.50, 2000.75, 1500.25],
            'currency_code': ['USD', 'EUR', 'USD'],
            'transport_mode': ['OCEAN', 'AIR', 'ROAD']
        }
        df = pd.DataFrame(data)
        file_path = os.path.join(tmp_path, "test_custom.csv")
        df.to_csv(file_path, index=False, sep=';', header=False)
        
        # Define a custom configuration with specific delimiter and header settings
        config = {
            'delimiter': ';',
            'encoding': 'utf-8',
            'has_header': False,
            'usecols': [0, 1, 2, 3, 4, 5, 6]  # Use all columns
        }
        
        # Initialize a CSVConnector with the test file path and custom config
        connector = CSVConnector(file_path, config)
        
        # Call read_file and store the result
        df = connector.read_file()
        
        # Assert that the result contains the expected data with custom options applied
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3  # 3 rows
        assert len(df.columns) == 7  # 7 columns
    
    def test_preview_data(self, tmp_path):
        """Tests that preview_data returns the first n rows of the CSV data"""
        # Create a temporary test CSV file with multiple rows
        data = {
            'record_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'origin': ['Port A', 'Port B', 'Port C', 'Port D', 'Port E'],
            'destination': ['Port X', 'Port Y', 'Port Z', 'Port W', 'Port V'],
            'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3', 'Carrier 4', 'Carrier 5'],
            'freight_charge': [1000.50, 2000.75, 1500.25, 1800.00, 2200.50],
            'currency_code': ['USD', 'EUR', 'USD', 'EUR', 'USD'],
            'transport_mode': ['OCEAN', 'AIR', 'ROAD', 'RAIL', 'OCEAN']
        }
        df = pd.DataFrame(data)
        file_path = os.path.join(tmp_path, "test_preview.csv")
        df.to_csv(file_path, index=False)
        
        # Initialize a CSVConnector with the test file path
        connector = CSVConnector(file_path)
        
        # Call preview_data with n_rows=3 and store the result
        preview_df = connector.preview_data(n_rows=3)
        
        # Assert that the result is a pandas DataFrame
        assert isinstance(preview_df, pd.DataFrame)
        
        # Assert that the DataFrame contains exactly 3 rows
        assert len(preview_df) == 3
        
        # Assert that the rows match the first 3 rows of the original data
        assert preview_df.iloc[0]['record_date'] == '2023-01-01'
        assert preview_df.iloc[1]['record_date'] == '2023-01-02'
        assert preview_df.iloc[2]['record_date'] == '2023-01-03'

class TestExcelConnector:
    """Test class for the ExcelConnector specialized class"""
    
    def test_init(self, tmp_path):
        """Tests that the ExcelConnector initializes correctly with a valid Excel file path"""
        # Create a temporary test Excel file
        test_file = create_test_excel(tmp_path, "test_file.xlsx")
        
        # Initialize an ExcelConnector with the test file path
        connector = ExcelConnector(test_file)
        
        # Assert that the file_path attribute is set correctly
        assert connector.file_path == test_file
        
        # Assert that the config attribute is initialized with Excel-specific default values
        assert connector.config.get('sheet_name') == 0  # First sheet by default
        assert connector.config.get('has_header') is True
    
    def test_read_file(self, tmp_path):
        """Tests that read_file correctly reads and returns Excel file contents as a DataFrame"""
        # Create a temporary test Excel file with known content
        test_file = create_test_excel(tmp_path, "test_file.xlsx")
        
        # Initialize an ExcelConnector with the test file path
        connector = ExcelConnector(test_file)
        
        # Call read_file and store the result
        df = connector.read_file()
        
        # Assert that the result is a pandas DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Assert that the DataFrame contains the expected data
        assert len(df) == 3  # 3 rows
        assert 'record_date' in df.columns
        assert 'origin' in df.columns
        assert 'destination' in df.columns
        assert 'carrier' in df.columns
        assert 'freight_charge' in df.columns
        assert 'currency_code' in df.columns
        assert 'transport_mode' in df.columns
        
        # Assert that Excel-specific options (sheet_name, header) are applied correctly
        assert df.iloc[0]['origin'] == 'Port A'
        assert df.iloc[1]['destination'] == 'Port Y'
    
    def test_read_file_custom_sheet(self, tmp_path):
        """Tests that read_file correctly reads from a specified sheet"""
        # Create a temporary test Excel file with multiple sheets
        data1 = {
            'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'origin': ['Port A', 'Port B', 'Port C'],
            'destination': ['Port X', 'Port Y', 'Port Z'],
            'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
            'freight_charge': [1000.50, 2000.75, 1500.25],
            'currency_code': ['USD', 'EUR', 'USD'],
            'transport_mode': ['OCEAN', 'AIR', 'ROAD']
        }
        
        data2 = {
            'record_date': ['2023-02-01', '2023-02-02', '2023-02-03'],
            'origin': ['Port P', 'Port Q', 'Port R'],
            'destination': ['Port M', 'Port N', 'Port O'],
            'carrier': ['Carrier 4', 'Carrier 5', 'Carrier 6'],
            'freight_charge': [1200.50, 2100.75, 1600.25],
            'currency_code': ['USD', 'EUR', 'USD'],
            'transport_mode': ['RAIL', 'OCEAN', 'AIR']
        }
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        file_path = os.path.join(tmp_path, "test_multi_sheet.xlsx")
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
        
        # Define a custom configuration with a specific sheet_name
        config = {
            'sheet_name': 'Sheet2',
            'has_header': True
        }
        
        # Initialize an ExcelConnector with the test file path and custom config
        connector = ExcelConnector(file_path, config)
        
        # Call read_file and store the result
        df = connector.read_file()
        
        # Assert that the result contains the data from the specified sheet
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3  # 3 rows
        assert df.iloc[0]['origin'] == 'Port P'  # First origin from Sheet2
        assert df.iloc[0]['record_date'] == '2023-02-01'  # First date from Sheet2
    
    def test_get_sheet_names(self, tmp_path):
        """Tests that get_sheet_names returns a list of sheet names in the Excel file"""
        # Create a temporary test Excel file with multiple sheets
        data1 = {
            'record_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'origin': ['Port A', 'Port B', 'Port C'],
            'destination': ['Port X', 'Port Y', 'Port Z'],
            'carrier': ['Carrier 1', 'Carrier 2', 'Carrier 3'],
            'freight_charge': [1000.50, 2000.75, 1500.25],
            'currency_code': ['USD', 'EUR', 'USD'],
            'transport_mode': ['OCEAN', 'AIR', 'ROAD']
        }
        
        data2 = {
            'record_date': ['2023-02-01', '2023-02-02', '2023-02-03'],
            'origin': ['Port P', 'Port Q', 'Port R'],
            'destination': ['Port M', 'Port N', 'Port O'],
            'carrier': ['Carrier 4', 'Carrier 5', 'Carrier 6'],
            'freight_charge': [1200.50, 2100.75, 1600.25],
            'currency_code': ['USD', 'EUR', 'USD'],
            'transport_mode': ['RAIL', 'OCEAN', 'AIR']
        }
        
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        file_path = os.path.join(tmp_path, "test_sheet_names.xlsx")
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
        
        # Initialize an ExcelConnector with the test file path
        connector = ExcelConnector(file_path)
        
        # Call get_sheet_names and store the result
        sheet_names = connector.get_sheet_names()
        
        # Assert that the result is a list
        assert isinstance(sheet_names, list)
        
        # Assert that the list contains the expected sheet names
        assert len(sheet_names) == 2
        assert 'Sheet1' in sheet_names
        assert 'Sheet2' in sheet_names