import React, { StrictMode } from 'react'; // version specified in the documentation
import { createRoot } from 'react-dom/client'; // version specified in the documentation
import App from './App';
import './styles/index.css';

/**
 * Optional function to report web vitals metrics for performance monitoring
 * @param {any} metric - The web vitals metric to report
 * @returns {void} No return value
 */
const reportWebVitals = (metric: any): void => {
  // Check if a web vitals reporting endpoint is configured
  if (process.env.REACT_APP_ANALYTICS_ENDPOINT) {
    // If configured, send the performance metric to the analytics endpoint
    // In a real-world application, you would send the metric to your analytics service
    // using a library like Google Analytics, Mixpanel, or a custom solution.
    // Example:
    // ga('send', 'event', 'Web Vitals', metric.name, metric.value);
    console.log(metric); // Placeholder for analytics reporting
  }

  // Log the metric to the console in development mode
  if (process.env.NODE_ENV === 'development') {
    console.log(metric);
  }
};

// Get the root DOM element with id 'root'
const rootElement = document.getElementById('root');

if (rootElement) {
  // Create a React root using createRoot API
  const root = createRoot(rootElement);

  // Render the App component wrapped in StrictMode for development checks
  root.render(
    // LD1: Wrap the App component with React.StrictMode for enhanced development checks
    <StrictMode>
      {/* LD1: Render the main App component which sets up context providers and routing */}
      <App />
    </StrictMode>
  );

  // Optionally set up web vitals reporting
  // reportWebVitals(console.log); // Example: reportWebVitals(console.log)
}