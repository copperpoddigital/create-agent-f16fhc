#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility module for generating visualizations of freight price movement analysis results.

This module provides functions to create various chart types including line charts
for time series data, bar charts for comparisons, and trend indicators for
direction visualization.
"""

import typing
import base64
import io
from io import BytesIO
import datetime
import decimal
from decimal import Decimal

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..models.enums import TrendDirection
from .formatters import format_currency, format_percentage, format_trend, format_date
from ..core.logging import logger

# Global Constants
CHART_DPI = 100  # Resolution for generated chart images
CHART_COLORS = {  # Color scheme for charts
    'primary': '#1A5276',  # Deep Blue
    'secondary': '#148F77',  # Teal
    'increasing': '#27AE60',  # Green
    'decreasing': '#C0392B',  # Red
    'stable': '#F39C12',  # Amber
    'background': '#F8F9F9',  # Light Gray
    'text': '#2C3E50'  # Dark Gray
}
TREND_SYMBOLS = {
    TrendDirection.INCREASING: '↑',
    TrendDirection.DECREASING: '↓',
    TrendDirection.STABLE: '→'
}
DEFAULT_FIGURE_SIZE = (10, 6)  # Default size for chart figures in inches


def generate_line_chart(time_series: typing.List[typing.Dict[str, typing.Any]],
                       title: typing.Optional[str] = None,
                       value_key: typing.Optional[str] = 'value',
                       date_key: typing.Optional[str] = 'date',
                       currency_code: typing.Optional[str] = None,
                       figsize: typing.Optional[tuple] = None) -> typing.Dict[str, typing.Any]:
    """
    Generates a line chart for time series freight price data.
    
    Args:
        time_series: List of dictionaries containing time series data
        title: Chart title
        value_key: Dictionary key for the value field
        date_key: Dictionary key for the date field
        currency_code: Optional currency code for formatting
        figsize: Optional figure size tuple (width, height) in inches
        
    Returns:
        Dictionary with chart data including base64-encoded image
    """
    logger.info("Generating line chart for time series data")
    
    try:
        # Validate input
        if not time_series:
            logger.error("Cannot generate line chart: empty time series data")
            raise ValueError("Time series data cannot be empty")
        
        # Set default values if not provided
        chart_title = title or "Freight Price Movement"
        fig_size = figsize or DEFAULT_FIGURE_SIZE
        
        # Extract data
        dates = [item.get(date_key) for item in time_series]
        values = [float(item.get(value_key, 0)) for item in time_series]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Apply styling
        apply_chart_style(fig, ax)
        
        # Plot the data
        line = ax.plot(dates, values, marker='o', linestyle='-', color=CHART_COLORS['primary'], linewidth=2)
        
        # Format axes
        format_chart_labels(
            ax,
            x_label="Date",
            y_label=f"Price{f' ({currency_code})' if currency_code else ''}",
            title=chart_title,
            currency_code=currency_code
        )
        
        # Add annotations for key points
        add_data_annotations(ax, dates, values, currency_code=currency_code)
        
        # Convert to base64 image
        chart_image = encode_image_base64(fig)
        
        # Clean up
        plt.close(fig)
        
        return {
            "chart_type": "line",
            "title": chart_title,
            "data_points": len(time_series),
            "image": chart_image,
            "date_range": {
                "start": str(dates[0]) if dates else None,
                "end": str(dates[-1]) if dates else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating line chart: {str(e)}", exc_info=True)
        # Return a minimal result indicating the error
        return {
            "chart_type": "line",
            "error": str(e),
            "image": None
        }


def generate_bar_chart(data: typing.Dict[str, typing.Any],
                      title: typing.Optional[str] = None,
                      category_key: typing.Optional[str] = 'category',
                      value_key: typing.Optional[str] = 'value',
                      currency_code: typing.Optional[str] = None,
                      figsize: typing.Optional[tuple] = None) -> typing.Dict[str, typing.Any]:
    """
    Generates a bar chart for comparing freight prices across categories.
    
    Args:
        data: Dictionary containing categories and values
        title: Chart title
        category_key: Dictionary key for the category field
        value_key: Dictionary key for the value field
        currency_code: Optional currency code for formatting
        figsize: Optional figure size tuple (width, height) in inches
        
    Returns:
        Dictionary with chart data including base64-encoded image
    """
    logger.info("Generating bar chart for comparison data")
    
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            logger.error("Cannot generate bar chart: invalid data format")
            raise ValueError("Data must be a non-empty dictionary")
        
        # Process the data format - handle both list of dicts and dict of values
        if isinstance(data.get('data', []), list):
            # List of dictionaries format
            items = data.get('data', [])
            categories = [item.get(category_key, '') for item in items]
            values = [float(item.get(value_key, 0)) for item in items]
        else:
            # Direct dict format where keys are categories and values are values
            categories = list(data.keys())
            values = [float(data.get(key, 0)) for key in categories]
        
        # Set default values if not provided
        chart_title = title or "Freight Price Comparison"
        fig_size = figsize or DEFAULT_FIGURE_SIZE
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Apply styling
        apply_chart_style(fig, ax)
        
        # Plot the data
        bars = ax.bar(categories, values, color=CHART_COLORS['primary'], alpha=0.7)
        
        # Format axes
        format_chart_labels(
            ax,
            x_label="Category",
            y_label=f"Price{f' ({currency_code})' if currency_code else ''}",
            title=chart_title,
            currency_code=currency_code
        )
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            formatted_value = format_currency(Decimal(str(height)), currency_code) if currency_code else f"{height:.2f}"
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height * 1.01,
                formatted_value,
                ha='center', 
                va='bottom',
                fontsize=9,
                rotation=0,
                color=CHART_COLORS['text']
            )
        
        # Convert to base64 image
        chart_image = encode_image_base64(fig)
        
        # Clean up
        plt.close(fig)
        
        return {
            "chart_type": "bar",
            "title": chart_title,
            "data_points": len(categories),
            "image": chart_image,
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error generating bar chart: {str(e)}", exc_info=True)
        # Return a minimal result indicating the error
        return {
            "chart_type": "bar",
            "error": str(e),
            "image": None
        }


def generate_trend_indicator(trend: TrendDirection,
                           percentage_change: typing.Optional[decimal.Decimal] = None,
                           label: typing.Optional[str] = None,
                           figsize: typing.Optional[tuple] = None) -> typing.Dict[str, typing.Any]:
    """
    Generates a visual indicator for price movement trend direction.
    
    Args:
        trend: TrendDirection enum value
        percentage_change: Optional percentage change value
        label: Optional custom label
        figsize: Optional figure size tuple (width, height) in inches
        
    Returns:
        Dictionary with trend indicator data including base64-encoded image
    """
    logger.info(f"Generating trend indicator for direction: {trend}")
    
    try:
        # Validate input
        if not isinstance(trend, TrendDirection):
            logger.error(f"Invalid trend direction: {trend}")
            raise ValueError(f"Invalid trend direction: {trend}")
        
        # Define colors and symbols based on trend
        if trend == TrendDirection.INCREASING:
            color = CHART_COLORS['increasing']
            symbol = TREND_SYMBOLS[TrendDirection.INCREASING]
        elif trend == TrendDirection.DECREASING:
            color = CHART_COLORS['decreasing']
            symbol = TREND_SYMBOLS[TrendDirection.DECREASING]
        else:  # STABLE
            color = CHART_COLORS['stable']
            symbol = TREND_SYMBOLS[TrendDirection.STABLE]
        
        # Create a small figure for the indicator
        fig_size = figsize or (3, 3)
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Remove axes and set background
        ax.axis('off')
        fig.patch.set_facecolor(CHART_COLORS['background'])
        ax.patch.set_facecolor(CHART_COLORS['background'])
        
        # Add the trend symbol as text
        ax.text(0.5, 0.5, symbol, 
                fontsize=36, 
                ha='center', 
                va='center', 
                color=color,
                weight='bold')
        
        # Add percentage change if provided
        if percentage_change is not None:
            formatted_pct = format_percentage(percentage_change)
            ax.text(0.5, 0.25, formatted_pct, 
                    fontsize=18, 
                    ha='center', 
                    va='center', 
                    color=color)
        
        # Add label if provided
        if label:
            ax.text(0.5, 0.75, label, 
                    fontsize=14, 
                    ha='center', 
                    va='center', 
                    color=CHART_COLORS['text'])
        
        # Convert to base64 image
        chart_image = encode_image_base64(fig)
        
        # Clean up
        plt.close(fig)
        
        return {
            "chart_type": "trend_indicator",
            "trend": str(trend),
            "symbol": symbol,
            "percentage_change": str(percentage_change) if percentage_change is not None else None,
            "label": label,
            "image": chart_image
        }
        
    except Exception as e:
        logger.error(f"Error generating trend indicator: {str(e)}", exc_info=True)
        # Return a minimal result indicating the error
        return {
            "chart_type": "trend_indicator",
            "trend": str(trend) if isinstance(trend, TrendDirection) else None,
            "error": str(e),
            "image": None
        }


def generate_comparison_chart(base_time_series: typing.List[typing.Dict[str, typing.Any]],
                            comparison_time_series: typing.List[typing.Dict[str, typing.Any]],
                            title: typing.Optional[str] = None,
                            value_key: typing.Optional[str] = 'value',
                            date_key: typing.Optional[str] = 'date',
                            base_label: typing.Optional[str] = 'Base Period',
                            comparison_label: typing.Optional[str] = 'Comparison Period',
                            currency_code: typing.Optional[str] = None,
                            figsize: typing.Optional[tuple] = None) -> typing.Dict[str, typing.Any]:
    """
    Generates a chart comparing two time periods of freight price data.
    
    Args:
        base_time_series: List of dictionaries containing base period data
        comparison_time_series: List of dictionaries containing comparison period data
        title: Chart title
        value_key: Dictionary key for the value field
        date_key: Dictionary key for the date field
        base_label: Label for base period series
        comparison_label: Label for comparison period series
        currency_code: Optional currency code for formatting
        figsize: Optional figure size tuple (width, height) in inches
        
    Returns:
        Dictionary with comparison chart data including base64-encoded image
    """
    logger.info("Generating comparison chart for two time periods")
    
    try:
        # Validate input
        if not base_time_series or not comparison_time_series:
            logger.error("Cannot generate comparison chart: empty time series data")
            raise ValueError("Time series data cannot be empty")
        
        # Set default values if not provided
        chart_title = title or "Freight Price Comparison"
        fig_size = figsize or DEFAULT_FIGURE_SIZE
        
        # Extract data for base period
        base_dates = [item.get(date_key) for item in base_time_series]
        base_values = [float(item.get(value_key, 0)) for item in base_time_series]
        
        # Extract data for comparison period
        comp_dates = [item.get(date_key) for item in comparison_time_series]
        comp_values = [float(item.get(value_key, 0)) for item in comparison_time_series]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=fig_size)
        
        # Apply styling
        apply_chart_style(fig, ax)
        
        # Plot the data
        base_line = ax.plot(base_dates, base_values, marker='o', linestyle='-', 
                          color=CHART_COLORS['primary'], linewidth=2, 
                          label=base_label)
        
        comp_line = ax.plot(comp_dates, comp_values, marker='s', linestyle='--', 
                          color=CHART_COLORS['secondary'], linewidth=2, 
                          label=comparison_label)
        
        # Format axes
        format_chart_labels(
            ax,
            x_label="Date",
            y_label=f"Price{f' ({currency_code})' if currency_code else ''}",
            title=chart_title,
            currency_code=currency_code
        )
        
        # Add legend
        ax.legend(loc='best', frameon=True, facecolor=CHART_COLORS['background'])
        
        # Add annotations for significant differences
        significant_diffs = []
        if len(base_values) == len(comp_values):
            for i in range(len(base_values)):
                if abs(comp_values[i] - base_values[i]) / (base_values[i] if base_values[i] != 0 else 1) > 0.1:
                    significant_diffs.append((i, base_values[i], comp_values[i]))
        
        for idx, base_val, comp_val in significant_diffs[:3]:  # Limit to 3 annotations to avoid clutter
            ax.annotate(
                f"{format_percentage(Decimal(str((comp_val - base_val) / base_val if base_val != 0 else comp_val)))}",
                xy=(base_dates[idx], comp_val),
                xytext=(0, 10),
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=8,
                color=CHART_COLORS['secondary'],
                bbox=dict(boxstyle="round,pad=0.2", fc=CHART_COLORS['background'], alpha=0.8)
            )
        
        # Convert to base64 image
        chart_image = encode_image_base64(fig)
        
        # Clean up
        plt.close(fig)
        
        # Calculate some basic statistics for the result
        base_avg = sum(base_values) / len(base_values) if base_values else 0
        comp_avg = sum(comp_values) / len(comp_values) if comp_values else 0
        avg_change = comp_avg - base_avg
        pct_change = (avg_change / base_avg * 100) if base_avg else 0
        
        return {
            "chart_type": "comparison",
            "title": chart_title,
            "base_period": {
                "label": base_label,
                "data_points": len(base_time_series),
                "date_range": {
                    "start": str(base_dates[0]) if base_dates else None,
                    "end": str(base_dates[-1]) if base_dates else None
                }
            },
            "comparison_period": {
                "label": comparison_label,
                "data_points": len(comparison_time_series),
                "date_range": {
                    "start": str(comp_dates[0]) if comp_dates else None,
                    "end": str(comp_dates[-1]) if comp_dates else None
                }
            },
            "statistics": {
                "average_change": float(f"{avg_change:.2f}"),
                "percentage_change": float(f"{pct_change:.2f}")
            },
            "image": chart_image
        }
        
    except Exception as e:
        logger.error(f"Error generating comparison chart: {str(e)}", exc_info=True)
        # Return a minimal result indicating the error
        return {
            "chart_type": "comparison",
            "error": str(e),
            "image": None
        }


def encode_image_base64(fig: matplotlib.figure.Figure, 
                      format: typing.Optional[str] = 'png',
                      dpi: typing.Optional[int] = None) -> str:
    """
    Encodes a matplotlib figure as a base64 string.
    
    Args:
        fig: Matplotlib figure to encode
        format: Image format (png, jpg, svg, etc.)
        dpi: Resolution of the image
        
    Returns:
        Base64-encoded image string
    """
    try:
        buffer = BytesIO()
        fig.savefig(buffer, format=format, dpi=dpi or CHART_DPI, 
                   bbox_inches='tight', pad_inches=0.1, facecolor=CHART_COLORS['background'])
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode('utf-8')
        return image_data
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}", exc_info=True)
        return ""


def apply_chart_style(fig: matplotlib.figure.Figure, 
                    ax: matplotlib.axes.Axes,
                    style_overrides: typing.Optional[dict] = None) -> None:
    """
    Applies consistent styling to matplotlib charts.
    
    Args:
        fig: Matplotlib figure
        ax: Matplotlib axes
        style_overrides: Optional dictionary of style overrides
    """
    try:
        # Set background colors
        fig.patch.set_facecolor(CHART_COLORS['background'])
        ax.set_facecolor(CHART_COLORS['background'])
        
        # Set text color
        for text in ax.get_xticklabels() + ax.get_yticklabels():
            text.set_color(CHART_COLORS['text'])
        
        # Configure grid
        ax.grid(True, linestyle='--', alpha=0.3, color=CHART_COLORS['text'])
        
        # Configure ticks
        ax.tick_params(colors=CHART_COLORS['text'], direction='out')
        
        # Configure spines
        for spine in ax.spines.values():
            spine.set_color(CHART_COLORS['text'])
            spine.set_linewidth(0.5)
        
        # Apply any overrides
        if style_overrides and isinstance(style_overrides, dict):
            for key, value in style_overrides.items():
                if hasattr(ax, f"set_{key}"):
                    getattr(ax, f"set_{key}")(value)
    except Exception as e:
        logger.error(f"Error applying chart style: {str(e)}", exc_info=True)


def format_chart_labels(ax: matplotlib.axes.Axes,
                      x_label: typing.Optional[str] = None,
                      y_label: typing.Optional[str] = None,
                      title: typing.Optional[str] = None,
                      currency_code: typing.Optional[str] = None) -> None:
    """
    Formats axis labels and annotations for charts.
    
    Args:
        ax: Matplotlib axes
        x_label: Label for x-axis
        y_label: Label for y-axis
        title: Chart title
        currency_code: Optional currency code for formatting
    """
    try:
        # Set axis labels
        if x_label:
            ax.set_xlabel(x_label, color=CHART_COLORS['text'], fontsize=12)
        
        if y_label:
            ax.set_ylabel(y_label, color=CHART_COLORS['text'], fontsize=12)
        
        if title:
            ax.set_title(title, color=CHART_COLORS['text'], fontsize=14, fontweight='bold')
        
        # Format y-axis ticks with currency if specified
        if currency_code:
            from matplotlib.ticker import FuncFormatter
            
            def currency_formatter(x, pos):
                return format_currency(Decimal(str(x)), currency_code, include_symbol=True)
            
            ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        
        # Improve date formatting if x-axis contains dates
        if isinstance(ax.get_xticks()[0], (float, int)) and len(ax.get_xticks()) > 0:
            if hasattr(ax, 'xaxis') and hasattr(ax.xaxis, 'get_major_formatter'):
                formatter = ax.xaxis.get_major_formatter()
                if isinstance(formatter, plt.matplotlib.dates.DateFormatter):
                    # Already a date formatter, keep it
                    pass
                elif all(isinstance(x, datetime.datetime) or isinstance(x, datetime.date) for x in ax.get_lines()[0].get_xdata() if x is not None):
                    # X-axis has dates but no date formatter
                    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        
        # Make all labels look nice
        plt.tight_layout()
    except Exception as e:
        logger.error(f"Error formatting chart labels: {str(e)}", exc_info=True)


def add_data_annotations(ax: matplotlib.axes.Axes,
                       x_data: typing.List,
                       y_data: typing.List,
                       annotation_points: typing.Optional[dict] = None,
                       currency_code: typing.Optional[str] = None) -> None:
    """
    Adds annotations to highlight key data points on charts.
    
    Args:
        ax: Matplotlib axes
        x_data: X-axis data points
        y_data: Y-axis data points
        annotation_points: Optional dictionary specifying which points to annotate
        currency_code: Optional currency code for formatting
    """
    try:
        if not x_data or not y_data or len(x_data) != len(y_data):
            return
        
        # If annotation_points is not specified, create default annotations
        if annotation_points is None:
            # Default: annotate first, last, min, max points
            points_to_annotate = {}
            
            # First point
            points_to_annotate['first'] = (0, y_data[0])
            
            # Last point
            points_to_annotate['last'] = (len(y_data) - 1, y_data[-1])
            
            # Min point (excluding first and last if possible)
            if len(y_data) > 2:
                min_idx = np.argmin(y_data[1:-1]) + 1  # +1 to account for slicing
                points_to_annotate['min'] = (min_idx, y_data[min_idx])
            else:
                min_idx = np.argmin(y_data)
                points_to_annotate['min'] = (min_idx, y_data[min_idx])
            
            # Max point (excluding first and last if possible)
            if len(y_data) > 2:
                max_idx = np.argmax(y_data[1:-1]) + 1  # +1 to account for slicing
                points_to_annotate['max'] = (max_idx, y_data[max_idx])
            else:
                max_idx = np.argmax(y_data)
                points_to_annotate['max'] = (max_idx, y_data[max_idx])
        else:
            points_to_annotate = annotation_points
        
        # Add annotations for the specified points
        for label, (idx, value) in points_to_annotate.items():
            if 0 <= idx < len(x_data):
                x_val = x_data[idx]
                y_val = y_data[idx]
                
                formatted_value = format_currency(Decimal(str(y_val)), currency_code) if currency_code else f"{y_val:.2f}"
                
                ax.annotate(
                    formatted_value,
                    xy=(x_val, y_val),
                    xytext=(0, 10),  # 10 points vertical offset
                    textcoords="offset points",
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    color=CHART_COLORS['text'],
                    bbox=dict(boxstyle="round,pad=0.3", fc=CHART_COLORS['background'], alpha=0.8)
                )
    except Exception as e:
        logger.error(f"Error adding data annotations: {str(e)}", exc_info=True)