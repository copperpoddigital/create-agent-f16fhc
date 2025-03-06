"""
Service responsible for formatting and delivering analysis results in various output formats.
This module transforms raw analysis data into user-friendly presentations including JSON, CSV, and text summaries with optional visualizations.
"""

import logging
import typing
import json
import csv  # version: standard library
import io  # version: standard library
from io import StringIO
import decimal
import datetime
import pandas  # version: ^1.5.0

from .analysis_engine import AnalysisEngine
from ..models.analysis_result import AnalysisResult
from ..models.enums import OutputFormat, TrendDirection
from ..core.exceptions import PresentationException
from ..utils.formatters import format_currency, format_percentage, format_trend, format_date_range, format_time_period, format_json_value
from ..utils.visualization import generate_line_chart, generate_bar_chart, generate_trend_indicator, generate_comparison_chart
from ..schemas.responses import PriceMovementResponse

# Initialize logger
logger = logging.getLogger(__name__)


def format_json_output(analysis_result: AnalysisResult, pretty_print: typing.Optional[bool] = False) -> str:
    """
    Formats analysis results as JSON.

    Args:
        analysis_result: Analysis result object
        pretty_print: Whether to format with indentation for readability

    Returns:
        JSON-formatted analysis results
    """
    logger.info(f"Formatting analysis result {analysis_result.id} as JSON")
    try:
        # Extract result data from analysis_result
        result_data = analysis_result.to_dict(include_details=True)

        # Convert any non-JSON-serializable values using format_json_value
        def recursive_format(obj):
            if isinstance(obj, dict):
                return {k: format_json_value(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [format_json_value(item) for item in obj]
            else:
                return format_json_value(obj)

        structured_data = recursive_format(result_data)

        # If pretty_print is True, format with indentation
        indent = 4 if pretty_print else None

        # Serialize the structured data to a JSON string
        json_string = json.dumps(structured_data, indent=indent)

        # Return the JSON string
        return json_string

    except Exception as e:
        logger.error(f"Error formatting analysis result {analysis_result.id} as JSON: {e}", exc_info=True)
        raise PresentationException(f"Failed to format analysis result {analysis_result.id} as JSON: {e}", original_exception=e)


def format_csv_output(analysis_result: AnalysisResult) -> str:
    """
    Formats analysis results as CSV.

    Args:
        analysis_result: Analysis result object

    Returns:
        CSV-formatted analysis results
    """
    logger.info(f"Formatting analysis result {analysis_result.id} as CSV")
    try:
        # Extract result data from analysis_result
        result_data = analysis_result.to_dict(include_details=True)

        # Create a StringIO object for CSV writing
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # Determine the appropriate CSV structure based on the analysis type
        if 'time_series' in result_data and result_data['time_series']:
            # Time series data
            header = ['start_date', 'end_date', 'average_freight_charge', 'min_freight_charge', 'max_freight_charge', 'count']
            writer.writerow(header)

            # For time series data, write each time period as a row
            for period in result_data['results']['time_series']:
                row = [
                    period.get('start_date'),
                    period.get('end_date'),
                    period.get('average_freight_charge'),
                    period.get('min_freight_charge'),
                    period.get('max_freight_charge'),
                    period.get('count')
                ]
                writer.writerow(row)
        else:
            # Summary data
            header = ['start_value', 'end_value', 'absolute_change', 'percentage_change', 'trend_direction']
            writer.writerow(header)
            row = [
                result_data.get('start_value'),
                result_data.get('end_value'),
                result_data.get('absolute_change'),
                result_data.get('percentage_change'),
                result_data.get('trend_direction')
            ]
            writer.writerow(row)

        # Return the CSV string from the StringIO object
        csv_string = csv_buffer.getvalue()
        return csv_string

    except Exception as e:
        logger.error(f"Error formatting analysis result {analysis_result.id} as CSV: {e}", exc_info=True)
        raise PresentationException(f"Failed to format analysis result {analysis_result.id} as CSV: {e}", original_exception=e)


def format_text_output(analysis_result: AnalysisResult) -> str:
    """
    Formats analysis results as human-readable text.

    Args:
        analysis_result: Analysis result object

    Returns:
        Text-formatted analysis results
    """
    logger.info(f"Formatting analysis result {analysis_result.id} as text")
    try:
        # Extract result data from analysis_result
        result_data = analysis_result.to_dict(include_details=True)

        # Extract relevant data
        time_period = result_data.get('time_period', {})
        start_value = result_data.get('start_value')
        end_value = result_data.get('end_value')
        absolute_change = result_data.get('absolute_change')
        percentage_change = result_data.get('percentage_change')
        trend_direction = result_data.get('trend_direction')
        currency_code = result_data.get('currency_code', 'USD')
        statistics = result_data.get('statistics', {})

        # Format the time period information using format_time_period
        time_period_str = format_time_period(
            start_date=datetime.datetime.fromisoformat(time_period['start_date']).date() if time_period.get('start_date') else None,
            end_date=datetime.datetime.fromisoformat(time_period['end_date']).date() if time_period.get('end_date') else None,
            granularity=time_period.get('granularity')
        )

        # Format the absolute and percentage changes using format_currency and format_percentage
        absolute_change_str = format_currency(absolute_change, currency_code) if absolute_change is not None else "N/A"
        percentage_change_str = format_percentage(percentage_change) if percentage_change is not None else "N/A"

        # Format the trend direction using format_trend
        trend_direction_str = format_trend(TrendDirection[trend_direction]) if trend_direction else "N/A"

        # Include aggregated statistics with appropriate formatting
        average_charge = format_currency(statistics.get('average'), currency_code) if statistics.get('average') is not None else "N/A"
        minimum_charge = format_currency(statistics.get('minimum'), currency_code) if statistics.get('minimum') is not None else "N/A"
        maximum_charge = format_currency(statistics.get('maximum'), currency_code) if statistics.get('maximum') is not None else "N/A"

        # Create a text template with sections for summary, details, and statistics
        text_report = f"""
        Freight Price Movement Analysis
        ==============================
        Period: {time_period_str}
        Generated: {datetime.datetime.now().isoformat()}

        SUMMARY:
        Freight charges have {trend_direction_str.split(' ')[0].lower() if trend_direction_str != "N/A" else "remained stable"} by {percentage_change_str} 
        ({absolute_change_str}) over the selected period.

        DETAILS:
        - Starting value: {format_currency(start_value, currency_code) if start_value is not None else "N/A"}
        - Ending value: {format_currency(end_value, currency_code) if end_value is not None else "N/A"}
        - Absolute change: {absolute_change_str}
        - Percentage change: {percentage_change_str}
        - Trend direction: {trend_direction_str}

        STATISTICS:
        - Average charge: {average_charge}
        - Minimum charge: {minimum_charge}
        - Maximum charge: {maximum_charge}
        """

        # Return the formatted text
        return text_report

    except Exception as e:
        logger.error(f"Error formatting analysis result {analysis_result.id} as text: {e}", exc_info=True)
        raise PresentationException(f"Failed to format analysis result {analysis_result.id} as text: {e}", original_exception=e)


def generate_visualization(analysis_result: AnalysisResult, visualization_type: typing.Optional[str] = None) -> typing.Dict[str, typing.Any]:
    """
    Generates visualizations for analysis results.

    Args:
        analysis_result: Analysis result object
        visualization_type: Optional type of visualization to generate

    Returns:
        Visualization data including base64-encoded images
    """
    logger.info(f"Generating visualization for analysis result {analysis_result.id}")
    try:
        # Extract result data from analysis_result
        result_data = analysis_result.to_dict(include_details=True)

        # Extract time series data
        time_series = result_data.get('results', {}).get('time_series', [])

        # Extract trend direction
        trend_direction = result_data.get('trend_direction')

        # Extract percentage change
        percentage_change = result_data.get('percentage_change')

        # Extract currency code
        currency_code = result_data.get('currency_code')

        # If visualization_type is not specified, determine the appropriate type based on the data
        if not visualization_type:
            if time_series:
                visualization_type = "line"
            elif trend_direction:
                visualization_type = "trend_indicator"
            else:
                visualization_type = "summary"

        # Generate visualizations based on the type
        if visualization_type == "line":
            visualization_data = generate_line_chart(time_series, currency_code=currency_code)
        elif visualization_type == "bar":
            visualization_data = generate_bar_chart(result_data.get('results', {}).get('statistics', {}), currency_code=currency_code)
        elif visualization_type == "trend_indicator":
            visualization_data = generate_trend_indicator(TrendDirection[trend_direction], percentage_change)
        elif visualization_type == "comparison":
            # Assuming you have comparison data in the analysis result
            visualization_data = generate_comparison_chart(time_series, time_series, currency_code=currency_code)
        else:
            visualization_data = {"message": "No visualization available for this data"}

        # Return a dictionary with visualization data including base64-encoded images
        return visualization_data

    except Exception as e:
        logger.error(f"Error generating visualization for analysis result {analysis_result.id}: {e}", exc_info=True)
        raise PresentationException(f"Failed to generate visualization for analysis result {analysis_result.id}: {e}", original_exception=e)


def get_output_formatter(output_format: OutputFormat) -> typing.Callable:
    """
    Returns the appropriate formatter function for the specified output format.

    Args:
        output_format: Output format enum value

    Returns:
        Formatter function for the specified output format
    """
    try:
        # If output_format is OutputFormat.JSON, return format_json_output
        if output_format == OutputFormat.JSON:
            return format_json_output

        # If output_format is OutputFormat.CSV, return format_csv_output
        elif output_format == OutputFormat.CSV:
            return format_csv_output

        # If output_format is OutputFormat.TEXT, return format_text_output
        elif output_format == OutputFormat.TEXT:
            return format_text_output

        # If output_format is not recognized, raise PresentationException
        else:
            raise PresentationException(f"Unsupported output format: {output_format}")

    except Exception as e:
        logger.error(f"Error getting output formatter for {output_format}: {e}", exc_info=True)
        raise PresentationException(f"Failed to get output formatter for {output_format}: {e}", original_exception=e)


class PresentationService:
    """
    Service for formatting and delivering analysis results.
    """

    def __init__(self, analysis_engine: typing.Optional[AnalysisEngine] = None):
        """
        Initializes the PresentationService.

        Args:
            analysis_engine: Optional AnalysisEngine instance
        """
        self.logger = logger
        if analysis_engine:
            self._analysis_engine = analysis_engine
        else:
            self._analysis_engine = AnalysisEngine()
        self.logger.info("PresentationService initialized")

    def format_result(self, analysis_id: str, output_format: typing.Optional[OutputFormat] = None,
                      include_visualization: typing.Optional[bool] = False) -> typing.Dict[str, typing.Any]:
        """
        Formats an analysis result according to the specified output format.

        Args:
            analysis_id: ID of the analysis result to format
            output_format: Optional output format enum value
            include_visualization: Whether to include visualizations

        Returns:
            Formatted analysis result
        """
        self.logger.info(f"Formatting analysis result {analysis_id} with output format {output_format}")
        try:
            # Retrieve the analysis result using _analysis_engine.get_analysis_result()
            analysis_result = self._analysis_engine.get_analysis_result(analysis_id)

            # If analysis result is not found, raise PresentationException
            if not analysis_result:
                raise PresentationException(f"Analysis result not found: {analysis_id}")

            # If output_format is not specified, use the format from the analysis result
            if not output_format:
                output_format = analysis_result.output_format

            # Get the appropriate formatter function using get_output_formatter()
            formatter = get_output_formatter(output_format)

            # Format the analysis result using the formatter function
            formatted_result = formatter(analysis_result)

            # If include_visualization is True, generate visualizations
            visualization_data = None
            if include_visualization:
                visualization_data = generate_visualization(analysis_result)

            # Combine the formatted result and visualizations into a response dictionary
            response = {
                "analysis_id": analysis_result.id,
                "output": formatted_result,
                "visualization": visualization_data,
                "output_format": str(output_format)
            }

            # Return the formatted result
            return response

        except Exception as e:
            self.logger.error(f"Error formatting analysis result {analysis_id}: {e}", exc_info=True)
            raise PresentationException(f"Failed to format analysis result {analysis_id}: {e}", original_exception=e)

    def export_result(self, analysis_id: str, output_format: typing.Optional[OutputFormat] = None,
                      file_path: typing.Optional[str] = None,
                      include_visualization: typing.Optional[bool] = False) -> typing.Dict[str, typing.Any]:
        """
        Exports an analysis result to a file in the specified format.

        Args:
            analysis_id: ID of the analysis result to export
            output_format: Optional output format enum value
            file_path: Optional file path to save the exported result
            include_visualization: Whether to include visualizations

        Returns:
            Export result information
        """
        self.logger.info(f"Exporting analysis result {analysis_id} to file")
        try:
            # Format the result using format_result()
            formatted_result = self.format_result(analysis_id, output_format, include_visualization)

            # If file_path is provided, write the formatted result to the file
            if file_path:
                with open(file_path, "w") as f:
                    f.write(formatted_result["output"])
            # If file_path is not provided, generate a default file path based on analysis_id and format
            else:
                file_path = f"analysis_result_{analysis_id}.{output_format.lower()}"
                with open(file_path, "w") as f:
                    f.write(formatted_result["output"])

            # Return a dictionary with export information including file path and success status
            export_info = {
                "file_path": file_path,
                "success": True
            }
            return export_info

        except Exception as e:
            self.logger.error(f"Error exporting analysis result {analysis_id}: {e}", exc_info=True)
            raise PresentationException(f"Failed to export analysis result {analysis_id}: {e}", original_exception=e)

    def generate_summary(self, analysis_id: str) -> typing.Dict[str, typing.Any]:
        """
        Generates a summary of an analysis result.

        Args:
            analysis_id: ID of the analysis result

        Returns:
            Summary of the analysis result
        """
        self.logger.info(f"Generating summary for analysis result {analysis_id}")
        try:
            # Retrieve the analysis result using _analysis_engine.get_analysis_result()
            analysis_result = self._analysis_engine.get_analysis_result(analysis_id)

            # If analysis result is not found, raise PresentationException
            if not analysis_result:
                raise PresentationException(f"Analysis result not found: {analysis_id}")

            # Extract key metrics from the analysis result
            start_value = analysis_result.start_value
            end_value = analysis_result.end_value
            absolute_change = analysis_result.absolute_change
            percentage_change = analysis_result.percentage_change
            trend_direction = analysis_result.trend_direction
            currency_code = analysis_result.currency_code

            # Format the metrics using appropriate formatting functions
            start_value_str = format_currency(start_value, currency_code) if start_value is not None else "N/A"
            end_value_str = format_currency(end_value, currency_code) if end_value is not None else "N/A"
            absolute_change_str = format_currency(absolute_change, currency_code) if absolute_change is not None else "N/A"
            percentage_change_str = format_percentage(percentage_change) if percentage_change is not None else "N/A"
            trend_direction_str = format_trend(trend_direction) if trend_direction else "N/A"

            # Create a summary dictionary with the formatted metrics
            summary = {
                "start_value": start_value_str,
                "end_value": end_value_str,
                "absolute_change": absolute_change_str,
                "percentage_change": percentage_change_str,
                "trend_direction": trend_direction_str
            }

            # Return the summary dictionary
            return summary

        except Exception as e:
            self.logger.error(f"Error generating summary for analysis result {analysis_id}: {e}", exc_info=True)
            raise PresentationException(f"Failed to generate summary for analysis result {analysis_id}: {e}", original_exception=e)

    def format_comparison(self, base_analysis_id: str, comparison_analysis_id: str,
                          output_format: typing.Optional[OutputFormat] = None,
                          include_visualization: typing.Optional[bool] = False) -> typing.Dict[str, typing.Any]:
        """
        Formats a comparison between two analysis results.

        Args:
            base_analysis_id: ID of the base analysis result
            comparison_analysis_id: ID of the comparison analysis result
            output_format: Optional output format enum value
            include_visualization: Whether to include visualizations

        Returns:
            Formatted comparison result
        """
        self.logger.info(f"Formatting comparison between analysis results {base_analysis_id} and {comparison_analysis_id}")
        try:
            # Retrieve both analysis results using _analysis_engine.get_analysis_result()
            base_analysis_result = self._analysis_engine.get_analysis_result(base_analysis_id)
            comparison_analysis_result = self._analysis_engine.get_analysis_result(comparison_analysis_id)

            # If either analysis result is not found, raise PresentationException
            if not base_analysis_result or not comparison_analysis_result:
                raise PresentationException("One or both analysis results not found")

            # If output_format is not specified, use JSON as default
            if not output_format:
                output_format = OutputFormat.JSON

            # Format both analysis results using the appropriate formatter
            base_formatted = get_output_formatter(output_format)(base_analysis_result)
            comparison_formatted = get_output_formatter(output_format)(comparison_analysis_result)

            # Calculate and format the differences between the results
            base_value = base_analysis_result.start_value
            comparison_value = comparison_analysis_result.start_value
            difference = base_value - comparison_value if base_value and comparison_value else None
            difference_str = format_currency(difference, base_analysis_result.currency_code) if difference else "N/A"

            # If include_visualization is True, generate a comparison visualization
            visualization_data = None
            if include_visualization:
                visualization_data = generate_visualization(base_analysis_result)

            # Combine the formatted results and comparison into a response dictionary
            response = {
                "base_analysis": base_formatted,
                "comparison_analysis": comparison_formatted,
                "difference": difference_str,
                "visualization": visualization_data
            }

            # Return the formatted comparison
            return response

        except Exception as e:
            self.logger.error(f"Error formatting comparison between analysis results {base_analysis_id} and {comparison_analysis_id}: {e}", exc_info=True)
            raise PresentationException(f"Failed to format comparison between analysis results {base_analysis_id} and {comparison_analysis_id}: {e}", original_exception=e)