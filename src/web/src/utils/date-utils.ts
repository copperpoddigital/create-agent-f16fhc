/**
 * Utility functions for date manipulation and formatting in the Freight Price Movement Agent
 * Provides centralized date-related helper functions to ensure consistent date handling
 * across the application, particularly for time period selection and analysis.
 */

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc"; // v1.11.7
import timezone from "dayjs/plugin/timezone"; // v1.11.7
import customParseFormat from "dayjs/plugin/customParseFormat"; // v1.11.7
import isSameOrBefore from "dayjs/plugin/isSameOrBefore"; // v1.11.7
import isSameOrAfter from "dayjs/plugin/isSameOrAfter"; // v1.11.7
import { DATE_FORMATS, DEFAULT_DATE_FORMAT } from '../config/constants';
import { TimeGranularity } from '../types';

// Extend dayjs with plugins
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(customParseFormat);
dayjs.extend(isSameOrBefore);
dayjs.extend(isSameOrAfter);

/**
 * Formats a date string or Date object according to the specified format
 * 
 * @param date - Date string or Date object to format
 * @param format - Format string (defaults to application default format)
 * @returns Formatted date string
 */
export const formatDate = (date: string | Date, format: string = DEFAULT_DATE_FORMAT): string => {
  if (!date) {
    return '';
  }
  
  return dayjs(date).format(format);
};

/**
 * Parses a date string in the specified format into a Date object
 * 
 * @param dateString - Date string to parse
 * @param format - Format of the date string (defaults to application default format)
 * @returns Parsed Date object or null if invalid
 */
export const parseDate = (dateString: string, format: string = DEFAULT_DATE_FORMAT): Date | null => {
  if (!dateString) {
    return null;
  }
  
  const parsed = dayjs(dateString, format);
  
  return parsed.isValid() ? parsed.toDate() : null;
};

/**
 * Checks if a date string is valid according to the specified format
 * 
 * @param dateString - Date string to validate
 * @param format - Format to validate against (defaults to application default format)
 * @returns True if the date is valid, false otherwise
 */
export const isValidDate = (dateString: string, format: string = DEFAULT_DATE_FORMAT): boolean => {
  if (!dateString) {
    return false;
  }
  
  return dayjs(dateString, format).isValid();
};

/**
 * Formats a date for API requests using the API_FORMAT
 * 
 * @param date - Date string or Date object to format
 * @returns Date formatted for API consumption
 */
export const formatDateForAPI = (date: string | Date): string => {
  if (!date) {
    return '';
  }
  
  return dayjs(date).format(DATE_FORMATS.API_FORMAT);
};

/**
 * Formats a date received from the API to the application's display format
 * 
 * @param dateString - Date string from API (in API_FORMAT)
 * @returns Date formatted for display
 */
export const formatDateFromAPI = (dateString: string): string => {
  if (!dateString) {
    return '';
  }
  
  return dayjs(dateString, DATE_FORMATS.API_FORMAT).format(DEFAULT_DATE_FORMAT);
};

/**
 * Generates start and end dates for a predefined time period based on granularity
 * 
 * @param granularity - Time granularity (daily, weekly, monthly)
 * @param periods - Number of periods to go back
 * @returns Object with startDate and endDate strings in YYYY-MM-DD format
 */
export const getDateRangeForGranularity = (
  granularity: TimeGranularity,
  periods: number = 1
): { startDate: string; endDate: string } => {
  const endDate = dayjs();
  let startDate;

  switch (granularity) {
    case TimeGranularity.DAILY:
      startDate = endDate.subtract(periods, 'day');
      break;
    case TimeGranularity.WEEKLY:
      startDate = endDate.subtract(periods, 'week');
      break;
    case TimeGranularity.MONTHLY:
      startDate = endDate.subtract(periods, 'month');
      break;
    default:
      startDate = endDate.subtract(periods, 'day');
  }

  return {
    startDate: startDate.format(DATE_FORMATS.YYYY_MM_DD),
    endDate: endDate.format(DATE_FORMATS.YYYY_MM_DD),
  };
};

/**
 * Calculates the difference between two dates in the specified unit
 * 
 * @param startDate - Start date string or Date object
 * @param endDate - End date string or Date object
 * @param unit - Unit for calculation (day, week, month, etc.)
 * @returns Difference between dates in the specified unit
 */
export const calculateDateDifference = (
  startDate: string | Date,
  endDate: string | Date,
  unit: string = 'day'
): number => {
  const start = dayjs(startDate);
  const end = dayjs(endDate);
  
  return Math.abs(end.diff(start, unit as any));
};

/**
 * Adds a specified amount of time to a date
 * 
 * @param date - Date string or Date object
 * @param amount - Amount to add
 * @param unit - Unit of time to add (day, week, month, etc.)
 * @returns New date after addition, formatted as YYYY-MM-DD
 */
export const addToDate = (
  date: string | Date,
  amount: number,
  unit: string = 'day'
): string => {
  return dayjs(date).add(amount, unit as any).format(DATE_FORMATS.YYYY_MM_DD);
};

/**
 * Subtracts a specified amount of time from a date
 * 
 * @param date - Date string or Date object
 * @param amount - Amount to subtract
 * @param unit - Unit of time to subtract (day, week, month, etc.)
 * @returns New date after subtraction, formatted as YYYY-MM-DD
 */
export const subtractFromDate = (
  date: string | Date,
  amount: number,
  unit: string = 'day'
): string => {
  return dayjs(date).subtract(amount, unit as any).format(DATE_FORMATS.YYYY_MM_DD);
};

/**
 * Checks if a date is before another date
 * 
 * @param date - Date to check
 * @param compareDate - Date to compare against
 * @returns True if date is before compareDate, false otherwise
 */
export const isDateBefore = (date: string | Date, compareDate: string | Date): boolean => {
  return dayjs(date).isBefore(dayjs(compareDate));
};

/**
 * Checks if a date is after another date
 * 
 * @param date - Date to check
 * @param compareDate - Date to compare against
 * @returns True if date is after compareDate, false otherwise
 */
export const isDateAfter = (date: string | Date, compareDate: string | Date): boolean => {
  return dayjs(date).isAfter(dayjs(compareDate));
};

/**
 * Checks if a date is between two other dates (inclusive)
 * 
 * @param date - Date to check
 * @param startDate - Start of date range
 * @param endDate - End of date range
 * @returns True if date is between startDate and endDate (inclusive), false otherwise
 */
export const isDateBetween = (
  date: string | Date,
  startDate: string | Date,
  endDate: string | Date
): boolean => {
  const d = dayjs(date);
  return d.isSameOrAfter(dayjs(startDate)) && d.isSameOrBefore(dayjs(endDate));
};

/**
 * Gets the start of a period (day, week, month, etc.) for a given date
 * 
 * @param date - Date string or Date object
 * @param unit - Unit of time (day, week, month, etc.)
 * @returns Start of period date formatted as YYYY-MM-DD
 */
export const getStartOfPeriod = (date: string | Date, unit: string = 'day'): string => {
  return dayjs(date).startOf(unit as any).format(DATE_FORMATS.YYYY_MM_DD);
};

/**
 * Gets the end of a period (day, week, month, etc.) for a given date
 * 
 * @param date - Date string or Date object
 * @param unit - Unit of time (day, week, month, etc.)
 * @returns End of period date formatted as YYYY-MM-DD
 */
export const getEndOfPeriod = (date: string | Date, unit: string = 'day'): string => {
  return dayjs(date).endOf(unit as any).format(DATE_FORMATS.YYYY_MM_DD);
};

/**
 * Generates an array of date ranges based on start date, end date, and granularity
 * 
 * @param startDate - Start date string or Date object
 * @param endDate - End date string or Date object
 * @param granularity - Time granularity (daily, weekly, monthly, custom)
 * @param customInterval - Custom interval in days (used only when granularity is CUSTOM)
 * @returns Array of date range objects { start, end, label }
 */
export const generateDateRanges = (
  startDate: string | Date,
  endDate: string | Date,
  granularity: TimeGranularity,
  customInterval?: number
): Array<{ start: string; end: string; label: string }> => {
  const start = dayjs(startDate);
  const end = dayjs(endDate);
  const ranges: Array<{ start: string; end: string; label: string }> = [];
  
  let unit: string;
  let interval: number;
  
  // Determine unit and interval based on granularity
  switch (granularity) {
    case TimeGranularity.DAILY:
      unit = 'day';
      interval = 1;
      break;
    case TimeGranularity.WEEKLY:
      unit = 'week';
      interval = 1;
      break;
    case TimeGranularity.MONTHLY:
      unit = 'month';
      interval = 1;
      break;
    case TimeGranularity.CUSTOM:
      unit = 'day';
      interval = customInterval || 1;
      break;
    default:
      unit = 'day';
      interval = 1;
  }
  
  // Generate date ranges
  let currentStart = start;
  while (currentStart.isBefore(end) || currentStart.isSame(end, 'day')) {
    let currentEnd;
    
    if (granularity === TimeGranularity.CUSTOM) {
      // For custom interval, add the specified number of days (minus 1 to make it inclusive)
      currentEnd = currentStart.add(interval - 1, 'day');
      
      // If currentEnd goes beyond the overall end date, cap it at the end date
      if (currentEnd.isAfter(end)) {
        currentEnd = end;
      }
    } else {
      // For standard intervals, use endOf to get the proper period end
      currentEnd = currentStart.endOf(unit as any);
      
      // If currentEnd goes beyond the overall end date, cap it at the end date
      if (currentEnd.isAfter(end)) {
        currentEnd = end;
      }
    }
    
    // Format the label based on the granularity
    let label = '';
    switch (granularity) {
      case TimeGranularity.DAILY:
        label = currentStart.format('MMM DD');
        break;
      case TimeGranularity.WEEKLY:
        label = `${currentStart.format('MMM DD')} - ${currentEnd.format('MMM DD')}`;
        break;
      case TimeGranularity.MONTHLY:
        label = currentStart.format('MMM YYYY');
        break;
      case TimeGranularity.CUSTOM:
        label = `${currentStart.format('MMM DD')} - ${currentEnd.format('MMM DD')}`;
        break;
    }
    
    ranges.push({
      start: currentStart.format(DATE_FORMATS.YYYY_MM_DD),
      end: currentEnd.format(DATE_FORMATS.YYYY_MM_DD),
      label
    });
    
    // Move to the next period
    currentStart = currentStart.add(interval, unit as any);
    
    // Check if we've gone past the end date
    if (granularity !== TimeGranularity.CUSTOM && currentStart.isAfter(end)) {
      break;
    }
  }
  
  return ranges;
};