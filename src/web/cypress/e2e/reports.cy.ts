/// <reference types="cypress" />

/**
 * End-to-end tests for the Reports functionality in the Freight Price Movement Agent
 * 
 * These tests cover the main user flows for managing reports including:
 * - Viewing the reports list
 * - Creating new reports
 * - Editing existing reports
 * - Running reports and downloading results
 * - Viewing report details
 * - Deleting reports
 * - Filtering and pagination
 * - Error handling
 * 
 * @version 1.0.0
 */

describe('Reports Management', () => {
  beforeEach(() => {
    // Login to the application
    cy.login(); // Assumes a custom command has been defined for login

    // Intercept API requests
    cy.intercept('GET', '**/api/v1/reports*').as('getReports');
    
    // Navigate to the reports page
    cy.visit('/reports');
    
    // Wait for the reports to load
    cy.wait('@getReports');
  });

  it('should display reports list correctly', () => {
    // Verify the page header
    cy.get('h1').should('contain', 'SAVED REPORTS');
    
    // Verify Create Report button exists
    cy.get('[data-cy="create-report-button"]').should('be.visible');
    
    // Verify reports table is displayed
    cy.get('[data-cy="reports-table"]').should('be.visible');
    
    // Verify table headers
    cy.get('[data-cy="reports-table"] th').should('contain', 'Name');
    cy.get('[data-cy="reports-table"] th').should('contain', 'Created');
    cy.get('[data-cy="reports-table"] th').should('contain', 'Last Run');
    cy.get('[data-cy="reports-table"] th').should('contain', 'Actions');
    
    // Verify at least one report is displayed
    cy.get('[data-cy="report-row"]').should('have.length.at.least', 1);
    
    // Verify report details
    cy.get('[data-cy="report-name"]').first().should('not.be.empty');
    cy.get('[data-cy="report-created-date"]').first().should('match', /\d{4}-\d{2}-\d{2}/);
    cy.get('[data-cy="report-actions"]').first().should('be.visible');
  });

  it('should filter reports by name', () => {
    // Intercept the filtered request
    cy.intercept('GET', '**/api/v1/reports*').as('filterReports');
    
    // Get the name of the first report to use as filter
    let filterText;
    cy.get('[data-cy="report-name"]').first().invoke('text').then((text) => {
      filterText = text.substring(0, 5); // Use first 5 characters for filtering
      
      // Type the filter text
      cy.get('[data-cy="filter-input"]').type(filterText);
      cy.get('[data-cy="apply-filter"]').click();
      
      // Wait for filtered results
      cy.wait('@filterReports');
      
      // Verify filtered results contain the filter text
      cy.get('[data-cy="report-row"]').each(($row) => {
        cy.wrap($row).find('[data-cy="report-name"]').should('contain', filterText);
      });
      
      // Clear filter
      cy.get('[data-cy="clear-filter"]').click();
      cy.wait('@filterReports');
    });
  });

  it('should create a new report', () => {
    // Intercept the POST request
    cy.intercept('POST', '**/api/v1/reports').as('createReport');
    
    // Click the Create Report button
    cy.get('[data-cy="create-report-button"]').click();
    
    // Verify navigation to create page
    cy.url().should('include', '/reports/create');
    
    // Fill in the report form
    const reportName = `Test Report ${Date.now()}`;
    cy.get('[data-cy="report-name-input"]').type(reportName);
    cy.get('[data-cy="report-description-input"]').type('Created by automated test');
    
    // Select time period
    cy.get('[data-cy="time-period-start-date"]').type('2023-01-01');
    cy.get('[data-cy="time-period-end-date"]').type('2023-03-31');
    cy.get('[data-cy="time-period-granularity-weekly"]').click();
    
    // Select data filters
    cy.get('[data-cy="data-source-select"]').select('All Sources');
    cy.get('[data-cy="origin-select"]').select('All Origins');
    cy.get('[data-cy="destination-select"]').select('All Destinations');
    
    // Select output format
    cy.get('[data-cy="output-format-json"]').click();
    
    // Include visualization
    cy.get('[data-cy="include-visualization-checkbox"]').check();
    
    // Submit form
    cy.get('[data-cy="save-report-button"]').click();
    
    // Wait for API response
    cy.wait('@createReport').its('response.statusCode').should('eq', 201);
    
    // Verify success message
    cy.get('[data-cy="success-notification"]').should('contain', 'Report created successfully');
    
    // Verify redirect to reports list
    cy.url().should('include', '/reports');
    
    // Verify new report appears in the list
    cy.get('[data-cy="report-name"]').should('contain', reportName);
  });

  it('should edit an existing report', () => {
    // Get the id of the first report
    cy.get('[data-cy="report-row"]').first().invoke('attr', 'data-report-id').then((reportId) => {
      // Intercept GET request for specific report
      cy.intercept('GET', `**/api/v1/reports/${reportId}`).as('getReport');
      
      // Intercept PUT request
      cy.intercept('PUT', `**/api/v1/reports/${reportId}`).as('updateReport');
      
      // Click edit button on first report
      cy.get('[data-cy="report-row"]').first().find('[data-cy="edit-report-button"]').click();
      
      // Verify navigation to edit page
      cy.url().should('include', `/reports/edit/${reportId}`);
      
      // Wait for report data to load
      cy.wait('@getReport');
      
      // Update report details
      const updatedName = `Updated Report ${Date.now()}`;
      cy.get('[data-cy="report-name-input"]').clear().type(updatedName);
      cy.get('[data-cy="report-description-input"]').clear().type('Updated by automated test');
      
      // Change output format
      cy.get('[data-cy="output-format-csv"]').click();
      
      // Submit form
      cy.get('[data-cy="save-report-button"]').click();
      
      // Wait for update to complete
      cy.wait('@updateReport').its('response.statusCode').should('eq', 200);
      
      // Verify success message
      cy.get('[data-cy="success-notification"]').should('contain', 'Report updated successfully');
      
      // Verify redirect to reports list
      cy.url().should('include', '/reports');
      
      // Verify updated report appears in the list
      cy.get('[data-cy="report-name"]').should('contain', updatedName);
    });
  });

  it('should run a report and download results', () => {
    // Get the id of the first report
    cy.get('[data-cy="report-row"]').first().invoke('attr', 'data-report-id').then((reportId) => {
      // Set up file download stub
      cy.window().then((win) => {
        cy.stub(win, 'open').as('windowOpen');
      });
      
      // Intercept run report request
      cy.intercept('POST', `**/api/v1/reports/${reportId}/run`, {
        statusCode: 200,
        headers: {
          'content-type': 'application/json',
          'content-disposition': 'attachment; filename=report-results.json'
        },
        body: { results: 'test data' }
      }).as('runReport');
      
      // Click run button on first report
      cy.get('[data-cy="report-row"]').first().find('[data-cy="run-report-button"]').click();
      
      // Wait for API request to complete
      cy.wait('@runReport');
      
      // Verify success message
      cy.get('[data-cy="success-notification"]').should('contain', 'Report executed successfully');
      
      // Verify download was triggered
      cy.get('@windowOpen').should('be.called');
    });
  });

  it('should view report details', () => {
    // Get the id of the first report
    cy.get('[data-cy="report-row"]').first().invoke('attr', 'data-report-id').then((reportId) => {
      // Intercept GET request for specific report
      cy.intercept('GET', `**/api/v1/reports/${reportId}`).as('getReport');
      
      // Click view button on first report
      cy.get('[data-cy="report-row"]').first().find('[data-cy="view-report-button"]').click();
      
      // Verify navigation to view page
      cy.url().should('include', `/reports/view/${reportId}`);
      
      // Wait for report data to load
      cy.wait('@getReport');
      
      // Verify report details are displayed
      cy.get('[data-cy="report-details"]').should('be.visible');
      cy.get('[data-cy="report-name-display"]').should('be.visible');
      cy.get('[data-cy="report-created-date-display"]').should('be.visible');
      cy.get('[data-cy="report-last-run-display"]').should('exist');
      
      // Check if results are available
      cy.get('body').then(($body) => {
        if ($body.find('[data-cy="report-results"]').length > 0) {
          cy.get('[data-cy="report-results"]').should('be.visible');
          
          // If visualization is enabled, check that it's displayed
          if ($body.find('[data-cy="report-visualization"]').length > 0) {
            cy.get('[data-cy="report-visualization"]').should('be.visible');
          }
        }
      });
      
      // Verify navigation back to list
      cy.get('[data-cy="back-to-list-button"]').click();
      cy.url().should('include', '/reports');
    });
  });

  it('should delete a report', () => {
    // Get name and id of the first report
    let reportName;
    cy.get('[data-cy="report-row"]').first().invoke('attr', 'data-report-id').then((reportId) => {
      cy.get('[data-cy="report-row"]').first().find('[data-cy="report-name"]').invoke('text').then((name) => {
        reportName = name;
        
        // Intercept DELETE request
        cy.intercept('DELETE', `**/api/v1/reports/${reportId}`).as('deleteReport');
        
        // Click delete button on first report
        cy.get('[data-cy="report-row"]').first().find('[data-cy="delete-report-button"]').click();
        
        // Verify confirmation modal appears
        cy.get('[data-cy="confirm-delete-modal"]').should('be.visible');
        cy.get('[data-cy="confirm-delete-modal"]').should('contain', 'Are you sure you want to delete this report?');
        
        // Confirm deletion
        cy.get('[data-cy="confirm-delete-button"]').click();
        
        // Wait for DELETE request to complete
        cy.wait('@deleteReport').its('response.statusCode').should('eq', 200);
        
        // Verify success message
        cy.get('[data-cy="success-notification"]').should('contain', 'Report deleted successfully');
        
        // Verify report is no longer in the list
        cy.get('[data-cy="report-name"]').should('not.contain', reportName);
      });
    });
  });

  it('should paginate through reports', () => {
    // Mock response for first page
    cy.intercept('GET', '**/api/v1/reports*page=1*', {
      statusCode: 200,
      body: {
        data: Array(10).fill(null).map((_, i) => ({
          id: `page1-${i}`,
          name: `Report Page 1 - ${i}`,
          created_at: '2023-01-01',
          last_run: '2023-01-02'
        })),
        pagination: {
          total: 15,
          page: 1,
          pageSize: 10,
          totalPages: 2
        }
      }
    }).as('getPage1');

    // Mock response for second page
    cy.intercept('GET', '**/api/v1/reports*page=2*', {
      statusCode: 200,
      body: {
        data: Array(5).fill(null).map((_, i) => ({
          id: `page2-${i}`,
          name: `Report Page 2 - ${i}`,
          created_at: '2023-01-01',
          last_run: '2023-01-02'
        })),
        pagination: {
          total: 15,
          page: 2,
          pageSize: 10,
          totalPages: 2
        }
      }
    }).as('getPage2');

    // Reload to trigger our mocked first page
    cy.visit('/reports');
    cy.wait('@getPage1');

    // Verify first page data
    cy.get('[data-cy="report-name"]').first().should('contain', 'Report Page 1');
    cy.get('[data-cy="pagination"]').should('be.visible');
    cy.get('[data-cy="pagination-current-page"]').should('contain', '1');

    // Go to second page
    cy.get('[data-cy="pagination-next"]').click();
    cy.wait('@getPage2');

    // Verify second page data
    cy.get('[data-cy="report-name"]').first().should('contain', 'Report Page 2');
    cy.get('[data-cy="pagination-current-page"]').should('contain', '2');

    // Go back to first page
    cy.get('[data-cy="pagination-prev"]').click();
    cy.wait('@getPage1');

    // Verify first page again
    cy.get('[data-cy="report-name"]').first().should('contain', 'Report Page 1');
    cy.get('[data-cy="pagination-current-page"]').should('contain', '1');
  });

  it('should display empty state when no reports exist', () => {
    // Mock empty reports response
    cy.intercept('GET', '**/api/v1/reports*', {
      statusCode: 200,
      body: {
        data: [],
        pagination: {
          total: 0,
          page: 1,
          pageSize: 10,
          totalPages: 0
        }
      }
    }).as('emptyReports');

    // Reload page to trigger our mock
    cy.visit('/reports');
    cy.wait('@emptyReports');

    // Verify empty state
    cy.get('[data-cy="empty-state"]').should('be.visible');
    cy.get('[data-cy="empty-state-message"]').should('contain', 'No reports found');
    
    // Verify Create Report button is still available
    cy.get('[data-cy="create-report-button"]').should('be.visible');
  });

  it('should handle API errors gracefully', () => {
    // Mock error response
    cy.intercept('GET', '**/api/v1/reports*', {
      statusCode: 500,
      body: {
        error: true,
        message: 'Internal server error'
      }
    }).as('errorReports');

    // Reload page to trigger our mock
    cy.visit('/reports');
    cy.wait('@errorReports');

    // Verify error state
    cy.get('[data-cy="error-state"]').should('be.visible');
    cy.get('[data-cy="error-message"]').should('contain', 'Error loading reports');
    cy.get('[data-cy="retry-button"]').should('be.visible');

    // Mock successful response for retry
    cy.intercept('GET', '**/api/v1/reports*', {
      statusCode: 200,
      body: {
        data: [{
          id: '1',
          name: 'Test Report',
          created_at: '2023-01-01',
          last_run: '2023-01-02'
        }],
        pagination: {
          total: 1,
          page: 1,
          pageSize: 10,
          totalPages: 1
        }
      }
    }).as('retryReports');

    // Click retry button
    cy.get('[data-cy="retry-button"]').click();
    cy.wait('@retryReports');

    // Verify reports are now displayed
    cy.get('[data-cy="reports-table"]').should('be.visible');
    cy.get('[data-cy="report-row"]').should('have.length', 1);
    cy.get('[data-cy="report-name"]').should('contain', 'Test Report');
  });
});