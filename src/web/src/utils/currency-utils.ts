/**
 * Currency utility functions for the Freight Price Movement Agent
 * 
 * This file provides utility functions for currency formatting, parsing, and conversion
 * to ensure consistent handling of monetary values across the application.
 */

import { DEFAULT_CURRENCY, SUPPORTED_CURRENCIES } from '../config/constants';

/**
 * Interface for currency formatting options
 */
interface CurrencyFormatOptions {
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  useGrouping?: boolean;
  signDisplay?: 'auto' | 'never' | 'always' | 'exceptZero';
}

/**
 * Interface for percentage formatting options
 */
interface PercentageFormatOptions {
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
  signDisplay?: 'auto' | 'never' | 'always' | 'exceptZero';
}

/**
 * Interface for exchange rates object
 */
interface ExchangeRates {
  [currencyPair: string]: number;
}

/**
 * Formats a numeric value as a currency string with the specified currency code
 * 
 * @param value - The numeric value to format
 * @param currencyCode - The currency code (default: DEFAULT_CURRENCY)
 * @param options - Formatting options
 * @returns Formatted currency string
 */
export const formatCurrency = (
  value: number,
  currencyCode: string = DEFAULT_CURRENCY,
  options: CurrencyFormatOptions = {}
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  const defaultOptions: CurrencyFormatOptions = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: true
  };

  const formatOptions = { ...defaultOptions, ...options };

  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      ...formatOptions
    }).format(value);
  } catch (error) {
    console.error(`Error formatting currency: ${error}`);
    return `${value} ${currencyCode}`;
  }
};

/**
 * Parses a currency string into a numeric value
 * 
 * @param currencyString - The currency string to parse
 * @returns Parsed numeric value
 */
export const parseCurrency = (currencyString: string): number => {
  if (!currencyString || typeof currencyString !== 'string') {
    return 0;
  }

  // Remove currency symbols, commas, spaces, and other non-numeric characters
  // Keep decimal point and minus sign
  const numericString = currencyString
    .replace(/[^\d.-]/g, '')
    .trim();

  const value = parseFloat(numericString);
  return isNaN(value) ? 0 : value;
};

/**
 * Converts a monetary value from one currency to another using exchange rates
 * 
 * @param value - The monetary value to convert
 * @param fromCurrency - Source currency code
 * @param toCurrency - Target currency code
 * @param exchangeRates - Object containing exchange rates
 * @returns Converted value in target currency
 */
export const convertCurrency = (
  value: number,
  fromCurrency: string = DEFAULT_CURRENCY,
  toCurrency: string = DEFAULT_CURRENCY,
  exchangeRates?: ExchangeRates
): number => {
  if (typeof value !== 'number' || isNaN(value)) {
    return 0;
  }

  // If currencies are the same, no conversion needed
  if (fromCurrency === toCurrency) {
    return value;
  }

  if (!exchangeRates) {
    // In a real application, we would fetch current exchange rates here
    // For now, we'll throw an error if rates aren't provided
    throw new Error('Exchange rates must be provided for currency conversion');
  }

  const rateKey = `${fromCurrency}${toCurrency}`;
  const inverseRateKey = `${toCurrency}${fromCurrency}`;

  if (rateKey in exchangeRates) {
    return value * exchangeRates[rateKey];
  } else if (inverseRateKey in exchangeRates) {
    return value / exchangeRates[inverseRateKey];
  } else {
    // If direct conversion not available, try to convert through base currency (usually USD)
    const baseToFrom = `${DEFAULT_CURRENCY}${fromCurrency}`;
    const baseToTo = `${DEFAULT_CURRENCY}${toCurrency}`;

    if (baseToFrom in exchangeRates && baseToTo in exchangeRates) {
      // Convert to base currency first, then to target currency
      const valueInBaseCurrency = value / exchangeRates[baseToFrom];
      return valueInBaseCurrency * exchangeRates[baseToTo];
    }
    
    throw new Error(`No exchange rate found for conversion from ${fromCurrency} to ${toCurrency}`);
  }
};

/**
 * Formats a numeric value as a percentage string with sign
 * 
 * @param value - The numeric value as direct percentage (5.2 for 5.2%)
 * @param options - Formatting options
 * @returns Formatted percentage string with sign and % symbol (e.g., "+5.2%")
 */
export const formatPercentage = (
  value: number,
  options: PercentageFormatOptions = {}
): string => {
  if (typeof value !== 'number' || isNaN(value)) {
    return '';
  }

  const defaultOptions: PercentageFormatOptions = {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
    signDisplay: 'always'
  };

  const formatOptions = { ...defaultOptions, ...options };

  try {
    // Input is direct percentage (5.2 for 5.2%), but Intl.NumberFormat expects decimal (0.052)
    // so we divide by 100
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      ...formatOptions
    }).format(value / 100);
  } catch (error) {
    console.error(`Error formatting percentage: ${error}`);
    return `${value > 0 ? '+' : ''}${value}%`;
  }
};

/**
 * Gets the currency symbol for a given currency code
 * 
 * @param currencyCode - The currency code
 * @returns Currency symbol
 */
export const getCurrencySymbol = (currencyCode: string = DEFAULT_CURRENCY): string => {
  try {
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      currencyDisplay: 'symbol'
    });
    
    // Format a zero value and extract just the symbol
    const parts = formatter.formatToParts(0);
    const currencyPart = parts.find(part => part.type === 'currency');
    return currencyPart ? currencyPart.value : currencyCode;
  } catch (error) {
    console.error(`Error getting currency symbol: ${error}`);
    return currencyCode;
  }
};

/**
 * Returns the default currency code for the application
 * 
 * @returns Default currency code
 */
export const getDefaultCurrency = (): string => {
  return DEFAULT_CURRENCY;
};

/**
 * Returns the list of supported currency codes
 * 
 * @returns Array of supported currency codes
 */
export const getSupportedCurrencies = (): string[] => {
  return [...SUPPORTED_CURRENCIES];
};

/**
 * Formats an absolute price change with appropriate sign and currency
 * 
 * @param change - The price change value
 * @param currencyCode - The currency code
 * @returns Formatted absolute change string
 */
export const formatAbsoluteChange = (
  change: number,
  currencyCode: string = DEFAULT_CURRENCY
): string => {
  if (typeof change !== 'number' || isNaN(change)) {
    return '';
  }

  const sign = change > 0 ? '+' : (change < 0 ? '-' : '');
  const absChange = Math.abs(change);
  const formattedValue = formatCurrency(absChange, currencyCode);

  return `${sign}${formattedValue}`;
};