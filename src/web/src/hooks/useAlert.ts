import { useAlertContext, AlertType } from '../contexts/AlertContext';

/**
 * A custom React hook that provides alert management functionality
 * for the Freight Price Movement Agent web application.
 * 
 * This hook simplifies access to the alert context and provides an interface
 * for displaying different types of alerts and notifications.
 * 
 * @returns An object containing alert state and alert management functions
 * 
 * @example
 * const { showSuccess, showError } = useAlert();
 * 
 * // Display a success alert
 * showSuccess('Data successfully imported');
 * 
 * // Display an error alert with options
 * showError('Failed to connect to data source', {
 *   title: 'Connection Error',
 *   dismissible: true,
 *   duration: 5000
 * });
 */
const useAlert = () => {
  const {
    alerts,
    showAlert,
    hideAlert,
    clearAlerts,
    showSuccess,
    showError,
    showWarning,
    showInfo
  } = useAlertContext();

  return {
    /**
     * Current list of active alerts
     */
    alerts,

    /**
     * Show an alert with the specified type and message
     * @param type The type of alert (success, error, warning, info)
     * @param message The message to display in the alert
     * @param options Additional options like title, dismissible flag, and duration
     * @returns The ID of the created alert
     */
    showAlert,

    /**
     * Hide/remove a specific alert by ID
     * @param id The ID of the alert to hide
     */
    hideAlert,

    /**
     * Remove all active alerts
     */
    clearAlerts,

    /**
     * Show a success alert
     * @param message The message to display
     * @param options Additional options like title, dismissible flag, and duration
     * @returns The ID of the created alert
     */
    showSuccess,

    /**
     * Show an error alert
     * @param message The message to display
     * @param options Additional options like title, dismissible flag, and duration
     * @returns The ID of the created alert
     */
    showError,

    /**
     * Show a warning alert
     * @param message The message to display
     * @param options Additional options like title, dismissible flag, and duration
     * @returns The ID of the created alert
     */
    showWarning,

    /**
     * Show an info alert
     * @param message The message to display
     * @param options Additional options like title, dismissible flag, and duration
     * @returns The ID of the created alert
     */
    showInfo
  };
};

export default useAlert;