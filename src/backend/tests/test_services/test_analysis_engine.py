"""
Unit and integration tests for the Analysis Engine service, which is responsible for calculating freight price movements across time periods. This test file verifies the accuracy of calculations, caching behavior, and error handling in the analysis engine.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
import uuid

from ../../services.analysis_engine import (
    AnalysisEngine, get_cached_analysis, cache_analysis_result
)
from ../../utils.calculation import (
    calculate_absolute_change, calculate_percentage_change, determine_trend_direction
)
from ../../core.exceptions import AnalysisException
from ../../core.cache import cache_manager
from ../../models.freight_data import FreightData
from ../../models.time_period import TimePeriod
from ../../models.analysis_result import AnalysisResult
from ../../models.enums import (
    TrendDirection, AnalysisStatus, OutputFormat, GranularityType, TransportMode
)


def test_calculate_absolute_change():
    """Tests the calculate_absolute_change function with various inputs."""
    # Test with positive change (end > start)
    assert calculate_absolute_change(Decimal('100'), Decimal('150')) == Decimal('50')
    
    # Test with negative change (end < start)
    assert calculate_absolute_change(Decimal('150'), Decimal('100')) == Decimal('-50')
    
    # Test with no change (end = start)
    assert calculate_absolute_change(Decimal('100'), Decimal('100')) == Decimal('0')
    
    # Test with zero start value
    assert calculate_absolute_change(Decimal('0'), Decimal('100')) == Decimal('100')
    
    # Test with zero end value
    assert calculate_absolute_change(Decimal('100'), Decimal('0')) == Decimal('-100')
    
    # Test with large values
    assert calculate_absolute_change(Decimal('1000000'), Decimal('1000001')) == Decimal('1')


def test_calculate_percentage_change():
    """Tests the calculate_percentage_change function with various inputs."""
    # Test with positive change (end > start)
    assert calculate_percentage_change(Decimal('100'), Decimal('150')) == Decimal('50')
    
    # Test with negative change (end < start)
    assert calculate_percentage_change(Decimal('150'), Decimal('100')) == Decimal('-33.3333')
    
    # Test with no change (end = start)
    assert calculate_percentage_change(Decimal('100'), Decimal('100')) == Decimal('0')
    
    # Test with zero start value and positive end value
    result = calculate_percentage_change(Decimal('0'), Decimal('100'))
    assert result == Decimal('9999.9999')  # Special case indicating new rate established
    
    # Test with zero start value and zero end value
    assert calculate_percentage_change(Decimal('0'), Decimal('0')) == Decimal('0')
    
    # Test with positive start value and zero end value
    assert calculate_percentage_change(Decimal('100'), Decimal('0')) == Decimal('-100')


def test_determine_trend_direction():
    """Tests the determine_trend_direction function with various inputs."""
    # Test with percentage change > threshold (should return INCREASING)
    assert determine_trend_direction(Decimal('5')) == TrendDirection.INCREASING
    
    # Test with percentage change < -threshold (should return DECREASING)
    assert determine_trend_direction(Decimal('-5')) == TrendDirection.DECREASING
    
    # Test with percentage change between -threshold and threshold (should return STABLE)
    assert determine_trend_direction(Decimal('0.5')) == TrendDirection.STABLE
    assert determine_trend_direction(Decimal('-0.5')) == TrendDirection.STABLE
    
    # Test with percentage change exactly at threshold (should return INCREASING)
    assert determine_trend_direction(Decimal('1')) == TrendDirection.INCREASING
    
    # Test with percentage change exactly at -threshold (should return DECREASING)
    assert determine_trend_direction(Decimal('-1')) == TrendDirection.DECREASING
    
    # Test with zero percentage change (should return STABLE)
    assert determine_trend_direction(Decimal('0')) == TrendDirection.STABLE


def test_analyze_price_movement(db_session):
    """Tests the analyze_price_movement method of AnalysisEngine."""
    # Create test time period
    time_period = TimePeriod(
        name="Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data spanning the time period
    start_date = time_period.start_date
    freight_data = []
    for i in range(10):
        record_date = start_date + timedelta(days=i*3)
        freight_data.append(FreightData(
            record_date=record_date,
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,  # Increasing price trend
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Perform analysis
    result, cache_hit = engine.analyze_price_movement(time_period.id)
    
    # Verify the result
    assert result is not None
    assert result.status == AnalysisStatus.COMPLETED
    assert not cache_hit
    
    # Check that the calculated values are correct
    result_dict = result.to_dict(include_details=True)
    assert 'absolute_change' in result_dict
    assert 'percentage_change' in result_dict
    assert 'trend_direction' in result_dict
    
    # Verify trend direction is INCREASING since we created increasing prices
    assert result_dict['trend_direction'] == TrendDirection.INCREASING.name


def test_analyze_price_movement_with_filters(db_session):
    """Tests the analyze_price_movement method with various filters."""
    # Create test time period
    time_period = TimePeriod(
        name="Filter Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create origins, destinations, and carriers
    origin1_id = str(uuid.uuid4())
    origin2_id = str(uuid.uuid4())
    dest1_id = str(uuid.uuid4())
    dest2_id = str(uuid.uuid4())
    carrier1_id = str(uuid.uuid4())
    carrier2_id = str(uuid.uuid4())
    
    # Create test freight data with different origins, destinations, and carriers
    start_date = time_period.start_date
    freight_data = []
    
    # Data for origin1, dest1, carrier1, OCEAN
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=origin1_id,
            destination_id=dest1_id,
            carrier_id=carrier1_id,
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    # Data for origin2, dest2, carrier2, AIR
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=origin2_id,
            destination_id=dest2_id,
            carrier_id=carrier2_id,
            freight_charge=2000 + i*100,  # Higher price, steeper increase
            transport_mode=TransportMode.AIR,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Test filter by origin
    origin_filter = {"origin_ids": [origin1_id]}
    result_origin, _ = engine.analyze_price_movement(time_period.id, filters=origin_filter)
    result_dict = result_origin.to_dict(include_details=True)
    # Verify that only origin1 data is included
    assert result_dict['start_value'] < 1500  # Should be around 1000, not 2000
    
    # Test filter by carrier
    carrier_filter = {"carrier_ids": [carrier2_id]}
    result_carrier, _ = engine.analyze_price_movement(time_period.id, filters=carrier_filter)
    result_dict = result_carrier.to_dict(include_details=True)
    # Verify that only carrier2 data is included
    assert result_dict['start_value'] > 1500  # Should be around 2000, not 1000
    
    # Test filter by transport mode
    mode_filter = {"transport_modes": [TransportMode.AIR]}
    result_mode, _ = engine.analyze_price_movement(time_period.id, filters=mode_filter)
    result_dict = result_mode.to_dict(include_details=True)
    # Verify that only AIR data is included
    assert result_dict['start_value'] > 1500  # Should be around 2000, not 1000
    
    # Test multiple filters
    combined_filter = {
        "origin_ids": [origin1_id],
        "carrier_ids": [carrier1_id],
        "transport_modes": [TransportMode.OCEAN]
    }
    result_combined, _ = engine.analyze_price_movement(time_period.id, filters=combined_filter)
    result_dict = result_combined.to_dict(include_details=True)
    # Verify that only matching data is included
    assert result_dict['start_value'] < 1500  # Should be around 1000


def test_analyze_price_movement_with_empty_data(db_session):
    """Tests the analyze_price_movement method with no matching data."""
    # Create test time period
    time_period = TimePeriod(
        name="Empty Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Test with filters that won't match any data
    non_existent_id = str(uuid.uuid4())
    filter_no_match = {"origin_ids": [non_existent_id]}
    
    # Analyze with filters that won't match any data
    result, _ = engine.analyze_price_movement(time_period.id, filters=filter_no_match)
    
    # Verify that the analysis fails with appropriate message
    assert result.status == AnalysisStatus.FAILED
    assert "No freight data available" in result.error_message


def test_analyze_price_movement_with_invalid_time_period(db_session):
    """Tests the analyze_price_movement method with an invalid time period ID."""
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Use a non-existent time period ID
    non_existent_id = str(uuid.uuid4())
    
    # Analyze with non-existent time period
    result, _ = engine.analyze_price_movement(non_existent_id)
    
    # Verify that the analysis fails with appropriate message
    assert result.status == AnalysisStatus.FAILED
    assert "Time period not found" in result.error_message


def test_calculate_price_movement(db_session):
    """Tests the calculate_price_movement method directly."""
    # Create test time period
    time_period = TimePeriod(
        name="Calculation Test Period",
        start_date=datetime.now() - timedelta(days=10),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    
    # Create test freight data with known values
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*2),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*100,  # 1000, 1100, 1200, 1300, 1400
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Calculate price movement
    results = engine.calculate_price_movement(freight_data, time_period)
    
    # Verify results contain expected fields
    assert 'start_value' in results
    assert 'end_value' in results
    assert 'absolute_change' in results
    assert 'percentage_change' in results
    assert 'trend_direction' in results
    assert 'time_series' in results
    
    # Verify the calculated values match expected
    assert results['start_value'] == 1000.0
    assert results['end_value'] == 1400.0
    assert results['absolute_change'] == 400.0
    assert results['percentage_change'] == 40.0
    assert results['trend_direction'] == TrendDirection.INCREASING.name
    
    # Verify time series data is generated correctly
    assert len(results['time_series']) > 0


def test_get_analysis_result(db_session):
    """Tests the get_analysis_result method."""
    # Create test time period
    time_period = TimePeriod(
        name="Get Result Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Perform analysis to create a result
    analysis_result, _ = engine.analyze_price_movement(time_period.id)
    
    # Get the analysis result by ID
    retrieved_result = engine.get_analysis_result(analysis_result.id)
    
    # Verify the result was retrieved correctly
    assert retrieved_result is not None
    assert retrieved_result.id == analysis_result.id
    assert retrieved_result.time_period_id == time_period.id
    assert retrieved_result.status == AnalysisStatus.COMPLETED
    
    # Try to get a non-existent result
    non_existent_id = str(uuid.uuid4())
    non_existent_result = engine.get_analysis_result(non_existent_id)
    
    # Verify that None is returned for non-existent ID
    assert non_existent_result is None


def test_delete_analysis_result(db_session):
    """Tests the delete_analysis_result method."""
    # Create test time period
    time_period = TimePeriod(
        name="Delete Result Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Perform analysis to create a result
    analysis_result, _ = engine.analyze_price_movement(time_period.id)
    
    # Delete the analysis result
    deletion_success = engine.delete_analysis_result(analysis_result.id)
    
    # Verify the deletion was successful
    assert deletion_success is True
    
    # Try to get the deleted result
    deleted_result = engine.get_analysis_result(analysis_result.id)
    
    # Verify that the result no longer exists
    assert deleted_result is None
    
    # Try to delete a non-existent result
    non_existent_id = str(uuid.uuid4())
    non_existent_deletion = engine.delete_analysis_result(non_existent_id)
    
    # Verify that False is returned for non-existent ID
    assert non_existent_deletion is False


def test_rerun_analysis(db_session):
    """Tests the rerun_analysis method."""
    # Create test time period
    time_period = TimePeriod(
        name="Rerun Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,  # Increasing prices
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Perform first analysis
    initial_result, _ = engine.analyze_price_movement(time_period.id)
    initial_values = initial_result.to_dict(include_details=True)
    
    # Add more freight data with different trend
    additional_data = []
    for i in range(5):
        additional_data.append(FreightData(
            record_date=start_date + timedelta(days=15+i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1300 - i*50,  # Decreasing prices
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(additional_data)
    db_session.commit()
    
    # Rerun the analysis
    updated_result = engine.rerun_analysis(initial_result.id, use_cache=False)
    updated_values = updated_result.to_dict(include_details=True)
    
    # Verify that the results have changed
    assert updated_values['percentage_change'] != initial_values['percentage_change']
    
    # Try to rerun a non-existent analysis
    non_existent_id = str(uuid.uuid4())
    non_existent_rerun = engine.rerun_analysis(non_existent_id)
    
    # Verify that None is returned for non-existent ID
    assert non_existent_rerun is None


def test_compare_time_periods(db_session):
    """Tests the compare_time_periods method."""
    # Create two test time periods (base and comparison)
    base_period = TimePeriod(
        name="Base Period",
        start_date=datetime.now() - timedelta(days=60),
        end_date=datetime.now() - timedelta(days=30),
        granularity=GranularityType.DAILY
    )
    comparison_period = TimePeriod(
        name="Comparison Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(base_period)
    db_session.add(comparison_period)
    db_session.flush()
    
    # Create common origin, destination, carrier for consistent comparison
    origin_id = str(uuid.uuid4())
    destination_id = str(uuid.uuid4())
    carrier_id = str(uuid.uuid4())
    
    # Create test freight data for base period
    base_start_date = base_period.start_date
    base_freight_data = []
    for i in range(5):
        base_freight_data.append(FreightData(
            record_date=base_start_date + timedelta(days=i*3),
            origin_id=origin_id,
            destination_id=destination_id,
            carrier_id=carrier_id,
            freight_charge=1000 + i*50,  # 1000 to 1200
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    # Create test freight data for comparison period
    comp_start_date = comparison_period.start_date
    comp_freight_data = []
    for i in range(5):
        comp_freight_data.append(FreightData(
            record_date=comp_start_date + timedelta(days=i*3),
            origin_id=origin_id,
            destination_id=destination_id,
            carrier_id=carrier_id,
            freight_charge=1300 + i*50,  # 1300 to 1500 (higher than base period)
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(base_freight_data)
    db_session.add_all(comp_freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Compare the time periods
    comparison_results = engine.compare_time_periods(base_period.id, comparison_period.id)
    
    # Verify the comparison results
    assert comparison_results is not None
    assert 'base_period' in comparison_results
    assert 'comparison_period' in comparison_results
    assert 'difference' in comparison_results
    
    # The comparison period values should be higher
    assert comparison_results['comparison_period']['value'] > comparison_results['base_period']['value']
    
    # The difference should be positive and the trend should be INCREASING
    assert comparison_results['difference']['absolute'] > 0
    assert comparison_results['difference']['percentage'] > 0
    assert comparison_results['difference']['trend_direction'] == TrendDirection.INCREASING.name


def test_caching_behavior(db_session):
    """Tests the caching behavior of the analysis engine."""
    # Create test time period
    time_period = TimePeriod(
        name="Cache Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # First analysis with caching enabled
    result1, cache_hit1 = engine.analyze_price_movement(time_period.id, use_cache=True)
    
    # Verify first analysis wasn't from cache
    assert not cache_hit1
    
    # Second analysis with caching enabled should use cache
    result2, cache_hit2 = engine.analyze_price_movement(time_period.id, use_cache=True)
    
    # Verify second analysis was from cache
    assert cache_hit2
    
    # Analysis with caching disabled should not use cache
    result3, cache_hit3 = engine.analyze_price_movement(time_period.id, use_cache=False)
    
    # Verify third analysis wasn't from cache
    assert not cache_hit3
    
    # Invalidate cache
    engine.invalidate_cache(result1.id)
    
    # Analysis after invalidation should not use cache
    result4, cache_hit4 = engine.analyze_price_movement(time_period.id, use_cache=True)
    
    # Verify fourth analysis wasn't from cache
    assert not cache_hit4


def test_cache_expiry(db_session):
    """Tests the cache expiry functionality."""
    # Create test time period
    time_period = TimePeriod(
        name="Cache Expiry Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # First analysis with caching enabled
    result1, cache_hit1 = engine.analyze_price_movement(time_period.id, use_cache=True)
    
    # Verify first analysis wasn't from cache
    assert not cache_hit1
    
    # Mock datetime.now to return a future time beyond cache expiry
    with patch('datetime.datetime') as mock_datetime:
        # Set current time to 2 hours in the future (beyond default cache TTL)
        future_time = datetime.now() + timedelta(hours=2)
        mock_datetime.utcnow.return_value = future_time
        mock_datetime.now.return_value = future_time
        
        # Analysis after cache expiry should not use cache
        result2, cache_hit2 = engine.analyze_price_movement(time_period.id, use_cache=True)
        
        # Verify second analysis wasn't from cache due to expiry
        assert not cache_hit2


def test_different_output_formats(db_session):
    """Tests the analysis with different output formats."""
    # Create test time period
    time_period = TimePeriod(
        name="Format Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.flush()
    
    # Create test freight data
    start_date = time_period.start_date
    freight_data = []
    for i in range(5):
        freight_data.append(FreightData(
            record_date=start_date + timedelta(days=i*3),
            origin_id=str(uuid.uuid4()),
            destination_id=str(uuid.uuid4()),
            carrier_id=str(uuid.uuid4()),
            freight_charge=1000 + i*50,
            transport_mode=TransportMode.OCEAN,
            currency_code="USD"
        ))
    
    db_session.add_all(freight_data)
    db_session.commit()
    
    # Initialize analysis engine
    engine = AnalysisEngine()
    
    # Test JSON output format (default)
    result_json, _ = engine.analyze_price_movement(time_period.id, output_format=OutputFormat.JSON)
    assert result_json.output_format == OutputFormat.JSON
    
    # Test CSV output format
    result_csv, _ = engine.analyze_price_movement(time_period.id, output_format=OutputFormat.CSV)
    assert result_csv.output_format == OutputFormat.CSV
    
    # Test TEXT output format
    result_text, _ = engine.analyze_price_movement(time_period.id, output_format=OutputFormat.TEXT)
    assert result_text.output_format == OutputFormat.TEXT


def test_error_handling(db_session):
    """Tests error handling in the analysis engine."""
    # Create test time period
    time_period = TimePeriod(
        name="Error Test Period",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        granularity=GranularityType.DAILY
    )
    db_session.add(time_period)
    db_session.commit()
    
    # Mock FreightData.get_for_analysis to raise an exception
    with patch('../../models.freight_data.FreightData.get_for_analysis') as mock_get:
        mock_get.side_effect = Exception("Test exception")
        
        # Initialize analysis engine
        engine = AnalysisEngine()
        
        # Analyze with the mocked error condition
        result, _ = engine.analyze_price_movement(time_period.id)
        
        # Verify that the analysis fails with appropriate message
        assert result.status == AnalysisStatus.FAILED
        assert "Test exception" in result.error_message


class TestAnalysisEngine:
    """Test class for the AnalysisEngine service"""
    
    def setup_method(self, method):
        """Setup method that runs before each test"""
        self.engine = AnalysisEngine()
    
    def teardown_method(self, method):
        """Teardown method that runs after each test"""
        # Clean up any resources or mocks
        pass
    
    def test_analyze_price_movement(self, db_session):
        """Tests the analyze_price_movement method"""
        # Create test time period
        time_period = TimePeriod(
            name="Class Test Period",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            granularity=GranularityType.DAILY
        )
        db_session.add(time_period)
        db_session.flush()
        
        # Create test freight data
        start_date = time_period.start_date
        freight_data = []
        for i in range(5):
            freight_data.append(FreightData(
                record_date=start_date + timedelta(days=i*3),
                origin_id=str(uuid.uuid4()),
                destination_id=str(uuid.uuid4()),
                carrier_id=str(uuid.uuid4()),
                freight_charge=1000 + i*50,
                transport_mode=TransportMode.OCEAN,
                currency_code="USD"
            ))
        
        db_session.add_all(freight_data)
        db_session.commit()
        
        # Perform analysis
        result, cache_hit = self.engine.analyze_price_movement(time_period.id)
        
        # Verify results
        assert result is not None
        assert result.status == AnalysisStatus.COMPLETED
        assert not cache_hit
    
    def test_calculate_price_movement(self, db_session):
        """Tests the calculate_price_movement method"""
        # Create test time period
        time_period = TimePeriod(
            name="Class Calc Test Period",
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now(),
            granularity=GranularityType.DAILY
        )
        
        # Create test freight data with known values
        start_date = time_period.start_date
        freight_data = []
        for i in range(5):
            freight_data.append(FreightData(
                record_date=start_date + timedelta(days=i*2),
                origin_id=str(uuid.uuid4()),
                destination_id=str(uuid.uuid4()),
                carrier_id=str(uuid.uuid4()),
                freight_charge=1000 + i*100,
                transport_mode=TransportMode.OCEAN,
                currency_code="USD"
            ))
        
        # Calculate price movement
        results = self.engine.calculate_price_movement(freight_data, time_period)
        
        # Verify results
        assert results['start_value'] == 1000.0
        assert results['end_value'] == 1400.0
        assert results['absolute_change'] == 400.0
        assert results['percentage_change'] == 40.0
        assert results['trend_direction'] == TrendDirection.INCREASING.name
    
    def test_caching_behavior(self, db_session):
        """Tests the caching behavior"""
        # Create test time period
        time_period = TimePeriod(
            name="Class Cache Test Period",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            granularity=GranularityType.DAILY
        )
        db_session.add(time_period)
        db_session.flush()
        
        # Create test freight data
        start_date = time_period.start_date
        freight_data = []
        for i in range(5):
            freight_data.append(FreightData(
                record_date=start_date + timedelta(days=i*3),
                origin_id=str(uuid.uuid4()),
                destination_id=str(uuid.uuid4()),
                carrier_id=str(uuid.uuid4()),
                freight_charge=1000 + i*50,
                transport_mode=TransportMode.OCEAN,
                currency_code="USD"
            ))
        
        db_session.add_all(freight_data)
        db_session.commit()
        
        # First analysis
        result1, cache_hit1 = self.engine.analyze_price_movement(time_period.id, use_cache=True)
        assert not cache_hit1
        
        # Second analysis should use cache
        result2, cache_hit2 = self.engine.analyze_price_movement(time_period.id, use_cache=True)
        assert cache_hit2
        
        # Invalidate cache
        self.engine.invalidate_cache(result1.id)
        
        # Third analysis should not use cache
        result3, cache_hit3 = self.engine.analyze_price_movement(time_period.id, use_cache=True)
        assert not cache_hit3