// Import Cypress and Testing Library extensions for better DOM querying
import '@testing-library/cypress/add-commands';

// Type declarations for custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to log in to the application
       * @param username - The username to log in with
       * @param password - The password to log in with
       * @example cy.login('admin', 'password123')
       */
      login(username: string, password: string): Chainable<void>;
      
      /**
       * Custom command to create a new data source
       * @param name - The name of the data source
       * @param type - The type of data source (CSV File, Database, API)
       * @param options - Additional options for the data source
       * @example cy.createDataSource('TMS Export', 'CSV File', { filePath: 'fixtures/sample.csv' })
       */
      createDataSource(name: string, type: string, options?: any): Chainable<string>;
      
      /**
       * Custom command to delete a data source by ID
       * @param id - The ID of the data source to delete
       * @example cy.deleteDataSource('123e4567-e89b-12d3-a456-426614174000')
       */
      deleteDataSource(id: string): Chainable<void>;
      
      /**
       * Custom command to select a data source from a list
       * @param name - The name of the data source to select
       * @example cy.selectDataSource('TMS Export')
       */
      selectDataSource(name: string): Chainable<void>;
      
      /**
       * Custom command to create a new analysis
       * @param name - The name of the analysis
       * @param options - Additional options for the analysis configuration
       * @example cy.createAnalysis('Q1 Ocean Rates', { startDate: '2023-01-01', endDate: '2023-03-31' })
       */
      createAnalysis(name: string, options?: any): Chainable<string>;
      
      /**
       * Custom command to run an analysis by ID
       * @param id - The ID of the analysis to run
       * @example cy.runAnalysis('123e4567-e89b-12d3-a456-426614174000')
       */
      runAnalysis(id: string): Chainable<void>;
      
      /**
       * Custom command to view analysis results
       * @param id - The ID of the analysis to view
       * @example cy.viewAnalysisResults('123e4567-e89b-12d3-a456-426614174000')
       */
      viewAnalysisResults(id: string): Chainable<void>;
      
      /**
       * Custom command to configure time period for analysis
       * @param startDate - The start date in YYYY-MM-DD format
       * @param endDate - The end date in YYYY-MM-DD format
       * @param granularity - The granularity (Daily, Weekly, Monthly, Custom)
       * @example cy.configureTimePeriod('2023-01-01', '2023-03-31', 'Weekly')
       */
      configureTimePeriod(startDate: string, endDate: string, granularity: string): Chainable<void>;
      
      /**
       * Custom command to wait for a specific API request to complete
       * @param method - The HTTP method (GET, POST, PUT, DELETE)
       * @param url - The URL pattern to intercept
       * @example cy.waitForRequest('POST', '/api/v1/analysis')
       */
      waitForRequest(method: string, url: string): Chainable<any>;
      
      /**
       * Custom command to select an option from a dropdown
       * @param label - The label of the dropdown
       * @param option - The option to select
       * @example cy.selectFromDropdown('Data Source', 'TMS Export')
       */
      selectFromDropdown(label: string, option: string): Chainable<void>;
      
      /**
       * Custom command to check table contents against expected data
       * @param selector - The table selector
       * @param expectedData - The expected data array
       * @example cy.checkTableContents('table.results', [{ name: 'Example', value: '100' }])
       */
      checkTableContents(selector: string, expectedData: any[]): Chainable<void>;
      
      /**
       * Custom command to verify a toast notification
       * @param message - The expected message
       * @param type - The type of toast (success, error, warning, info)
       * @example cy.verifyToast('Operation successful', 'success')
       */
      verifyToast(message: string, type?: string): Chainable<void>;
      
      /**
       * Custom command to navigate to a specific page
       * @param page - The page to navigate to
       * @example cy.navigateTo('dashboard')
       */
      navigateTo(page: string): Chainable<void>;
      
      /**
       * Custom command to navigate to the data sources page
       * @example cy.navigateToDataSources()
       */
      navigateToDataSources(): Chainable<void>;
      
      /**
       * Custom command to navigate to the analysis page
       * @example cy.navigateToAnalysis()
       */
      navigateToAnalysis(): Chainable<void>;
      
      /**
       * Custom command to navigate to the reports page
       * @example cy.navigateToReports()
       */
      navigateToReports(): Chainable<void>;
      
      /**
       * Custom command to navigate to the settings page
       * @example cy.navigateToSettings()
       */
      navigateToSettings(): Chainable<void>;
    }
  }
}

/**
 * Registers a custom command for user login
 */
function registerLoginCommand(): void {
  Cypress.Commands.add('login', (username: string, password: string) => {
    // Intercept auth endpoint
    cy.intercept('POST', '/api/v1/auth/token').as('loginRequest');
    
    // Navigate to login page
    cy.visit('/login');
    
    // Fill the login form
    cy.findByLabelText('Username').type(username);
    cy.findByLabelText('Password').type(password);
    
    // Submit the form
    cy.findByRole('button', { name: /login/i }).click();
    
    // Wait for the login request to complete
    cy.wait('@loginRequest').then((interception) => {
      // Verify successful login - should redirect to dashboard
      cy.url().should('include', '/dashboard');
      
      // Store the token in local storage for future requests
      if (interception.response?.statusCode === 200 && interception.response?.body?.access_token) {
        localStorage.setItem('access_token', interception.response.body.access_token);
      }
    });
  });
}

/**
 * Registers custom commands for data source management
 */
function registerDataSourceCommands(): void {
  // Create data source command
  Cypress.Commands.add('createDataSource', (name: string, type: string, options = {}) => {
    // Navigate to data sources page
    cy.navigateToDataSources();
    
    // Click add data source button
    cy.findByRole('button', { name: /add source/i }).click();
    
    // Fill the form
    cy.findByLabelText('Name').type(name);
    cy.selectFromDropdown('Source Type', type);
    
    // Handle different data source types
    if (type === 'CSV File') {
      // Upload file if provided
      if (options.filePath) {
        cy.get('input[type="file"]').attachFile(options.filePath);
      }
      
      // Configure date format if provided
      if (options.dateFormat) {
        cy.selectFromDropdown('Date Format', options.dateFormat);
      }
      
      // Configure field mappings
      if (options.fieldMappings) {
        Object.entries(options.fieldMappings).forEach(([field, mappedField]) => {
          cy.selectFromDropdown(`Field Mapping: ${field}`, String(mappedField));
        });
      }
    } else if (type === 'Database') {
      // Handle database configuration
      if (options.connectionString) {
        cy.findByLabelText('Connection String').type(options.connectionString);
      }
      if (options.username) {
        cy.findByLabelText('Username').type(options.username);
      }
      if (options.password) {
        cy.findByLabelText('Password').type(options.password);
      }
    } else if (type === 'API') {
      // Handle API configuration
      if (options.endpoint) {
        cy.findByLabelText('Endpoint URL').type(options.endpoint);
      }
      if (options.apiKey) {
        cy.findByLabelText('API Key').type(options.apiKey);
      }
    }
    
    // Test connection if needed
    if (options.testConnection) {
      cy.findByRole('button', { name: /test connection/i }).click();
      cy.verifyToast('Connection successful', 'success');
    }
    
    // Intercept the create data source request
    cy.intercept('POST', '/api/v1/data/sources').as('createDataSourceRequest');
    
    // Save the data source
    cy.findByRole('button', { name: /save source/i }).click();
    
    // Wait for the request to complete and return the created ID
    return cy.wait('@createDataSourceRequest').then((interception) => {
      if (interception.response?.statusCode === 201 && interception.response?.body?.id) {
        return interception.response.body.id;
      }
      return null;
    });
  });
  
  // Delete data source command
  Cypress.Commands.add('deleteDataSource', (id: string) => {
    cy.navigateToDataSources();
    
    // Intercept the delete request
    cy.intercept('DELETE', `/api/v1/data/sources/${id}`).as('deleteDataSourceRequest');
    
    // Find and click the delete button for the specific data source
    cy.get(`[data-cy="data-source-${id}"] [data-cy="delete-button"]`).click();
    
    // Confirm deletion in the dialog
    cy.findByRole('button', { name: /confirm/i }).click();
    
    // Wait for the delete request to complete
    cy.wait('@deleteDataSourceRequest');
    
    // Verify the data source is no longer in the list
    cy.get(`[data-cy="data-source-${id}"]`).should('not.exist');
  });
  
  // Select data source command
  Cypress.Commands.add('selectDataSource', (name: string) => {
    cy.navigateToDataSources();
    
    // Find the data source by name and click it
    cy.findByText(name).click();
  });
}

/**
 * Registers custom commands for analysis operations
 */
function registerAnalysisCommands(): void {
  // Create analysis command
  Cypress.Commands.add('createAnalysis', (name: string, options = {}) => {
    cy.navigateToAnalysis();
    
    // Click the "New Analysis" button
    cy.findByRole('button', { name: /new analysis/i }).click();
    
    // Configure time period if options provided
    if (options.startDate && options.endDate) {
      cy.configureTimePeriod(
        options.startDate,
        options.endDate,
        options.granularity || 'Weekly'
      );
    }
    
    // Configure data filters if provided
    if (options.filters) {
      if (options.filters.dataSource) {
        cy.selectFromDropdown('Data Source', options.filters.dataSource);
      }
      if (options.filters.origin) {
        cy.selectFromDropdown('Origin', options.filters.origin);
      }
      if (options.filters.destination) {
        cy.selectFromDropdown('Destination', options.filters.destination);
      }
      if (options.filters.carrier) {
        cy.selectFromDropdown('Carrier', options.filters.carrier);
      }
    }
    
    // Configure analysis options
    if (options.analysisOptions) {
      if (options.analysisOptions.calculateAbsoluteChange !== undefined) {
        const checkbox = cy.get('[name="calculateAbsoluteChange"]');
        options.analysisOptions.calculateAbsoluteChange ? checkbox.check() : checkbox.uncheck();
      }
      
      if (options.analysisOptions.calculatePercentageChange !== undefined) {
        const checkbox = cy.get('[name="calculatePercentageChange"]');
        options.analysisOptions.calculatePercentageChange ? checkbox.check() : checkbox.uncheck();
      }
      
      if (options.analysisOptions.identifyTrendDirection !== undefined) {
        const checkbox = cy.get('[name="identifyTrendDirection"]');
        options.analysisOptions.identifyTrendDirection ? checkbox.check() : checkbox.uncheck();
      }
      
      if (options.analysisOptions.compareToHistoricalBaseline) {
        cy.get('[name="compareToHistoricalBaseline"]').check();
        if (options.analysisOptions.baselinePeriod) {
          cy.findByLabelText('Baseline period').type(options.analysisOptions.baselinePeriod);
        }
      }
      
      // Configure output format
      if (options.analysisOptions.outputFormat) {
        cy.get(`[name="outputFormat"][value="${options.analysisOptions.outputFormat}"]`).check();
      }
      
      // Configure visualization
      if (options.analysisOptions.includeVisualization !== undefined) {
        const checkbox = cy.get('[name="includeVisualization"]');
        options.analysisOptions.includeVisualization ? checkbox.check() : checkbox.uncheck();
      }
    }
    
    // Intercept the create analysis request
    cy.intercept('POST', '/api/v1/analysis').as('createAnalysisRequest');
    
    // Run the analysis
    cy.findByRole('button', { name: /run analysis/i }).click();
    
    // Wait for the request to complete and return the created ID
    return cy.wait('@createAnalysisRequest').then((interception) => {
      if (interception.response?.statusCode === 201 && interception.response?.body?.id) {
        return interception.response.body.id;
      }
      return null;
    });
  });
  
  // Run analysis command
  Cypress.Commands.add('runAnalysis', (id: string) => {
    cy.navigateToAnalysis();
    
    // Intercept the analysis execution request
    cy.intercept('POST', `/api/v1/analysis/${id}/run`).as('runAnalysisRequest');
    
    // Find and click the run button for the specific analysis
    cy.get(`[data-cy="analysis-${id}"] [data-cy="run-button"]`).click();
    
    // Wait for the analysis to complete
    cy.wait('@runAnalysisRequest');
    
    // Verify the analysis completes successfully
    cy.verifyToast('Analysis completed successfully', 'success');
  });
  
  // View analysis results command
  Cypress.Commands.add('viewAnalysisResults', (id: string) => {
    cy.navigateToAnalysis();
    
    // Find and click on the analysis to view its results
    cy.get(`[data-cy="analysis-${id}"]`).click();
    
    // Verify we're on the results page
    cy.url().should('include', `/analysis/${id}/results`);
  });
  
  // Configure time period command
  Cypress.Commands.add('configureTimePeriod', (startDate: string, endDate: string, granularity: string) => {
    // Fill start date
    cy.findByLabelText('Start Date').clear().type(startDate);
    
    // Fill end date
    cy.findByLabelText('End Date').clear().type(endDate);
    
    // Select granularity
    if (granularity === 'Daily') {
      cy.get('[name="granularity"][value="daily"]').check();
    } else if (granularity === 'Weekly') {
      cy.get('[name="granularity"][value="weekly"]').check();
    } else if (granularity === 'Monthly') {
      cy.get('[name="granularity"][value="monthly"]').check();
    } else if (granularity === 'Custom') {
      cy.get('[name="granularity"][value="custom"]').check();
      // If custom interval is provided, set it
      if (typeof granularity === 'object' && granularity.interval) {
        cy.findByLabelText('Custom interval').type(granularity.interval);
      }
    }
  });
}

/**
 * Registers utility commands for common testing operations
 */
function registerUtilityCommands(): void {
  // Wait for request command
  Cypress.Commands.add('waitForRequest', (method: string, url: string) => {
    cy.intercept(method, url).as('waitedRequest');
    return cy.wait('@waitedRequest');
  });
  
  // Select from dropdown command
  Cypress.Commands.add('selectFromDropdown', (label: string, option: string) => {
    cy.findByLabelText(label).click();
    cy.findByText(option).click();
  });
  
  // Check table contents command
  Cypress.Commands.add('checkTableContents', (selector: string, expectedData: any[]) => {
    cy.get(selector).within(() => {
      // Check number of rows
      cy.get('tbody tr').should('have.length', expectedData.length);
      
      // Check each row's content
      expectedData.forEach((rowData, rowIndex) => {
        cy.get(`tbody tr:nth-child(${rowIndex + 1})`).within(() => {
          Object.values(rowData).forEach((cellValue, cellIndex) => {
            cy.get(`td:nth-child(${cellIndex + 1})`).should('contain', cellValue);
          });
        });
      });
    });
  });
  
  // Verify toast notification command
  Cypress.Commands.add('verifyToast', (message: string, type = '') => {
    if (type) {
      cy.get(`.toast.toast-${type}`).should('contain', message);
    } else {
      cy.get('.toast').should('contain', message);
    }
  });
}

/**
 * Registers commands for navigation within the application
 */
function registerNavigationCommands(): void {
  // Generic navigation command
  Cypress.Commands.add('navigateTo', (page: string) => {
    cy.visit(`/${page.toLowerCase()}`);
  });
  
  // Specific navigation commands
  Cypress.Commands.add('navigateToDataSources', () => {
    cy.visit('/data-sources');
  });
  
  Cypress.Commands.add('navigateToAnalysis', () => {
    cy.visit('/analysis');
  });
  
  Cypress.Commands.add('navigateToReports', () => {
    cy.visit('/reports');
  });
  
  Cypress.Commands.add('navigateToSettings', () => {
    cy.visit('/settings');
  });
}

// Register all custom commands
registerLoginCommand();
registerDataSourceCommands();
registerAnalysisCommands();
registerUtilityCommands();
registerNavigationCommands();