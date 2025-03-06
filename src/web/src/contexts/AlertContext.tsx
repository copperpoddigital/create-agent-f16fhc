import React, { createContext, useContext, useState, useCallback, ReactNode, FC } from 'react';
import { v4 as uuidv4 } from 'uuid'; // v9.0.0
import Alert from '../components/common/Alert';

/**
 * Enum defining the available alert types
 */
export enum AlertType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

/**
 * Interface defining the structure of an alert object
 */
export interface Alert {
  id: string;
  type: AlertType;
  message: string;
  title?: string;
  dismissible: boolean;
  createdAt: number;
}

/**
 * Interface defining the alert context value
 */
export interface AlertContextType {
  alerts: Alert[];
  showAlert: (type: AlertType, message: string, options?: { title?: string, dismissible?: boolean, duration?: number }) => string;
  hideAlert: (id: string) => void;
  clearAlerts: () => void;
  showSuccess: (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }) => string;
  showError: (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }) => string;
  showWarning: (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }) => string;
  showInfo: (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }) => string;
}

// Create initial context
const initialAlertContext: AlertContextType = {
  alerts: [],
  showAlert: () => '',
  hideAlert: () => {},
  clearAlerts: () => {},
  showSuccess: () => '',
  showError: () => '',
  showWarning: () => '',
  showInfo: () => ''
};

// Create context
export const AlertContext = createContext<AlertContextType>(initialAlertContext);

/**
 * Provider component that makes alert context available to child components
 */
export const AlertProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  /**
   * Displays a new alert with the specified type, message, and options
   * @param type The type of alert to display
   * @param message The message to display in the alert
   * @param options Additional options for the alert
   * @returns The ID of the newly created alert
   */
  const showAlert = useCallback((
    type: AlertType, 
    message: string, 
    options?: { title?: string, dismissible?: boolean, duration?: number }
  ): string => {
    const id = uuidv4();
    const newAlert: Alert = {
      id,
      type,
      message,
      title: options?.title,
      dismissible: options?.dismissible ?? true,
      createdAt: Date.now()
    };
    
    setAlerts(prevAlerts => [...prevAlerts, newAlert]);
    
    // Automatically dismiss alert after duration (if provided)
    if (options?.duration) {
      setTimeout(() => {
        hideAlert(id);
      }, options.duration);
    }
    
    return id;
  }, []);

  /**
   * Removes an alert with the specified ID
   * @param id The ID of the alert to remove
   */
  const hideAlert = useCallback((id: string): void => {
    setAlerts(prevAlerts => prevAlerts.filter(alert => alert.id !== id));
  }, []);
  
  /**
   * Removes all alerts from the state
   */
  const clearAlerts = useCallback((): void => {
    setAlerts([]);
  }, []);
  
  /**
   * Convenience method to show a success alert
   * @param message The message to display
   * @param options Additional options for the alert
   * @returns The ID of the newly created alert
   */
  const showSuccess = useCallback(
    (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }): string => 
      showAlert(AlertType.SUCCESS, message, options),
    [showAlert]
  );
  
  /**
   * Convenience method to show an error alert
   * @param message The message to display
   * @param options Additional options for the alert
   * @returns The ID of the newly created alert
   */
  const showError = useCallback(
    (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }): string => 
      showAlert(AlertType.ERROR, message, options),
    [showAlert]
  );
  
  /**
   * Convenience method to show a warning alert
   * @param message The message to display
   * @param options Additional options for the alert
   * @returns The ID of the newly created alert
   */
  const showWarning = useCallback(
    (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }): string => 
      showAlert(AlertType.WARNING, message, options),
    [showAlert]
  );
  
  /**
   * Convenience method to show an info alert
   * @param message The message to display
   * @param options Additional options for the alert
   * @returns The ID of the newly created alert
   */
  const showInfo = useCallback(
    (message: string, options?: { title?: string, dismissible?: boolean, duration?: number }): string => 
      showAlert(AlertType.INFO, message, options),
    [showAlert]
  );

  const contextValue: AlertContextType = {
    alerts,
    showAlert,
    hideAlert,
    clearAlerts,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };

  return (
    <AlertContext.Provider value={contextValue}>
      {children}
    </AlertContext.Provider>
  );
};

/**
 * Custom hook to access the alert context
 * @returns The alert context value
 * @throws Error if used outside of an AlertProvider
 */
export const useAlertContext = (): AlertContextType => {
  const context = useContext(AlertContext);
  
  if (!context) {
    throw new Error('useAlertContext must be used within an AlertProvider');
  }
  
  return context;
};