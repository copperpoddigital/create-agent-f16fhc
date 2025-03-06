/**
 * Format utilities for the Freight Price Movement Agent
 *
 * This file provides utility functions for general formatting operations to ensure
 * consistent presentation of data across the application. It includes formatters for
 * text, numbers, trends, dates, and other common data types.
 */

import { formatCurrency, formatPercentage } from './currency-utils';
import { formatDate } from './date-utils';
import { TrendDirection } from '../types';

/**
 * Truncates text to a specified length and adds ellipsis if needed
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length of the text
 * @returns Truncated text with ellipsis if needed
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (!text) {
    return '';
  }

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.substring(0, maxLength - 3)}...`;
};

/**
 * Capitalizes the first letter of a string
 *
 * @param text - Text to capitalize
 * @returns Text with first letter capitalized
 */
export const capitalizeFirstLetter = (text: string): string => {
  if (!text) {
    return '';
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Formats a file size in bytes to a human-readable format
 *
 * @param bytes - File size in bytes
 * @returns Formatted file size with appropriate unit
 */
export const formatFileSize = (bytes: number): string => {
  if (typeof bytes !== 'number' || isNaN(bytes) || bytes < 0) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let unitIndex = 0;

  while (bytes >= 1024 && unitIndex < units.length - 1) {
    bytes /= 1024;
    unitIndex++;
  }

  // Round to 2 decimal places
  const roundedValue = Math.round(bytes * 100) / 100;
  return `${roundedValue} ${units[unitIndex]}`;
};

/**
 * Formats a number with thousand separators and specified decimal places
 *
 * @param value - Number to format
 * @param decimalPlaces - Number of decimal places (default: 2)
 * @returns Formatted number string
 */
export const formatNumber = (value: number, decimalPlaces: number = 2): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces,
    useGrouping: true
  }).format(value);
};

/**
 * Formats a trend direction enum value into a human-readable string with optional icon
 *
 * @param direction - Trend direction enum value
 * @param includeIcon - Whether to include direction icon (default: true)
 * @returns Formatted trend direction with optional icon
 */
export const formatTrendDirection = (
  direction: TrendDirection,
  includeIcon: boolean = true
): string => {
  if (!direction) {
    return '';
  }

  switch (direction) {
    case TrendDirection.INCREASING:
      return includeIcon ? 'Increasing [↑]' : 'Increasing';
    case TrendDirection.DECREASING:
      return includeIcon ? 'Decreasing [↓]' : 'Decreasing';
    case TrendDirection.STABLE:
      return includeIcon ? 'Stable [→]' : 'Stable';
    default:
      return String(direction);
  }
};

/**
 * Formats a price change with appropriate sign, currency, and percentage
 *
 * @param absoluteChange - Absolute price change value
 * @param percentageChange - Percentage price change value
 * @param currencyCode - Currency code for formatting
 * @returns Formatted price change string
 */
export const formatPriceChange = (
  absoluteChange: number,
  percentageChange: number,
  currencyCode: string
): string => {
  if (typeof absoluteChange !== 'number' || isNaN(absoluteChange) ||
      typeof percentageChange !== 'number' || isNaN(percentageChange)) {
    return '';
  }

  const formattedAbsoluteChange = formatCurrency(absoluteChange, currencyCode, {
    signDisplay: 'always'
  });
  
  const formattedPercentageChange = formatPercentage(percentageChange);
  
  return `${formattedAbsoluteChange} (${formattedPercentageChange})`;
};

/**
 * Formats a time period with start and end dates and granularity
 *
 * @param startDate - Start date string
 * @param endDate - End date string
 * @param granularity - Time granularity (e.g., 'daily', 'weekly', 'monthly')
 * @returns Formatted time period string
 */
export const formatTimePeriod = (
  startDate: string,
  endDate: string,
  granularity?: string
): string => {
  if (!startDate || !endDate) {
    return '';
  }

  const formattedStartDate = formatDate(startDate);
  const formattedEndDate = formatDate(endDate);
  const formattedGranularity = granularity ? capitalizeFirstLetter(granularity) : '';

  if (formattedGranularity) {
    return `${formattedStartDate} - ${formattedEndDate} (${formattedGranularity})`;
  }
  
  return `${formattedStartDate} - ${formattedEndDate}`;
};

/**
 * Formats an array of items into a comma-separated string with optional limit
 *
 * @param items - Array of items to format
 * @param limit - Maximum number of items to include before adding "+ X more"
 * @param formatter - Optional function to format each item
 * @returns Comma-separated string of formatted items
 */
export const formatListToString = <T>(
  items: T[],
  limit?: number,
  formatter?: (item: T) => string
): string => {
  if (!items || !Array.isArray(items) || items.length === 0) {
    return '';
  }

  const itemLimit = limit ?? items.length;
  const itemFormatter = formatter ?? ((item: T) => String(item));
  
  if (items.length <= itemLimit) {
    return items.map(itemFormatter).join(', ');
  }
  
  const visibleItems = items.slice(0, itemLimit);
  const remaining = items.length - itemLimit;
  
  return `${visibleItems.map(itemFormatter).join(', ')} + ${remaining} more`;
};

/**
 * Strips HTML tags from a string
 *
 * @param html - String containing HTML
 * @returns Plain text without HTML tags
 */
export const stripHtml = (html: string): string => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  return html.replace(/<[^>]*>/g, '');
};

/**
 * Formats an ID by truncating and adding prefix/suffix if needed
 *
 * @param id - ID to format
 * @param length - Maximum length for truncated ID (default: 8)
 * @param prefix - Optional prefix to add
 * @returns Formatted ID
 */
export const formatId = (
  id: string,
  length: number = 8,
  prefix: string = ''
): string => {
  if (!id || typeof id !== 'string') {
    return '';
  }

  const truncatedId = id.substring(0, length);
  return prefix ? `${prefix}${truncatedId}` : truncatedId;
};

/**
 * Returns singular or plural form of a word based on count
 *
 * @param singular - Singular form of the word
 * @param plural - Plural form of the word (default: singular + 's')
 * @param count - Count to determine form
 * @returns Singular or plural form based on count
 */
export const pluralize = (
  singular: string,
  plural: string | undefined,
  count: number
): string => {
  if (!singular || typeof count !== 'number') {
    return '';
  }

  const pluralForm = plural ?? `${singular}s`;
  return count === 1 ? singular : pluralForm;
};