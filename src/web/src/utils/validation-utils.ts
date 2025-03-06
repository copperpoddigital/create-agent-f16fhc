/**
 * Validation utility functions for the Freight Price Movement Agent
 * 
 * This file provides a comprehensive set of validation functions to ensure
 * data integrity and form validation throughout the application. These functions
 * validate various data types including user inputs, file uploads, and analysis parameters.
 */

import { isValidDate, isDateBetween } from './date-utils';
import { getSupportedCurrencies } from './currency-utils';
import { 
  DataSourceType, 
  AuthType, 
  DatabaseType, 
  TMSType, 
  ERPType 
} from '../types';
import { TimeGranularity } from '../types';
import { 
  MAX_FILE_SIZE, 
  SUPPORTED_FILE_TYPES, 
  PASSWORD_MIN_LENGTH 
} from '../config/constants';

/**
 * Validates that a value is not empty or undefined
 * 
 * @param value - Any value to check for emptiness
 * @returns Error message if validation fails, undefined if validation passes
 */
export const isRequired = (value: any): string | undefined => {
  if (value === undefined || value === null || value === '') {
    return 'This field is required';
  }
  return undefined;
};

/**
 * Validates that a string is a properly formatted email address
 * 
 * @param email - Email address to validate
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateEmail = (email: string): string | undefined => {
  const requiredError = isRequired(email);
  if (requiredError) {
    return requiredError;
  }

  // Email regex pattern for validation
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  
  if (!emailPattern.test(email)) {
    return 'Please enter a valid email address';
  }
  
  return undefined;
};

/**
 * Validates that a password meets security requirements
 * 
 * @param password - Password to validate
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validatePassword = (password: string): string | undefined => {
  const requiredError = isRequired(password);
  if (requiredError) {
    return requiredError;
  }

  if (password.length < PASSWORD_MIN_LENGTH) {
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters long`;
  }

  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }

  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }

  if (!/\d/.test(password)) {
    return 'Password must contain at least one number';
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return 'Password must contain at least one special character';
  }

  return undefined;
};

/**
 * Validates that two passwords match
 * 
 * @param password - Original password
 * @param confirmPassword - Password confirmation to compare
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validatePasswordMatch = (password: string, confirmPassword: string): string | undefined => {
  const passwordRequiredError = isRequired(password);
  if (passwordRequiredError) {
    return passwordRequiredError;
  }

  const confirmPasswordRequiredError = isRequired(confirmPassword);
  if (confirmPasswordRequiredError) {
    return confirmPasswordRequiredError;
  }

  if (password !== confirmPassword) {
    return 'Passwords do not match';
  }

  return undefined;
};

/**
 * Validates that a username meets format requirements
 * 
 * @param username - Username to validate
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateUsername = (username: string): string | undefined => {
  const requiredError = isRequired(username);
  if (requiredError) {
    return requiredError;
  }

  if (username.length < 5) {
    return 'Username must be at least 5 characters long';
  }

  // Username should contain only alphanumeric characters, underscores, and hyphens
  if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    return 'Username can only contain letters, numbers, underscores, and hyphens';
  }

  return undefined;
};

/**
 * Validates that a string is a properly formatted URL
 * 
 * @param url - URL to validate
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateUrl = (url: string): string | undefined => {
  const requiredError = isRequired(url);
  if (requiredError) {
    return requiredError;
  }

  // URL regex pattern for validation
  const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
  
  if (!urlPattern.test(url)) {
    return 'Please enter a valid URL';
  }
  
  return undefined;
};

/**
 * Validates that a file does not exceed the maximum allowed size
 * 
 * @param file - File object to validate
 * @param maxSize - Maximum allowed size in bytes (optional, uses MAX_FILE_SIZE constant if not provided)
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateFileSize = (file: File, maxSize?: number): string | undefined => {
  if (!file) {
    return undefined; // File is not required
  }

  const maxAllowedSize = maxSize || MAX_FILE_SIZE;
  
  if (file.size > maxAllowedSize) {
    const maxSizeMB = maxAllowedSize / (1024 * 1024);
    return `File size exceeds the maximum allowed size of ${maxSizeMB} MB`;
  }
  
  return undefined;
};

/**
 * Validates that a file has an allowed file type
 * 
 * @param file - File object to validate
 * @param allowedTypes - Array of allowed file extensions (optional, uses SUPPORTED_FILE_TYPES constant if not provided)
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateFileType = (file: File, allowedTypes?: string[]): string | undefined => {
  if (!file) {
    return undefined; // File is not required
  }

  const allowed = allowedTypes || SUPPORTED_FILE_TYPES;
  
  // Extract file extension
  const fileExtension = file.name.split('.').pop()?.toLowerCase();
  
  if (!fileExtension || !allowed.includes(`.${fileExtension}`)) {
    return `File type not supported. Allowed types: ${allowed.join(', ')}`;
  }
  
  return undefined;
};

/**
 * Validates that a date range is valid (start date before end date)
 * 
 * @param startDate - Start date string
 * @param endDate - End date string
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateDateRange = (startDate: string, endDate: string): string | undefined => {
  const startDateRequiredError = isRequired(startDate);
  if (startDateRequiredError) {
    return startDateRequiredError;
  }

  const endDateRequiredError = isRequired(endDate);
  if (endDateRequiredError) {
    return endDateRequiredError;
  }

  if (!isValidDate(startDate)) {
    return 'Invalid start date format';
  }

  if (!isValidDate(endDate)) {
    return 'Invalid end date format';
  }

  // Check if start date is before end date
  if (new Date(startDate) >= new Date(endDate)) {
    return 'Start date must be before end date';
  }

  return undefined;
};

/**
 * Validates that a number is within a specified range
 * 
 * @param value - Numeric value to validate
 * @param min - Minimum allowed value (optional)
 * @param max - Maximum allowed value (optional)
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateNumericRange = (value: number, min?: number, max?: number): string | undefined => {
  if (typeof value !== 'number' || isNaN(value)) {
    return 'Please enter a valid number';
  }

  if (min !== undefined && value < min) {
    return `Value must be at least ${min}`;
  }

  if (max !== undefined && value > max) {
    return `Value must be at most ${max}`;
  }

  return undefined;
};

/**
 * Validates that a currency code is supported
 * 
 * @param currency - Currency code to validate
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateCurrency = (currency: string): string | undefined => {
  const requiredError = isRequired(currency);
  if (requiredError) {
    return requiredError;
  }

  const supportedCurrencies = getSupportedCurrencies();
  
  if (!supportedCurrencies.includes(currency)) {
    return `Currency not supported. Supported currencies: ${supportedCurrencies.join(', ')}`;
  }
  
  return undefined;
};

/**
 * Validates a single form field based on validation rules
 * 
 * @param value - Field value to validate
 * @param validations - Object containing validation rules
 * @returns Error message if validation fails, undefined if validation passes
 */
export const validateFormField = (value: any, validations: any): string | undefined => {
  if (!validations) {
    return undefined;
  }

  // Check if field is required
  if (validations.required) {
    const requiredError = isRequired(value);
    if (requiredError) {
      return requiredError;
    }
  }

  // Skip other validations if value is empty and not required
  if ((value === undefined || value === null || value === '') && !validations.required) {
    return undefined;
  }

  // Apply each validation rule
  if (validations.email) {
    const emailError = validateEmail(value);
    if (emailError) return emailError;
  }

  if (validations.password) {
    const passwordError = validatePassword(value);
    if (passwordError) return passwordError;
  }

  if (validations.url) {
    const urlError = validateUrl(value);
    if (urlError) return urlError;
  }

  if (validations.min !== undefined) {
    if (typeof value === 'string' && value.length < validations.min) {
      return `Must be at least ${validations.min} characters`;
    }
    if (typeof value === 'number' && value < validations.min) {
      return `Must be at least ${validations.min}`;
    }
  }

  if (validations.max !== undefined) {
    if (typeof value === 'string' && value.length > validations.max) {
      return `Must be at most ${validations.max} characters`;
    }
    if (typeof value === 'number' && value > validations.max) {
      return `Must be at most ${validations.max}`;
    }
  }

  if (validations.pattern) {
    if (!validations.pattern.test(value)) {
      return validations.patternMessage || 'Invalid format';
    }
  }

  if (validations.match && validations.matchValue) {
    if (value !== validations.matchValue) {
      return validations.matchMessage || 'Values do not match';
    }
  }

  if (validations.custom) {
    return validations.custom(value);
  }

  return undefined;
};

/**
 * Validates an entire form based on validation rules for each field
 * 
 * @param values - Object containing form field values
 * @param validations - Object containing validation rules for each field
 * @returns Object with field names as keys and error messages as values
 */
export const validateForm = (values: Record<string, any>, validations: Record<string, any>): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!values || !validations) {
    return errors;
  }

  // Validate each field using the corresponding validation rules
  Object.keys(validations).forEach(field => {
    const error = validateFormField(values[field], validations[field]);
    if (error) {
      errors[field] = error;
    }
  });

  return errors;
};

/**
 * Validates data source connection parameters based on source type
 * 
 * @param connectionParams - Object containing connection parameters
 * @returns Object with field names as keys and error messages as values
 */
export const validateDataSourceConnection = (connectionParams: Record<string, any>): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!connectionParams) {
    errors.source_type = 'Data source type is required';
    return errors;
  }

  const sourceType = connectionParams.source_type;

  // Validate common fields
  if (!sourceType) {
    errors.source_type = 'Data source type is required';
    return errors;
  }

  // Validate based on source type
  switch (sourceType) {
    case DataSourceType.CSV:
      // Validate CSV-specific parameters
      if (!connectionParams.file) {
        errors.file = 'File is required';
      } else {
        const fileSizeError = validateFileSize(connectionParams.file);
        const fileTypeError = validateFileType(connectionParams.file, ['.csv']);
        
        if (fileSizeError) errors.file = fileSizeError;
        if (fileTypeError) errors.file_type = fileTypeError;
      }
      
      if (!connectionParams.delimiter) {
        errors.delimiter = 'Delimiter is required';
      }
      
      if (connectionParams.has_header === undefined) {
        errors.has_header = 'Please specify if file has a header row';
      }
      
      if (!connectionParams.date_format) {
        errors.date_format = 'Date format is required';
      }
      break;

    case DataSourceType.DATABASE:
      // Validate DATABASE-specific parameters
      if (!connectionParams.database_type) {
        errors.database_type = 'Database type is required';
      } else if (!Object.values(DatabaseType).includes(connectionParams.database_type)) {
        errors.database_type = 'Invalid database type';
      }

      if (!connectionParams.host) {
        errors.host = 'Host is required';
      }

      if (!connectionParams.port) {
        errors.port = 'Port is required';
      } else if (isNaN(parseInt(connectionParams.port))) {
        errors.port = 'Port must be a number';
      }

      if (!connectionParams.database) {
        errors.database = 'Database name is required';
      }

      if (!connectionParams.username) {
        errors.username = 'Username is required';
      }

      if (!connectionParams.password && !connectionParams.connection_string) {
        errors.password = 'Password is required if connection string is not provided';
      }

      if (!connectionParams.query) {
        errors.query = 'Query is required';
      }
      break;

    case DataSourceType.API:
      // Validate API-specific parameters
      if (!connectionParams.url) {
        errors.url = 'URL is required';
      } else {
        const urlError = validateUrl(connectionParams.url);
        if (urlError) errors.url = urlError;
      }

      if (!connectionParams.method) {
        errors.method = 'Method is required';
      }

      if (!connectionParams.auth_type) {
        errors.auth_type = 'Authentication type is required';
      } else if (!Object.values(AuthType).includes(connectionParams.auth_type)) {
        errors.auth_type = 'Invalid authentication type';
      }

      if (connectionParams.auth_type !== AuthType.NONE) {
        if (!connectionParams.auth_config) {
          errors.auth_config = 'Authentication configuration is required';
        }
      }

      if (!connectionParams.response_path) {
        errors.response_path = 'Response path is required';
      }
      break;

    case DataSourceType.TMS:
      // Validate TMS-specific parameters
      if (!connectionParams.tms_type) {
        errors.tms_type = 'TMS type is required';
      } else if (!Object.values(TMSType).includes(connectionParams.tms_type)) {
        errors.tms_type = 'Invalid TMS type';
      }

      if (!connectionParams.connection_url) {
        errors.connection_url = 'Connection URL is required';
      } else {
        const urlError = validateUrl(connectionParams.connection_url);
        if (urlError) errors.connection_url = urlError;
      }

      if (!connectionParams.username) {
        errors.username = 'Username is required';
      }

      if (!connectionParams.password && !connectionParams.api_key) {
        errors.authentication = 'Either password or API key is required';
      }
      break;

    case DataSourceType.ERP:
      // Validate ERP-specific parameters
      if (!connectionParams.erp_type) {
        errors.erp_type = 'ERP type is required';
      } else if (!Object.values(ERPType).includes(connectionParams.erp_type)) {
        errors.erp_type = 'Invalid ERP type';
      }

      if (!connectionParams.connection_url) {
        errors.connection_url = 'Connection URL is required';
      } else {
        const urlError = validateUrl(connectionParams.connection_url);
        if (urlError) errors.connection_url = urlError;
      }

      if (!connectionParams.username) {
        errors.username = 'Username is required';
      }

      if (!connectionParams.password && !connectionParams.api_key) {
        errors.authentication = 'Either password or API key is required';
      }
      break;

    default:
      errors.source_type = 'Invalid data source type';
  }

  // Validate field mapping if provided
  if (connectionParams.field_mapping) {
    const mapping = connectionParams.field_mapping;
    
    if (!mapping.freight_charge) {
      errors['field_mapping.freight_charge'] = 'Freight charge field mapping is required';
    }
    
    if (!mapping.currency) {
      errors['field_mapping.currency'] = 'Currency field mapping is required';
    }
    
    if (!mapping.origin) {
      errors['field_mapping.origin'] = 'Origin field mapping is required';
    }
    
    if (!mapping.destination) {
      errors['field_mapping.destination'] = 'Destination field mapping is required';
    }
    
    if (!mapping.date_time) {
      errors['field_mapping.date_time'] = 'Date/time field mapping is required';
    }
  } else {
    errors.field_mapping = 'Field mapping is required';
  }

  return errors;
};

/**
 * Validates analysis parameters for price movement calculation
 * 
 * @param params - Object containing analysis parameters
 * @returns Object with field names as keys and error messages as values
 */
export const validateAnalysisParameters = (params: Record<string, any>): Record<string, string> => {
  const errors: Record<string, string> = {};

  if (!params) {
    errors.general = 'Analysis parameters are required';
    return errors;
  }

  // Validate time period parameters
  if (!params.start_date) {
    errors.start_date = 'Start date is required';
  } else if (!isValidDate(params.start_date)) {
    errors.start_date = 'Invalid start date format';
  }

  if (!params.end_date) {
    errors.end_date = 'End date is required';
  } else if (!isValidDate(params.end_date)) {
    errors.end_date = 'Invalid end date format';
  }

  // Validate date range if both dates are valid
  if (params.start_date && params.end_date && 
      isValidDate(params.start_date) && isValidDate(params.end_date)) {
    const dateRangeError = validateDateRange(params.start_date, params.end_date);
    if (dateRangeError) {
      errors.date_range = dateRangeError;
    }
  }

  // Validate granularity
  if (!params.granularity) {
    errors.granularity = 'Time granularity is required';
  } else if (!Object.values(TimeGranularity).includes(params.granularity)) {
    errors.granularity = 'Invalid time granularity';
  }

  // Validate custom interval if granularity is CUSTOM
  if (params.granularity === TimeGranularity.CUSTOM && !params.custom_interval) {
    errors.custom_interval = 'Custom interval is required';
  }

  // Validate data source selection
  if (!params.data_source_ids || params.data_source_ids.length === 0) {
    errors.data_source_ids = 'At least one data source must be selected';
  }

  // Validate filters if provided
  if (params.filters && Array.isArray(params.filters)) {
    params.filters.forEach((filter: any, index: number) => {
      if (!filter.field) {
        errors[`filters[${index}].field`] = 'Filter field is required';
      }
      
      if (!filter.operator) {
        errors[`filters[${index}].operator`] = 'Filter operator is required';
      }
      
      if (filter.value === undefined || filter.value === null) {
        errors[`filters[${index}].value`] = 'Filter value is required';
      }
    });
  }

  // Validate analysis options
  if (!params.options) {
    errors.options = 'Analysis options are required';
  } else {
    const options = params.options;
    
    // At least one calculation type must be selected
    if (!options.calculate_absolute_change && 
        !options.calculate_percentage_change && 
        !options.identify_trend_direction) {
      errors.calculation_type = 'At least one calculation type must be selected';
    }
    
    // If compare to baseline is true, baseline period ID is required
    if (options.compare_to_baseline && !options.baseline_period_id) {
      errors.baseline_period_id = 'Baseline period is required for comparison';
    }
  }

  return errors;
};