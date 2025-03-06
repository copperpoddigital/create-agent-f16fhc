import { useState, useEffect, useCallback } from 'react';
import { validateForm } from '../utils/validation-utils';

/**
 * Options for configuring the useForm hook
 */
interface UseFormOptions {
  initialValues?: Record<string, any>;
  onSubmit: (values: Record<string, any>, formHelpers: FormHelpers) => void | Promise<void>;
  validate?: (values: Record<string, any>) => Record<string, string> | Promise<Record<string, string>>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

/**
 * Helper functions provided to the onSubmit callback
 */
interface FormHelpers {
  setSubmitting: (isSubmitting: boolean) => void;
  setErrors: (errors: Record<string, string>) => void;
  resetForm: () => void;
}

/**
 * Return value of the useForm hook
 */
interface UseFormReturn {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  setFieldValue: (field: string, value: any) => void;
  setFieldTouched: (field: string, isTouched?: boolean) => void;
  setFieldError: (field: string, error?: string) => void;
  validateField: (field: string) => Promise<string | undefined>;
  validateForm: () => Promise<Record<string, string>>;
  resetForm: () => void;
  handleSubmit: (e?: React.FormEvent<HTMLFormElement>) => void;
}

/**
 * A custom hook for managing form state, validation, and submission
 * 
 * This hook provides a comprehensive form management solution with support for
 * field-level validation, form submission, and error tracking. It implements
 * client-side validation with server confirmation for form submissions as
 * required by the technical specifications.
 *
 * @param options - Configuration options for the form
 * @returns Form state and handlers for managing form interactions
 */
const useForm = (options: UseFormOptions): UseFormReturn => {
  const { 
    initialValues = {}, 
    onSubmit, 
    validate, 
    validateOnChange = false, 
    validateOnBlur = true 
  } = options;

  // Initialize form state
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  /**
   * Validates a single field and updates the errors state
   */
  const validateField = useCallback(async (field: string): Promise<string | undefined> => {
    // Skip validation if field doesn't exist in values
    if (!(field in values)) {
      return undefined;
    }

    let fieldError: string | undefined;

    if (validate) {
      // Use custom validation function if provided
      const validationErrors = await validate(values);
      fieldError = validationErrors[field];
    } else {
      // Use imported validateForm utility
      const validationErrors = validateForm(
        { [field]: values[field] }, 
        { [field]: { required: true } }
      );
      fieldError = validationErrors[field];
    }

    // Update errors state
    setErrors(prevErrors => {
      const newErrors = { ...prevErrors };
      if (fieldError) {
        newErrors[field] = fieldError;
      } else {
        delete newErrors[field];
      }
      return newErrors;
    });

    return fieldError;
  }, [validate, values]);

  /**
   * Validates all form fields and updates the errors state
   */
  const validateAllFields = useCallback(async (): Promise<Record<string, string>> => {
    let validationErrors: Record<string, string> = {};

    if (validate) {
      // Use custom validation function if provided
      validationErrors = await validate(values);
    } else {
      // Use imported validateForm utility
      validationErrors = validateForm(values, {});
    }

    setErrors(validationErrors);
    return validationErrors;
  }, [validate, values]);

  /**
   * Handles input change events and updates form values
   */
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setValues(prevValues => ({
      ...prevValues,
      [name]: fieldValue
    }));

    // If validateOnChange is enabled, validate the field immediately
    if (validateOnChange) {
      validateField(name);
    }
  }, [validateOnChange, validateField]);

  /**
   * Handles input blur events and marks fields as touched
   */
  const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name } = e.target;
    
    setTouched(prevTouched => ({
      ...prevTouched,
      [name]: true
    }));

    // If validateOnBlur is enabled, validate the field immediately
    if (validateOnBlur) {
      validateField(name);
    }
  }, [validateOnBlur, validateField]);

  /**
   * Sets a field value programmatically
   */
  const setFieldValue = useCallback((field: string, value: any) => {
    setValues(prevValues => ({
      ...prevValues,
      [field]: value
    }));

    // If validateOnChange is enabled, validate the field immediately
    if (validateOnChange) {
      validateField(field);
    }
  }, [validateOnChange, validateField]);

  /**
   * Marks a field as touched programmatically
   */
  const setFieldTouched = useCallback((field: string, isTouched: boolean = true) => {
    setTouched(prevTouched => ({
      ...prevTouched,
      [field]: isTouched
    }));

    // If validateOnBlur is enabled and the field is touched, validate immediately
    if (validateOnBlur && isTouched) {
      validateField(field);
    }
  }, [validateOnBlur, validateField]);

  /**
   * Sets a field error programmatically
   */
  const setFieldError = useCallback((field: string, error?: string) => {
    setErrors(prevErrors => {
      if (!error) {
        const newErrors = { ...prevErrors };
        delete newErrors[field];
        return newErrors;
      }
      return {
        ...prevErrors,
        [field]: error
      };
    });
  }, []);

  /**
   * Resets the form to its initial state
   */
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  /**
   * Handles form submission with validation
   */
  const handleSubmit = useCallback(async (e?: React.FormEvent<HTMLFormElement>) => {
    if (e) {
      e.preventDefault();
    }

    setIsSubmitting(true);
    
    // Validate all fields before submission
    const validationErrors = await validateAllFields();
    
    // If validation errors exist, mark fields as touched and prevent submission
    if (Object.keys(validationErrors).length > 0) {
      const touchedFields = Object.keys(validationErrors).reduce(
        (acc, key) => ({ ...acc, [key]: true }),
        {}
      );
      
      setTouched(prev => ({ ...prev, ...touchedFields }));
      setIsSubmitting(false);
      return;
    }

    // Form helpers to pass to onSubmit callback
    const formHelpers: FormHelpers = {
      setSubmitting,
      setErrors,
      resetForm
    };

    try {
      // Call onSubmit with current values and helpers
      await onSubmit(values, formHelpers);
      
      // Reset submitting state if not handled by onSubmit
      if (isSubmitting) {
        setIsSubmitting(false);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setIsSubmitting(false);
    }
  }, [onSubmit, resetForm, validateAllFields, values, isSubmitting]);

  // Run validation when values change if validateOnChange is enabled
  useEffect(() => {
    if (validateOnChange) {
      const timer = setTimeout(() => {
        validateAllFields();
      }, 200); // Debounce validation to avoid excessive validation calls
      
      return () => clearTimeout(timer);
    }
  }, [validateOnChange, validateAllFields, values]);

  // Return form state and handlers
  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    setFieldValue,
    setFieldTouched,
    setFieldError,
    validateField,
    validateForm: validateAllFields,
    resetForm,
    handleSubmit
  };
};

export default useForm;