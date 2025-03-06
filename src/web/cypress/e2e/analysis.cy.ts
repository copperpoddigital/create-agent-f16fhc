/// <reference types="cypress" />

describe('Analysis Functionality', () => {
  beforeEach(() => {
    // Set up before each test
    setupAnalysisTest();
  });

  it('should load the analysis page correctly', () => {
    testAnalysisPageLoads();
  });

  it('should create a new analysis with various configurations', () => {
    testCreateNewAnalysis();
  });

  it('should display analysis results correctly', () => {
    testViewAnalysisResults();
  });

  it('should run an existing analysis', () => {
    testRunExistingAnalysis();
  });

  it('should edit an existing analysis', () => {
    testEditAnalysis();
  });

  it('should delete an analysis', () => {
    testDeleteAnalysis();
  });

  it('should filter and paginate the analysis list', () => {
    testFilteringAndPagination();
  });

  it('should export analysis results in different formats', () => {
    testExportResults();
  });
});

/**
 * Setup function that runs before each test
 */
function setupAnalysisTest() {
  // Log in as a test user
  cy.login('testuser@example.com', 'password123');

  // Intercept API requests for analysis data
  cy.intercept('GET', '/api/v1/analysis*').as('getAnalysis');

  // Navigate to the analysis page
  cy.visit('/analysis');

  // Wait for API responses to complete
  cy.wait('@getAnalysis');
}

/**
 * Test that the analysis page loads correctly
 */
function testAnalysisPageLoads() {
  // Verify we're on the correct page
  cy.url().should('include', '/analysis');

  // Verify page title
  cy.get('h1').should('contain', 'Analysis');

  // Verify New Analysis button is visible
  cy.get('[data-cy=new-analysis-btn]').should('be.visible');

  // Verify analysis table is displayed with correct columns
  cy.get('[data-cy=analysis-table]').should('be.visible');
  cy.get('[data-cy=analysis-table] th').should('contain', 'Name');
  cy.get('[data-cy=analysis-table] th').should('contain', 'Created');
  cy.get('[data-cy=analysis-table] th').should('contain', 'Last Run');
  cy.get('[data-cy=analysis-table] th').should('contain', 'Actions');

  // Verify that saved analyses are listed in the table
  cy.get('[data-cy=analysis-table] tbody tr').should('have.length.gt', 0);
}

/**
 * Test creating a new analysis with various configurations
 */
function testCreateNewAnalysis() {
  // Intercept API requests for creating a new analysis
  cy.intercept('POST', '/api/v1/analysis').as('createAnalysis');

  // Click the New Analysis button
  cy.get('[data-cy=new-analysis-btn]').click();

  // Verify we're on the new analysis page
  cy.url().should('include', '/analysis/new');

  // Test time period selection
  testTimePeriodSelection();

  // Test data filter selection
  testDataFilterSelection();

  // Test analysis options
  testAnalysisOptions();

  // Submit the analysis form
  cy.get('[data-cy=run-analysis-btn]').click();

  // Wait for API response
  cy.wait('@createAnalysis').its('response.statusCode').should('eq', 200);

  // Verify successful creation with navigation to results page
  cy.url().should('include', '/analysis/results');
}

/**
 * Test the time period selection functionality
 */
function testTimePeriodSelection() {
  // Set start date
  cy.get('[data-cy=start-date]').clear().type('2023-01-01');

  // Set end date
  cy.get('[data-cy=end-date]').clear().type('2023-03-31');

  // Select different granularity options
  cy.get('[data-cy=granularity-daily]').check();
  cy.get('[data-cy=granularity-weekly]').check();
  cy.get('[data-cy=granularity-monthly]').check();

  // Test custom interval if available
  cy.get('[data-cy=granularity-custom]').check();
  cy.get('[data-cy=custom-interval]').should('be.visible').type('3');
  cy.get('[data-cy=custom-interval-unit]').select('days');

  // Back to standard option for rest of test
  cy.get('[data-cy=granularity-weekly]').check();

  // Test validation for invalid date ranges
  cy.get('[data-cy=end-date]').clear().type('2022-12-31');
  cy.get('[data-cy=run-analysis-btn]').click();
  cy.get('[data-cy=date-error]').should('be.visible')
    .and('contain', 'End date must be after start date');

  // Fix the date for the rest of the test
  cy.get('[data-cy=end-date]').clear().type('2023-03-31');
}

/**
 * Test the data filter selection functionality
 */
function testDataFilterSelection() {
  // Test data source selection
  cy.get('[data-cy=data-source-select]').click().type('All Sources{enter}');

  // Test origin selection
  cy.get('[data-cy=origin-select]').click().type('All Origins{enter}');

  // Test destination selection
  cy.get('[data-cy=destination-select]').click().type('All Destinations{enter}');

  // Test carrier selection
  cy.get('[data-cy=carrier-select]').click().type('All Carriers{enter}');

  // Test adding additional filter
  cy.get('[data-cy=add-filter-btn]').click();
  cy.get('[data-cy=filter-type-select]').select('Transport Mode');
  cy.get('[data-cy=filter-value-select]').click().type('Ocean{enter}');

  // Test removing added filter
  cy.get('[data-cy=remove-filter-btn]').first().click();
}

/**
 * Test the analysis options selection
 */
function testAnalysisOptions() {
  // Toggle calculation options
  cy.get('[data-cy=absolute-change-checkbox]').check();
  cy.get('[data-cy=percentage-change-checkbox]').check();
  cy.get('[data-cy=trend-direction-checkbox]').check();

  // Test output format selection
  cy.get('[data-cy=output-format-json]').check();
  cy.get('[data-cy=output-format-csv]').check();
  cy.get('[data-cy=output-format-text]').check();

  // Toggle visualization option
  cy.get('[data-cy=include-visualization-checkbox]').check();
}

/**
 * Test viewing analysis results
 */
function testViewAnalysisResults() {
  // Intercept API requests for analysis results
  cy.intercept('GET', '/api/v1/analysis/*/results').as('getResults');

  // Click on a completed analysis in the list
  cy.get('[data-cy=analysis-table] tbody tr')
    .first()
    .find('[data-cy=view-analysis-btn]')
    .click();

  // Wait for API response
  cy.wait('@getResults');

  // Verify we're on the analysis results page
  cy.url().should('include', '/analysis/results');

  // Verify the summary section displays correctly
  cy.get('[data-cy=results-summary]').should('be.visible');
  cy.get('[data-cy=time-period]').should('be.visible');
  cy.get('[data-cy=overall-change]').should('be.visible');
  cy.get('[data-cy=absolute-change]').should('be.visible');

  // Verify the chart is rendered
  cy.get('[data-cy=price-movement-chart]').should('be.visible');
  cy.get('canvas').should('be.visible');

  // Verify the detailed results table is displayed
  cy.get('[data-cy=detailed-results-table]').should('be.visible');
  cy.get('[data-cy=detailed-results-table] th').should('contain', 'Week');
  cy.get('[data-cy=detailed-results-table] th').should('contain', 'Price');
  cy.get('[data-cy=detailed-results-table] th').should('contain', 'Abs Change');
  cy.get('[data-cy=detailed-results-table] th').should('contain', '% Change');

  // Test the export buttons are available
  cy.get('[data-cy=export-btn]').should('be.visible');
  cy.get('[data-cy=save-btn]').should('be.visible');
}

/**
 * Test running an existing analysis
 */
function testRunExistingAnalysis() {
  // Intercept API requests for running an analysis
  cy.intercept('POST', '/api/v1/analysis/*/run').as('runAnalysis');

  // Click the run button for an existing analysis
  cy.get('[data-cy=analysis-table] tbody tr')
    .first()
    .find('[data-cy=run-analysis-btn]')
    .click();

  // Verify the confirmation modal appears
  cy.get('[data-cy=confirm-modal]').should('be.visible');
  cy.get('[data-cy=confirm-modal-title]').should('contain', 'Run Analysis');

  // Confirm running the analysis
  cy.get('[data-cy=confirm-btn]').click();

  // Wait for API response
  cy.wait('@runAnalysis').its('response.statusCode').should('eq', 200);

  // Verify the analysis status changes to "Running"
  cy.get('[data-cy=analysis-status]').should('contain', 'Running');

  // Intercept API requests for analysis completion
  cy.intercept('GET', '/api/v1/analysis/*/status').as('checkStatus');

  // Wait for the analysis to complete (polling)
  cy.wait('@checkStatus').then(({ response }) => {
    if (response.body.status !== 'Completed') {
      // If not completed, wait for next status check
      cy.wait('@checkStatus');
    }
  });

  // Verify navigation to results page when complete
  cy.url().should('include', '/analysis/results');
}

/**
 * Test editing an existing analysis
 */
function testEditAnalysis() {
  // Intercept API requests for editing an analysis
  cy.intercept('PUT', '/api/v1/analysis/*').as('updateAnalysis');

  // Click the edit button for an existing analysis
  cy.get('[data-cy=analysis-table] tbody tr')
    .first()
    .find('[data-cy=edit-analysis-btn]')
    .click();

  // Verify we're on the edit analysis page
  cy.url().should('include', '/analysis/edit');

  // Modify analysis parameters
  cy.get('[data-cy=analysis-name]').clear().type('Updated Analysis Name');
  cy.get('[data-cy=granularity-daily]').check();

  // Submit the updated form
  cy.get('[data-cy=save-analysis-btn]').click();

  // Wait for API response
  cy.wait('@updateAnalysis').its('response.statusCode').should('eq', 200);

  // Verify successful update with navigation to results page
  cy.url().should('include', '/analysis/results');
}

/**
 * Test deleting an analysis
 */
function testDeleteAnalysis() {
  // Intercept API requests for deleting an analysis
  cy.intercept('DELETE', '/api/v1/analysis/*').as('deleteAnalysis');

  // Get the name of the analysis to be deleted for verification
  cy.get('[data-cy=analysis-table] tbody tr')
    .last()
    .find('[data-cy=analysis-name]')
    .invoke('text')
    .as('deletedAnalysisName');

  // Click the delete button for an existing analysis
  cy.get('[data-cy=analysis-table] tbody tr')
    .last()
    .find('[data-cy=delete-analysis-btn]')
    .click();

  // Verify the confirmation modal appears
  cy.get('[data-cy=confirm-modal]').should('be.visible');
  cy.get('[data-cy=confirm-modal-title]').should('contain', 'Delete Analysis');

  // Confirm the deletion
  cy.get('[data-cy=confirm-btn]').click();

  // Wait for API response
  cy.wait('@deleteAnalysis').its('response.statusCode').should('eq', 200);

  // Verify successful deletion with removal from the list
  cy.get('@deletedAnalysisName').then((analysisName) => {
    cy.get('[data-cy=analysis-table] tbody').should('not.contain', analysisName);
  });

  // Verify success notification is displayed
  cy.get('[data-cy=notification]').should('be.visible')
    .and('contain', 'Analysis deleted successfully');
}

/**
 * Test filtering and pagination of analysis list
 */
function testFilteringAndPagination() {
  // Intercept API requests for filtered and paginated data
  cy.intercept('GET', '/api/v1/analysis*').as('getFilteredAnalysis');

  // Test filtering
  cy.get('[data-cy=filter-input]').type('Ocean');
  cy.wait('@getFilteredAnalysis');

  // Verify filtered results match the search criteria
  cy.get('[data-cy=analysis-table] tbody tr').each(($row) => {
    cy.wrap($row).should('contain', 'Ocean');
  });

  // Clear filter
  cy.get('[data-cy=clear-filter-btn]').click();
  cy.wait('@getFilteredAnalysis');

  // Test pagination if there are multiple pages
  cy.get('[data-cy=pagination]').then($pagination => {
    if ($pagination.find('[data-cy=next-page-btn]').length > 0) {
      // Click next page button
      cy.get('[data-cy=next-page-btn]').click();
      cy.wait('@getFilteredAnalysis');

      // Verify page has changed
      cy.get('[data-cy=current-page]').should('not.contain', '1');

      // Click previous page button
      cy.get('[data-cy=prev-page-btn]').click();
      cy.wait('@getFilteredAnalysis');

      // Verify we're back on page 1
      cy.get('[data-cy=current-page]').should('contain', '1');
    }
  });

  // Test combination of filtering and pagination
  cy.get('[data-cy=filter-input]').type('Air');
  cy.wait('@getFilteredAnalysis');

  // If there are multiple pages of filtered results, test pagination
  cy.get('[data-cy=pagination]').then($pagination => {
    if ($pagination.find('[data-cy=next-page-btn]').length > 0) {
      cy.get('[data-cy=next-page-btn]').click();
      cy.wait('@getFilteredAnalysis');

      // Verify filtered results on second page also match criteria
      cy.get('[data-cy=analysis-table] tbody tr').each(($row) => {
        cy.wrap($row).should('contain', 'Air');
      });
    }
  });
}

/**
 * Test exporting analysis results in different formats
 */
function testExportResults() {
  // Navigate to an analysis results page
  cy.get('[data-cy=analysis-table] tbody tr')
    .first()
    .find('[data-cy=view-analysis-btn]')
    .click();

  // Intercept file download requests
  cy.intercept('GET', '/api/v1/analysis/*/export?format=json').as('exportJson');
  cy.intercept('GET', '/api/v1/analysis/*/export?format=csv').as('exportCsv');
  cy.intercept('GET', '/api/v1/analysis/*/export?format=text').as('exportText');

  // Open export dropdown
  cy.get('[data-cy=export-btn]').click();

  // Test exporting in JSON format
  cy.get('[data-cy=export-json-btn]').click();
  cy.wait('@exportJson').its('response.statusCode').should('eq', 200);

  // Test exporting in CSV format
  cy.get('[data-cy=export-btn]').click();
  cy.get('[data-cy=export-csv-btn]').click();
  cy.wait('@exportCsv').its('response.statusCode').should('eq', 200);

  // Test exporting in Text format
  cy.get('[data-cy=export-btn]').click();
  cy.get('[data-cy=export-text-btn]').click();
  cy.wait('@exportText').its('response.statusCode').should('eq', 200);
}