// This file is automatically loaded by Cypress as specified in cypress.config.ts
// and serves as the main entry point for test support configuration.

// Import Testing Library extensions for Cypress
import '@testing-library/cypress';

// Import cypress-real-events for simulating real user events
import 'cypress-real-events';

// Import custom commands
import './commands';

/**
 * Configure global behavior for all Cypress tests in the Freight Price Movement Agent
 */
function setupGlobalBehavior(): void {
  // Preserve cookies between tests to maintain user session
  Cypress.Cookies.defaults({
    preserve: ['access_token', 'refresh_token', 'session_id'],
  });

  // Configure global handling for uncaught exceptions
  Cypress.on('uncaught:exception', (err, runnable) => {
    // Log the error for debugging purposes
    console.error('Uncaught exception:', err.message);
    
    // Returning false prevents Cypress from failing the test
    // This is useful for handling third-party script errors
    return false;
  });

  // Set consistent viewport size for all tests
  // This matches a standard laptop screen resolution
  Cypress.viewport(1280, 720);

  // Configure retry behavior for flaky tests
  Cypress.config('retries', {
    runMode: 2,     // Retry failed tests twice in CI/run mode
    openMode: 0     // Don't retry in development mode (Cypress UI open)
  });

  // Set appropriate timeouts for the Freight Price Movement Agent application
  Cypress.config({
    defaultCommandTimeout: 10000,  // Default timeout for most commands (10s)
    requestTimeout: 15000,         // Timeout for network requests (15s)
    pageLoadTimeout: 30000,        // Timeout for page loads (30s)
    responseTimeout: 30000,        // Timeout for responses (30s)
    execTimeout: 60000,            // Timeout for executing system commands (60s)
  });
}

// Execute the configuration function to set up global behavior
setupGlobalBehavior();