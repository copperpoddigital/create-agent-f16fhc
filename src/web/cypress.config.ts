import { defineConfig } from 'cypress'; // cypress version: ^12.10.0

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    video: false,
    screenshotOnRunFailure: true,
    trashAssetsBeforeRuns: true,
    setupNodeEvents(on, config) {
      // Register event listeners for test events
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
        table(data) {
          console.table(data);
          return null;
        }
      });

      // Configure environment-specific settings
      const environment = process.env.NODE_ENV || 'development';
      
      // Set environment-specific configurations
      if (environment === 'ci') {
        // CI-specific configurations
        config.baseUrl = process.env.CI_BASE_URL || config.baseUrl;
        config.env.apiUrl = process.env.CI_API_URL || config.env.apiUrl;
        config.video = true; // Enable video recording in CI environment
      }

      // Return the modified config
      return config;
    },
  },
  
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: '**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.ts',
  },
  
  env: {
    apiUrl: 'http://localhost:5000/api/v1',
    testUsername: 'test@example.com',
    testPassword: 'TestPassword123'
  },
  
  retries: {
    runMode: 2, // Retry failed tests twice in run mode (CI)
    openMode: 0  // Don't retry in open mode (dev)
  }
});