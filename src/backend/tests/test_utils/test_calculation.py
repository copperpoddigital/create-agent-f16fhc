import pytest
from decimal import Decimal

from ../../utils.calculation import (
    calculate_absolute_change, 
    calculate_percentage_change, 
    determine_trend_direction, 
    round_decimal, 
    validate_calculation_input, 
    TREND_THRESHOLD_PERCENT
)
from ../../models.enums import TrendDirection
from ../../core.exceptions import AnalysisException


def test_calculate_absolute_change():
    """Tests the calculate_absolute_change function with various inputs."""
    # Test with positive values
    result = calculate_absolute_change(Decimal('100'), Decimal('150'))
    assert result == Decimal('50')
    
    # Test with negative change
    result = calculate_absolute_change(Decimal('200'), Decimal('150'))
    assert result == Decimal('-50')
    
    # Test with zero start value
    result = calculate_absolute_change(Decimal('0'), Decimal('100'))
    assert result == Decimal('100')
    
    # Test with equal values
    result = calculate_absolute_change(Decimal('100'), Decimal('100'))
    assert result == Decimal('0')
    
    # Test with decimal values
    result = calculate_absolute_change(Decimal('100.50'), Decimal('150.75'))
    assert result == Decimal('50.25')


def test_calculate_absolute_change_with_none_values():
    """Tests that calculate_absolute_change raises AnalysisException when None values are provided."""
    # Test with None start_value
    with pytest.raises(AnalysisException):
        calculate_absolute_change(None, Decimal('100'))
    
    # Test with None end_value
    with pytest.raises(AnalysisException):
        calculate_absolute_change(Decimal('100'), None)
    
    # Test with both None values
    with pytest.raises(AnalysisException):
        calculate_absolute_change(None, None)


def test_calculate_percentage_change():
    """Tests the calculate_percentage_change function with various inputs."""
    # Test with positive change
    result = calculate_percentage_change(Decimal('100'), Decimal('150'))
    assert result == Decimal('50')
    
    # Test with negative change
    result = calculate_percentage_change(Decimal('200'), Decimal('150'))
    assert result == Decimal('-25')
    
    # Test with zero change
    result = calculate_percentage_change(Decimal('100'), Decimal('100'))
    assert result == Decimal('0')
    
    # Test with decimal values
    result = calculate_percentage_change(Decimal('100.50'), Decimal('150.75'))
    assert result == Decimal('50')  # Rounded appropriately


def test_calculate_percentage_change_edge_cases():
    """Tests the calculate_percentage_change function with edge cases."""
    # Test with zero start_value and positive end_value
    result = calculate_percentage_change(Decimal('0'), Decimal('100'))
    # Special case for "new rate established"
    assert result == Decimal('9999.9999')
    
    # Test with zero start_value and zero end_value
    result = calculate_percentage_change(Decimal('0'), Decimal('0'))
    assert result == Decimal('0')  # No change
    
    # Test with positive start_value and zero end_value
    result = calculate_percentage_change(Decimal('100'), Decimal('0'))
    assert result == Decimal('-100')  # 100% decrease
    
    # Test with very large percentage changes
    result = calculate_percentage_change(Decimal('1'), Decimal('1000'))
    assert result == Decimal('99900')  # 99,900% increase


def test_calculate_percentage_change_with_none_values():
    """Tests that calculate_percentage_change raises AnalysisException when None values are provided."""
    # Test with None start_value
    with pytest.raises(AnalysisException):
        calculate_percentage_change(None, Decimal('100'))
    
    # Test with None end_value
    with pytest.raises(AnalysisException):
        calculate_percentage_change(Decimal('100'), None)
    
    # Test with both None values
    with pytest.raises(AnalysisException):
        calculate_percentage_change(None, None)


def test_determine_trend_direction():
    """Tests the determine_trend_direction function with various percentage changes."""
    # Test with percentage change > TREND_THRESHOLD_PERCENT (increasing)
    result = determine_trend_direction(Decimal('5.0'))
    assert result == TrendDirection.INCREASING
    
    # Test with percentage change < -TREND_THRESHOLD_PERCENT (decreasing)
    result = determine_trend_direction(Decimal('-5.0'))
    assert result == TrendDirection.DECREASING
    
    # Test with percentage change between -TREND_THRESHOLD_PERCENT and TREND_THRESHOLD_PERCENT (stable)
    result = determine_trend_direction(Decimal('0.5'))
    assert result == TrendDirection.STABLE
    
    # Test with percentage change exactly equal to TREND_THRESHOLD_PERCENT
    result = determine_trend_direction(TREND_THRESHOLD_PERCENT)
    assert result == TrendDirection.STABLE
    
    # Test with percentage change exactly equal to -TREND_THRESHOLD_PERCENT
    result = determine_trend_direction(-TREND_THRESHOLD_PERCENT)
    assert result == TrendDirection.STABLE


def test_determine_trend_direction_with_none_value():
    """Tests that determine_trend_direction raises AnalysisException when None value is provided."""
    with pytest.raises(AnalysisException):
        determine_trend_direction(None)


def test_round_decimal():
    """Tests the round_decimal function with various inputs."""
    # Test rounding to 2 decimal places
    result = round_decimal(Decimal('123.456'), 2)
    assert result == Decimal('123.46')
    
    # Test rounding to 0 decimal places
    result = round_decimal(Decimal('123.456'), 0)
    assert result == Decimal('123')
    
    # Test rounding to 4 decimal places
    result = round_decimal(Decimal('123.456789'), 4)
    assert result == Decimal('123.4568')
    
    # Test rounding with negative numbers
    result = round_decimal(Decimal('-123.456'), 2)
    assert result == Decimal('-123.46')


def test_round_decimal_with_none_value():
    """Tests that round_decimal raises AnalysisException when None value is provided."""
    with pytest.raises(AnalysisException):
        round_decimal(None, 2)


def test_validate_calculation_input():
    """Tests the validate_calculation_input function with various inputs."""
    # Test with valid Decimal value
    result = validate_calculation_input(Decimal('123.45'))
    assert isinstance(result, Decimal)
    assert result == Decimal('123.45')
    
    # Test with valid integer value
    result = validate_calculation_input(123)
    assert isinstance(result, Decimal)
    assert result == Decimal('123')
    
    # Test with valid float value
    result = validate_calculation_input(123.45)
    assert isinstance(result, Decimal)
    assert result == Decimal('123.45')
    
    # Test with valid string value representing a number
    result = validate_calculation_input('123.45')
    assert isinstance(result, Decimal)
    assert result == Decimal('123.45')
    
    # Test with None value
    with pytest.raises(AnalysisException):
        validate_calculation_input(None)
    
    # Test with non-numeric string
    with pytest.raises(AnalysisException):
        validate_calculation_input('not a number')


@pytest.mark.parametrize('start_value, end_value, expected_result', [
    (Decimal('100'), Decimal('150'), Decimal('50')),
    (Decimal('200'), Decimal('150'), Decimal('-50')),
    (Decimal('0'), Decimal('100'), Decimal('100')),
    (Decimal('100'), Decimal('0'), Decimal('-100')),
    (Decimal('100'), Decimal('100'), Decimal('0')),
    (Decimal('100.50'), Decimal('150.75'), Decimal('50.25')),
])
def test_parameterized_absolute_change(start_value, end_value, expected_result):
    """Parameterized test for calculate_absolute_change with multiple test cases."""
    result = calculate_absolute_change(start_value, end_value)
    assert result == expected_result


@pytest.mark.parametrize('start_value, end_value, expected_result', [
    (Decimal('100'), Decimal('150'), Decimal('50')),
    (Decimal('200'), Decimal('150'), Decimal('-25')),
    (Decimal('100'), Decimal('100'), Decimal('0')),
    (Decimal('100'), Decimal('0'), Decimal('-100')),
    (Decimal('0'), Decimal('100'), Decimal('9999.9999')),  # Special case
    (Decimal('0'), Decimal('0'), Decimal('0')),
])
def test_parameterized_percentage_change(start_value, end_value, expected_result):
    """Parameterized test for calculate_percentage_change with multiple test cases."""
    result = calculate_percentage_change(start_value, end_value)
    assert result == expected_result


@pytest.mark.parametrize('percentage_change, expected_result', [
    (Decimal('5.0'), TrendDirection.INCREASING),
    (Decimal('-5.0'), TrendDirection.DECREASING),
    (Decimal('0.5'), TrendDirection.STABLE),
    (Decimal('0'), TrendDirection.STABLE),
    (TREND_THRESHOLD_PERCENT, TrendDirection.STABLE),
    (-TREND_THRESHOLD_PERCENT, TrendDirection.STABLE),
])
def test_parameterized_trend_direction(percentage_change, expected_result):
    """Parameterized test for determine_trend_direction with multiple test cases."""
    result = determine_trend_direction(percentage_change)
    assert result == expected_result