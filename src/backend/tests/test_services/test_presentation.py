import pytest  # version: ^7.0.0
import unittest.mock  # version: standard library
import json  # version: standard library
import csv  # version: standard library
import io  # version: standard library
import os  # version: standard library
import tempfile  # version: standard library
import typing  # version: standard library
from datetime import datetime  # version: standard library
from decimal import Decimal  # version: standard library

from src.backend.services.presentation import PresentationService, format_json_output, format_csv_output, format_text_output, generate_visualization  # Adjust import based on your project structure
from src.backend.models.analysis_result import AnalysisResult  # Adjust import based on your project structure
from src.backend.core.exceptions import PresentationException  # Adjust import based on your project structure
from src.backend.models.enums import OutputFormat, TrendDirection, AnalysisStatus  # Adjust import based on your project structure
from src.backend.services.analysis_engine import AnalysisEngine  # Adjust import based on your project structure


def create_mock_analysis_result(analysis_id: str, output_format: typing.Optional[OutputFormat] = None) -> AnalysisResult:
    """Creates a mock AnalysisResult object for testing"""
    # Create a mock AnalysisResult instance
    analysis_result = AnalysisResult(time_period_id="123")
    # Set id to the provided analysis_id
    analysis_result.id = analysis_id
    # Set status to COMPLETED
    analysis_result.status = AnalysisStatus.COMPLETED
    # Set output_format to the provided value or default to JSON
    analysis_result.output_format = output_format or OutputFormat.JSON
    # Set time_period_id to a sample UUID
    analysis_result.time_period_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    # Set start_value, end_value, absolute_change, percentage_change to sample values
    analysis_result.start_value = Decimal("100.00")
    analysis_result.end_value = Decimal("110.00")
    analysis_result.absolute_change = Decimal("10.00")
    analysis_result.percentage_change = Decimal("10.00")
    # Set trend_direction to a sample trend
    analysis_result.trend_direction = TrendDirection.INCREASING
    # Set currency_code to 'USD'
    analysis_result.currency_code = "USD"
    # Set results to a sample dictionary with time series data
    analysis_result.results = {
        "time_series": [
            {"date": "2023-01-01", "value": 100.00},
            {"date": "2023-01-08", "value": 102.00},
            {"date": "2023-01-15", "value": 105.00},
            {"date": "2023-01-22", "value": 108.00},
            {"date": "2023-01-29", "value": 110.00},
        ]
    }
    # Set calculated_at to current datetime
    analysis_result.calculated_at = datetime.now()
    # Return the mock AnalysisResult
    return analysis_result


class TestPresentationService:
    """Test suite for the PresentationService class"""

    def setup_method(self, method):
        """Set up test environment before each test"""
        # Create a mock AnalysisEngine
        self.mock_engine = unittest.mock.Mock(spec=AnalysisEngine)
        # Configure the mock to return appropriate test data
        self.mock_engine.get_analysis_result.return_value = create_mock_analysis_result("test_analysis")
        # Create a PresentationService instance with the mock engine
        self.presentation_service = PresentationService(analysis_engine=self.mock_engine)
        # Set up sample analysis results for testing
        self.sample_analysis_result = create_mock_analysis_result("test_analysis")

    def test_format_result_json(self, mocker):
        """Test formatting results in JSON format"""
        # Set up a mock analysis result with JSON output format
        mock_result = create_mock_analysis_result("json_analysis", output_format=OutputFormat.JSON)
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Call format_result with the analysis ID
        result = self.presentation_service.format_result("json_analysis")
        # Verify the result is properly formatted as JSON
        assert result["output_format"] == "JSON"
        # Verify the structure matches the expected JSON output format
        json_output = json.loads(result["output"])
        assert "id" in json_output
        assert "start_value" in json_output
        # Verify all required fields are present and correctly formatted
        assert json_output["id"] == "json_analysis"
        assert json_output["start_value"] == 100.00

    def test_format_result_csv(self):
        """Test formatting results in CSV format"""
        # Set up a mock analysis result with CSV output format
        mock_result = create_mock_analysis_result("csv_analysis", output_format=OutputFormat.CSV)
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Call format_result with the analysis ID
        result = self.presentation_service.format_result("csv_analysis")
        # Verify the result is properly formatted as CSV
        assert result["output_format"] == "CSV"
        # Parse the CSV and verify the headers and data rows
        csv_data = io.StringIO(result["output"])
        reader = csv.reader(csv_data)
        rows = list(reader)
        assert len(rows) > 0
        # Verify all required fields are present and correctly formatted
        assert "start_value" in rows[0]

    def test_format_result_text(self):
        """Test formatting results in text format"""
        # Set up a mock analysis result with TEXT output format
        mock_result = create_mock_analysis_result("text_analysis", output_format=OutputFormat.TEXT)
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Call format_result with the analysis ID
        result = self.presentation_service.format_result("text_analysis")
        # Verify the result is properly formatted as text
        assert result["output_format"] == "TEXT"
        # Verify the text contains all required sections (summary, details, statistics)
        assert "SUMMARY:" in result["output"]
        assert "DETAILS:" in result["output"]
        assert "STATISTICS:" in result["output"]
        # Verify all required information is present and correctly formatted
        assert "Freight Price Movement Analysis" in result["output"]

    def test_format_result_with_visualization(self):
        """Test formatting results with visualization"""
        # Set up a mock analysis result
        mock_result = create_mock_analysis_result("visual_analysis")
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Call format_result with include_visualization=True
        result = self.presentation_service.format_result("visual_analysis", include_visualization=True)
        # Verify the result includes visualization data
        assert "visualization" in result
        assert result["visualization"] is not None
        # Verify the visualization data has the expected structure
        assert "chart_type" in result["visualization"]
        # Verify the visualization type is appropriate for the data
        assert result["visualization"]["chart_type"] == "line"

    def test_export_result(self):
        """Test exporting results to a file"""
        # Set up a mock analysis result
        mock_result = create_mock_analysis_result("export_analysis")
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            file_path = tmp_file.name
        # Call export_result with the analysis ID and file path
        result = self.presentation_service.export_result("export_analysis", file_path=file_path)
        # Verify the file was created
        assert os.path.exists(file_path)
        # Verify the file contents match the expected format
        with open(file_path, "r") as f:
            file_contents = f.read()
        assert "id" in file_contents
        # Clean up the temporary file
        os.remove(file_path)

    def test_generate_summary(self):
        """Test generating a summary of analysis results"""
        # Set up a mock analysis result
        mock_result = create_mock_analysis_result("summary_analysis")
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Call generate_summary with the analysis ID
        summary = self.presentation_service.generate_summary("summary_analysis")
        # Verify the summary has the expected structure
        assert "start_value" in summary
        assert "end_value" in summary
        # Verify the summary contains key metrics (absolute change, percentage change, trend)
        assert "absolute_change" in summary
        assert "percentage_change" in summary
        assert "trend_direction" in summary
        # Verify the metrics are correctly formatted
        assert summary["start_value"] == "$100.00"

    def test_format_comparison(self):
        """Test formatting a comparison between two analysis results"""
        # Set up two mock analysis results
        mock_result1 = create_mock_analysis_result("base_analysis")
        mock_result2 = create_mock_analysis_result("comparison_analysis")
        # Configure the mock engine to return these results
        self.mock_engine.get_analysis_result.side_effect = [mock_result1, mock_result2]
        # Call format_comparison with both analysis IDs
        comparison = self.presentation_service.format_comparison("base_analysis", "comparison_analysis")
        # Verify the comparison has the expected structure
        assert "base_analysis" in comparison
        assert "comparison_analysis" in comparison
        # Verify the comparison includes both individual results
        assert "id" in json.loads(comparison["base_analysis"])
        assert "id" in json.loads(comparison["comparison_analysis"])
        # Verify the comparison includes difference calculations
        assert "difference" in comparison
        # Verify the formatting is correct for the specified output format
        assert comparison["difference"] == "-$0.00"

    def test_error_handling_missing_result(self):
        """Test error handling when analysis result is not found"""
        # Configure the mock engine to return None (no result found)
        self.mock_engine.get_analysis_result.return_value = None
        # Use pytest.raises to verify that PresentationException is raised
        with pytest.raises(PresentationException) as exc_info:
            # Call format_result with a non-existent analysis ID
            self.presentation_service.format_result("non_existent_analysis")
        # Verify the exception message indicates the result was not found
        assert "Analysis result not found" in str(exc_info.value)

    def test_error_handling_invalid_format(self):
        """Test error handling when an invalid output format is specified"""
        # Set up a mock analysis result
        mock_result = create_mock_analysis_result("invalid_format_analysis")
        # Configure the mock engine to return this result
        self.mock_engine.get_analysis_result.return_value = mock_result
        # Use pytest.raises to verify that PresentationException is raised
        with pytest.raises(PresentationException) as exc_info:
            # Call format_result with an invalid output format
            self.presentation_service.format_result("invalid_format_analysis", output_format="INVALID")
        # Verify the exception message indicates the format is invalid
        assert "Unsupported output format" in str(exc_info.value)


class TestFormatFunctions:
    """Test suite for individual formatter functions"""

    def test_format_json_output(self):
        """Test the format_json_output function"""
        # Create a mock AnalysisResult with sample data
        mock_result = create_mock_analysis_result("json_format_test")
        # Call format_json_output with the mock result
        json_string = format_json_output(mock_result)
        # Parse the returned JSON string
        json_output = json.loads(json_string)
        # Verify the JSON structure matches the expected format
        assert "id" in json_output
        assert "start_value" in json_output
        # Verify all required fields are present and correctly formatted
        assert json_output["id"] == "json_format_test"
        assert json_output["start_value"] == 100.00
        # Test with pretty_print=True and verify the formatting
        json_string_pretty = format_json_output(mock_result, pretty_print=True)
        assert len(json_string_pretty) > len(json_string)

    def test_format_csv_output(self):
        """Test the format_csv_output function"""
        # Create a mock AnalysisResult with sample data
        mock_result = create_mock_analysis_result("csv_format_test")
        # Call format_csv_output with the mock result
        csv_string = format_csv_output(mock_result)
        # Parse the returned CSV string
        csv_data = io.StringIO(csv_string)
        reader = csv.reader(csv_data)
        rows = list(reader)
        # Verify the CSV headers match the expected format
        assert "start_value" in rows[0]
        # Verify the data rows contain the correct values
        assert "100.0" in rows[1]
        # Verify all required fields are present and correctly formatted
        assert len(rows) > 0

    def test_format_text_output(self):
        """Test the format_text_output function"""
        # Create a mock AnalysisResult with sample data
        mock_result = create_mock_analysis_result("text_format_test")
        # Call format_text_output with the mock result
        text_output = format_text_output(mock_result)
        # Verify the text contains all required sections
        assert "SUMMARY:" in text_output
        assert "DETAILS:" in text_output
        assert "STATISTICS:" in text_output
        # Verify the text includes properly formatted metrics
        assert "$100.00" in text_output
        # Verify the text includes time period information
        assert "2023-01-01 to 2023-01-29" in text_output
        # Verify all required information is present and correctly formatted
        assert "Freight Price Movement Analysis" in text_output

    def test_generate_visualization(self):
        """Test the generate_visualization function"""
        # Create a mock AnalysisResult with time series data
        mock_result = create_mock_analysis_result("visual_format_test")
        # Call generate_visualization with the mock result
        visualization = generate_visualization(mock_result)
        # Verify the returned object has the expected structure
        assert "chart_type" in visualization
        # Verify it includes visualization data (e.g., base64-encoded images)
        assert "image" in visualization
        # Test with different visualization_type parameters
        visualization_bar = generate_visualization(mock_result, visualization_type="bar")
        assert "chart_type" in visualization_bar
        # Verify the visualization type is appropriate for the data
        assert visualization_bar["chart_type"] == "bar"

    def test_format_functions_error_handling(self):
        """Test error handling in formatter functions"""
        # Create a mock AnalysisResult with invalid or missing data
        mock_result = create_mock_analysis_result("error_format_test")
        mock_result.start_value = None
        mock_result.end_value = None
        mock_result.results = None
        # Use pytest.raises to verify appropriate exceptions are raised
        with pytest.raises(PresentationException):
            # Test each formatter function with the invalid data
            format_json_output(mock_result)
        with pytest.raises(PresentationException):
            format_csv_output(mock_result)
        with pytest.raises(PresentationException):
            format_text_output(mock_result)
        with pytest.raises(PresentationException):
            generate_visualization(mock_result)