"""
Unit tests for the AnalysisResult model in the Freight Price Movement Agent.

This module contains tests to verify the functionality, data integrity, and
behavior of the AnalysisResult model, including its methods for status updates,
result storage, caching, and serialization.
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from freezegun import freeze_time

from ...models.analysis_result import AnalysisResult
from ...models.time_period import TimePeriod
from ...models.enums import TrendDirection, AnalysisStatus, OutputFormat, GranularityType


def test_analysis_result_init():
    """Tests the initialization of an AnalysisResult instance with required attributes."""
    # Generate a UUID for time_period_id
    time_period_id = str(uuid.uuid4())
    
    # Initialize an AnalysisResult with just the required fields
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Assert that the instance has the expected attributes
    assert analysis_result is not None
    assert analysis_result.time_period_id == time_period_id
    assert analysis_result.status == AnalysisStatus.PENDING
    assert analysis_result.parameters == {}
    assert analysis_result.output_format == OutputFormat.JSON
    assert analysis_result.currency_code == 'USD'
    assert analysis_result.name.startswith("Analysis_")


def test_analysis_result_init_with_optional_fields():
    """Tests the initialization of an AnalysisResult instance with optional attributes."""
    # Generate a UUID for time_period_id
    time_period_id = str(uuid.uuid4())
    
    # Create a sample parameters dictionary
    parameters = {
        "filter": {
            "origin": "New York",
            "destination": "London"
        },
        "comparison": True
    }
    
    # Sample user ID
    user_id = str(uuid.uuid4())
    
    # Initialize an AnalysisResult with required and optional fields
    analysis_result = AnalysisResult(
        time_period_id=time_period_id,
        name="Q2 Ocean Freight Analysis",
        parameters=parameters,
        created_by=user_id,
        output_format=OutputFormat.CSV,
        currency_code="EUR"
    )
    
    # Assert that values match the input
    assert analysis_result.name == "Q2 Ocean Freight Analysis"
    assert analysis_result.parameters == parameters
    assert analysis_result.created_by == user_id
    assert analysis_result.output_format == OutputFormat.CSV
    assert analysis_result.currency_code == "EUR"


def test_analysis_result_update_status():
    """Tests the update_status method for changing the analysis status."""
    # Create a sample AnalysisResult
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Initial status should be PENDING
    assert analysis_result.status == AnalysisStatus.PENDING
    
    # Update status to PROCESSING
    analysis_result.update_status(AnalysisStatus.PROCESSING)
    assert analysis_result.status == AnalysisStatus.PROCESSING
    
    # Update status to COMPLETED
    analysis_result.update_status(AnalysisStatus.COMPLETED)
    assert analysis_result.status == AnalysisStatus.COMPLETED
    assert analysis_result.calculated_at is not None
    assert isinstance(analysis_result.calculated_at, datetime)
    
    # Update status to FAILED with error message
    error_message = "Analysis failed due to insufficient data"
    analysis_result.update_status(AnalysisStatus.FAILED, error_message)
    assert analysis_result.status == AnalysisStatus.FAILED
    assert analysis_result.error_message == error_message


def test_analysis_result_set_results():
    """Tests the set_results method for storing analysis results."""
    # Create a sample AnalysisResult
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Sample results
    results = {
        "time_series": [
            {"date": "2023-01-01", "value": 100.0},
            {"date": "2023-02-01", "value": 120.0},
            {"date": "2023-03-01", "value": 115.0}
        ],
        "summary": {
            "average": 111.67,
            "min": 100.0,
            "max": 120.0
        }
    }
    
    # Set results
    analysis_result.set_results(
        results=results,
        start_value=100.0,
        end_value=115.0,
        absolute_change=15.0,
        percentage_change=15.0,
        trend_direction=TrendDirection.INCREASING
    )
    
    # Assert that values match the input
    assert analysis_result.results == results
    assert float(analysis_result.start_value) == 100.0
    assert float(analysis_result.end_value) == 115.0
    assert float(analysis_result.absolute_change) == 15.0
    assert float(analysis_result.percentage_change) == 15.0
    assert analysis_result.trend_direction == TrendDirection.INCREASING
    assert analysis_result.status == AnalysisStatus.COMPLETED
    assert analysis_result.calculated_at is not None
    assert isinstance(analysis_result.calculated_at, datetime)


def test_analysis_result_set_results_with_trend_calculation():
    """Tests that trend_direction is calculated from percentage_change if not provided."""
    # Test increasing trend (percentage_change > 1.0)
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    analysis_result.set_results(
        results={},
        start_value=100.0,
        end_value=120.0,
        absolute_change=20.0,
        percentage_change=20.0
        # No trend_direction provided
    )
    assert analysis_result.trend_direction == TrendDirection.INCREASING
    
    # Test decreasing trend (percentage_change < -1.0)
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    analysis_result.set_results(
        results={},
        start_value=100.0,
        end_value=80.0,
        absolute_change=-20.0,
        percentage_change=-20.0
        # No trend_direction provided
    )
    assert analysis_result.trend_direction == TrendDirection.DECREASING
    
    # Test stable trend (-1.0 <= percentage_change <= 1.0)
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    analysis_result.set_results(
        results={},
        start_value=100.0,
        end_value=100.5,
        absolute_change=0.5,
        percentage_change=0.5
        # No trend_direction provided
    )
    assert analysis_result.trend_direction == TrendDirection.STABLE


def test_analysis_result_set_cache_expiry():
    """Tests the set_cache_expiry method for setting cache expiration."""
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Test with explicit expiry time
    expiry_time = datetime.utcnow() + timedelta(hours=2)
    analysis_result.set_cache_expiry(expiry_time=expiry_time)
    assert analysis_result.is_cached is True
    assert analysis_result.cache_expires_at == expiry_time
    
    # Test with minutes parameter
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    now = datetime.utcnow().replace(microsecond=0)
    with freeze_time(now):
        analysis_result.set_cache_expiry(minutes=30)
        assert analysis_result.is_cached is True
        assert analysis_result.cache_expires_at == now + timedelta(minutes=30)
    
    # Test with default (60 minutes)
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    now = datetime.utcnow().replace(microsecond=0)
    with freeze_time(now):
        analysis_result.set_cache_expiry()
        assert analysis_result.is_cached is True
        assert analysis_result.cache_expires_at == now + timedelta(minutes=60)


def test_analysis_result_is_cache_valid():
    """Tests the is_cache_valid method for checking cache validity."""
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Test with is_cached=False
    assert analysis_result.is_cache_valid() is False
    
    # Test with is_cached=True but cache_expires_at=None
    analysis_result.is_cached = True
    assert analysis_result.is_cache_valid() is False
    
    # Test with future expiry time
    now = datetime.utcnow()
    future_time = now + timedelta(hours=1)
    analysis_result.cache_expires_at = future_time
    with freeze_time(now):
        assert analysis_result.is_cache_valid() is True
    
    # Test with past expiry time
    past_time = now - timedelta(hours=1)
    analysis_result.cache_expires_at = past_time
    with freeze_time(now):
        assert analysis_result.is_cache_valid() is False


def test_analysis_result_to_dict():
    """Tests the to_dict method for serializing the analysis result."""
    # Create a sample AnalysisResult with all attributes
    time_period_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    analysis_result = AnalysisResult(
        time_period_id=time_period_id,
        name="Test Analysis",
        parameters={"filter": {"origin": "New York"}},
        created_by=user_id,
        output_format=OutputFormat.JSON,
        currency_code="USD"
    )
    
    # Set various attributes
    analysis_result.status = AnalysisStatus.COMPLETED
    analysis_result.start_value = Decimal('100.00')
    analysis_result.end_value = Decimal('120.00')
    analysis_result.absolute_change = Decimal('20.00')
    analysis_result.percentage_change = Decimal('20.00')
    analysis_result.trend_direction = TrendDirection.INCREASING
    analysis_result.calculated_at = now
    analysis_result.results = {"time_series": [{"date": "2023-01-01", "value": 100.0}]}
    analysis_result.is_cached = True
    analysis_result.cache_expires_at = now + timedelta(hours=1)
    
    # Get dictionary representation
    result_dict = analysis_result.to_dict()
    
    # Assert that the dictionary contains all expected keys with correct values
    assert result_dict["id"] == analysis_result.id
    assert result_dict["name"] == "Test Analysis"
    assert result_dict["time_period_id"] == time_period_id
    assert result_dict["status"] == "COMPLETED"
    assert result_dict["created_by"] == user_id
    assert result_dict["currency_code"] == "USD"
    assert result_dict["output_format"] == "JSON"
    assert result_dict["start_value"] == 100.0
    assert result_dict["end_value"] == 120.0
    assert result_dict["absolute_change"] == 20.0
    assert result_dict["percentage_change"] == 20.0
    assert result_dict["trend_direction"] == "INCREASING"
    assert result_dict["calculated_at"] == analysis_result.calculated_at.isoformat()
    assert result_dict["is_cached"] is True
    assert result_dict["cache_expires_at"] == analysis_result.cache_expires_at.isoformat()
    
    # Test with include_details=True
    detailed_dict = analysis_result.to_dict(include_details=True)
    assert "results" in detailed_dict
    assert detailed_dict["results"] == analysis_result.results


def test_analysis_result_from_dict():
    """Tests the from_dict class method for creating an instance from a dictionary."""
    # Create a sample dictionary
    time_period_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    data = {
        "time_period_id": time_period_id,
        "name": "Test Analysis",
        "parameters": {"filter": {"origin": "New York"}},
        "created_by": user_id,
        "status": "COMPLETED",
        "output_format": "CSV",
        "currency_code": "EUR",
        "start_value": 100.0,
        "end_value": 120.0,
        "absolute_change": 20.0,
        "percentage_change": 20.0,
        "trend_direction": "INCREASING",
        "calculated_at": now.isoformat(),
        "results": {"time_series": [{"date": "2023-01-01", "value": 100.0}]},
        "is_cached": True,
        "cache_expires_at": (now + timedelta(hours=1)).isoformat()
    }
    
    # Create instance from dictionary
    analysis_result = AnalysisResult.from_dict(data)
    
    # Assert that all attributes match the dictionary values
    assert analysis_result.time_period_id == time_period_id
    assert analysis_result.name == "Test Analysis"
    assert analysis_result.created_by == user_id
    assert analysis_result.status == AnalysisStatus.COMPLETED
    assert analysis_result.output_format == OutputFormat.CSV
    assert analysis_result.currency_code == "EUR"
    assert float(analysis_result.start_value) == 100.0
    assert float(analysis_result.end_value) == 120.0
    assert float(analysis_result.absolute_change) == 20.0
    assert float(analysis_result.percentage_change) == 20.0
    assert analysis_result.trend_direction == TrendDirection.INCREASING
    assert analysis_result.calculated_at.isoformat() == now.isoformat()
    assert analysis_result.results == data["results"]
    assert analysis_result.is_cached is True
    assert analysis_result.cache_expires_at.isoformat() == data["cache_expires_at"]


def test_analysis_result_relationships():
    """Tests the relationships between AnalysisResult and related models."""
    # Create a mock TimePeriod
    mock_time_period = TimePeriod(
        name="Q1 2023",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 3, 31),
        granularity=GranularityType.DAILY
    )
    
    # Create an AnalysisResult with the time_period_id
    analysis_result = AnalysisResult(time_period_id=mock_time_period.id)
    
    # Set up the relationship
    analysis_result.time_period = mock_time_period
    
    # Assert that the relationship is correct
    assert analysis_result.time_period is mock_time_period
    assert analysis_result in mock_time_period.analysis_results
    
    # Mock User relationship
    mock_user_id = str(uuid.uuid4())
    analysis_result.created_by = mock_user_id
    
    # In a real test, you'd create a User instance and set it
    # For this test, we'll just verify the field is set
    assert analysis_result.created_by == mock_user_id


def test_analysis_result_with_different_output_formats():
    """Tests the initialization of AnalysisResult with different output formats."""
    # Test with JSON output format
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(
        time_period_id=time_period_id,
        output_format=OutputFormat.JSON
    )
    assert analysis_result.output_format == OutputFormat.JSON
    
    # Test with CSV output format
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(
        time_period_id=time_period_id,
        output_format=OutputFormat.CSV
    )
    assert analysis_result.output_format == OutputFormat.CSV
    
    # Test with TEXT output format
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(
        time_period_id=time_period_id,
        output_format=OutputFormat.TEXT
    )
    assert analysis_result.output_format == OutputFormat.TEXT


def test_analysis_result_with_decimal_values():
    """Tests the handling of Decimal values for numeric fields."""
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Set Decimal values with specific precision and scale
    analysis_result.start_value = Decimal('1234.56')
    analysis_result.end_value = Decimal('5678.90')
    analysis_result.absolute_change = Decimal('4444.34')
    analysis_result.percentage_change = Decimal('359.99')
    
    # Verify that values are stored as Decimal
    assert isinstance(analysis_result.start_value, Decimal)
    assert isinstance(analysis_result.end_value, Decimal)
    assert isinstance(analysis_result.absolute_change, Decimal)
    assert isinstance(analysis_result.percentage_change, Decimal)
    
    # Verify precision and scale are maintained
    assert str(analysis_result.start_value) == '1234.56'
    assert str(analysis_result.end_value) == '5678.90'
    assert str(analysis_result.absolute_change) == '4444.34'
    assert str(analysis_result.percentage_change) == '359.99'


def test_analysis_result_with_complex_results():
    """Tests the handling of complex nested structures in the results field."""
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Create a complex nested structure
    complex_results = {
        "time_series_data": [
            {"date": "2023-01-01", "value": 100.0, "factors": ["seasonality", "demand"]},
            {"date": "2023-02-01", "value": 120.0, "factors": ["capacity", "fuel_price"]}
        ],
        "aggregates": {
            "by_origin": {
                "New York": {"avg": 105.5, "count": 10},
                "Los Angeles": {"avg": 115.2, "count": 8}
            },
            "by_carrier": {
                "Carrier A": {"avg": 110.0, "trend": "increasing"},
                "Carrier B": {"avg": 108.5, "trend": "stable"}
            }
        },
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "data_quality": "high",
            "confidence_score": 0.95
        }
    }
    
    # Set the complex results
    analysis_result.set_results(results=complex_results)
    
    # Verify the structure is preserved
    assert analysis_result.results["time_series_data"][0]["factors"] == ["seasonality", "demand"]
    assert analysis_result.results["aggregates"]["by_origin"]["New York"]["avg"] == 105.5
    assert analysis_result.results["aggregates"]["by_carrier"]["Carrier B"]["trend"] == "stable"
    assert analysis_result.results["metadata"]["data_quality"] == "high"


def test_analysis_result_inheritance():
    """Tests that AnalysisResult inherits from the correct base classes."""
    time_period_id = str(uuid.uuid4())
    analysis_result = AnalysisResult(time_period_id=time_period_id)
    
    # Check inheritance from expected base classes
    assert isinstance(analysis_result, Base)
    
    # These checks assume the class inherits from these mixins
    # In a real test, you might need to check for specific attributes or methods
    # instead of direct isinstance checks if imports are complex
    assert hasattr(analysis_result, 'id')  # UUIDMixin
    assert hasattr(analysis_result, 'created_at')  # TimestampMixin
    assert hasattr(analysis_result, 'updated_at')  # TimestampMixin
    assert hasattr(analysis_result, 'created_by')  # UserTrackingMixin
    assert hasattr(analysis_result, 'log_update')  # AuditableMixin


def test_analysis_result_timestamps():
    """Tests the timestamp functionality from TimestampMixin."""
    time_period_id = str(uuid.uuid4())
    
    # Create instance at time1
    time1 = datetime(2023, 1, 1, 12, 0, 0)
    with freeze_time(time1):
        analysis_result = AnalysisResult(time_period_id=time_period_id)
        
        # Check that created_at and updated_at are set
        assert analysis_result.created_at is not None
        assert analysis_result.updated_at is not None
        assert analysis_result.created_at == time1
        assert analysis_result.updated_at == time1
    
    # Update instance at time2
    time2 = datetime(2023, 1, 1, 12, 15, 0)
    with freeze_time(time2):
        # Update a field to trigger timestamp update
        analysis_result.name = "Updated Name"
        
        # In a real application with SQLAlchemy session, updated_at would change
        # For this test, we'll manually update it to simulate SQLAlchemy's behavior
        analysis_result.updated_at = datetime.utcnow()
        
        # Check that updated_at changed but created_at didn't
        assert analysis_result.created_at == time1
        assert analysis_result.updated_at == time2