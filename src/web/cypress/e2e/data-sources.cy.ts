/**
 * Cypress end-to-end tests for the Data Sources functionality
 * in the Freight Price Movement Agent application
 * 
 * Tests include viewing, adding, editing, deleting data sources,
 * as well as filtering and pagination features.
 * 
 * @package cypress ^12.0.0
 */

describe('Data Sources Management', () => {
  /**
   * Setup before each test case
   * - Login to the application
   * - Navigate to data sources page
   * - Wait for initial data to load
   */
  beforeEach(() => {
    // Login using custom Cypress command
    cy.login();
    
    // Intercept API requests for data sources
    cy.intercept('GET', '/api/v1/data-sources*').as('getDataSources');
    
    // Navigate to data sources page
    cy.visit('/data-sources');
    
    // Wait for data to load
    cy.wait('@getDataSources');
  });

  /**
   * Test: Verify that the data sources page displays correctly
   * with proper elements and data
   */
  it('should display a list of data sources', () => {
    // Verify page title is displayed
    cy.contains('DATA SOURCES').should('be.visible');
    
    // Verify "Add Source" button is present
    cy.contains('button', 'Add Source').should('be.visible');
    
    // Verify filter input exists
    cy.get('input[placeholder*="FILTER"]').should('be.visible');
    cy.contains('button', 'Apply').should('be.visible');
    cy.contains('button', 'Clear').should('be.visible');
    
    // Verify data sources table exists
    cy.get('table').should('be.visible');
    
    // Verify table headers
    cy.contains('th', 'Name').should('be.visible');
    cy.contains('th', 'Type').should('be.visible');
    cy.contains('th', 'Last Update').should('be.visible');
    cy.contains('th', 'Status').should('be.visible');
    cy.contains('th', 'Actions').should('be.visible');
    
    // Verify at least one data source is displayed
    cy.get('table tbody tr').should('have.length.at.least', 1);
    
    // Verify data source details are displayed correctly
    cy.get('table tbody tr').first().within(() => {
      // Verify name is not empty
      cy.get('td').eq(0).should('not.be.empty');
      
      // Verify type is displayed (CSV, Database, API, etc.)
      cy.get('td').eq(1).should('not.be.empty');
      
      // Verify last update date is displayed
      cy.get('td').eq(2).should('not.be.empty');
      
      // Verify status is displayed (Active, Warning, Inactive)
      cy.get('td').eq(3).should('not.be.empty');
      
      // Verify action buttons are present
      cy.get('td').eq(4).find('button, a').should('have.length.at.least', 2);
    });
    
    // Verify pagination controls
    cy.contains('Page').should('be.visible');
    cy.contains('< Previous').should('be.visible');
    cy.contains('Next >').should('be.visible');
  });

  /**
   * Test: Verify that filtering functionality works correctly
   */
  it('should filter data sources correctly', () => {
    // Intercept the filtered data request
    cy.intercept('GET', '/api/v1/data-sources*').as('filterDataSources');
    
    // Count initial number of data sources
    cy.get('table tbody tr').its('length').as('initialRowCount');
    
    // Type a search term in the filter input
    cy.get('input[placeholder*="FILTER"]').type('TMS');
    
    // Click Apply button to filter
    cy.contains('button', 'Apply').click();
    
    // Wait for filtered results
    cy.wait('@filterDataSources');
    
    // Verify that filtered results contain the search term
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).should('contain', 'TMS');
    });
    
    // Clear the filter
    cy.contains('button', 'Clear').click();
    cy.wait('@filterDataSources');
    
    // Verify original count of data sources is restored
    cy.get('@initialRowCount').then(initialCount => {
      cy.get('table tbody tr').should('have.length', Number(initialCount));
    });
  });

  /**
   * Test: Verify adding a new data source
   */
  it('should add a new data source', () => {
    // Intercept the POST request for creating a data source
    cy.intercept('POST', '/api/v1/data-sources').as('createDataSource');
    
    // Click the "Add Source" button
    cy.contains('button', 'Add Source').click();
    
    // Verify navigation to add data source page
    cy.url().should('include', '/data-sources/add');
    cy.contains('ADD DATA SOURCE').should('be.visible');
    
    // Generate a unique name for the data source
    const sourceName = `Test CSV Source ${Date.now()}`;
    
    // Fill in source details
    cy.get('input[name="name"]').type(sourceName);
    cy.get('select[name="sourceType"]').select('CSV File');
    cy.get('textarea[name="description"]').type('This is a test data source for E2E testing');
    
    // Upload a CSV file
    cy.get('input[type="file"]').attachFile('test-data.csv');
    
    // Select date format
    cy.get('select[name="dateFormat"]').select('YYYY-MM-DD');
    
    // Map fields
    cy.get('select[name="freightChargeField"]').select('price');
    cy.get('select[name="currencyField"]').select('currency_code');
    cy.get('select[name="originField"]').select('origin');
    cy.get('select[name="destinationField"]').select('destination');
    cy.get('select[name="dateTimeField"]').select('quote_date');
    
    // Test connection
    cy.contains('button', 'Test Connection').click();
    cy.contains('Connection successful').should('be.visible', { timeout: 10000 });
    
    // Save the data source
    cy.contains('button', 'Save Source').click();
    
    // Wait for the creation API request to complete
    cy.wait('@createDataSource').its('response.statusCode').should('eq', 201);
    
    // Verify success notification
    cy.contains('Data source created successfully').should('be.visible');
    
    // Verify navigation back to data sources list
    cy.url().should('include', '/data-sources').and('not.include', '/add');
    
    // Verify the new data source appears in the list
    cy.contains('table tbody tr', sourceName).should('be.visible');
  });

  /**
   * Test: Verify editing an existing data source
   */
  it('should edit an existing data source', () => {
    // Intercept the GET request for retrieving a specific data source
    cy.intercept('GET', '/api/v1/data-sources/*').as('getDataSource');
    
    // Intercept the PUT request for updating the data source
    cy.intercept('PUT', '/api/v1/data-sources/*').as('updateDataSource');
    
    // Store the name of the first data source for verification
    cy.get('table tbody tr').first().find('td').eq(0).invoke('text').as('originalName');
    
    // Click the edit button (= symbol in wireframe) for the first data source
    cy.get('table tbody tr').first().find('td').last().contains(/=|Edit/).click();
    
    // Wait for the data source details to load
    cy.wait('@getDataSource');
    
    // Verify navigation to edit page
    cy.url().should('include', '/data-sources/edit/');
    
    // Generate a unique updated name
    const updatedName = `Updated Source ${Date.now()}`;
    
    // Update the data source name
    cy.get('input[name="name"]').clear().type(updatedName);
    
    // Save the changes
    cy.contains('button', 'Save Source').click();
    
    // Wait for the update API request to complete
    cy.wait('@updateDataSource').its('response.statusCode').should('eq', 200);
    
    // Verify success notification
    cy.contains('Data source updated successfully').should('be.visible');
    
    // Verify navigation back to data sources list
    cy.url().should('include', '/data-sources').and('not.include', '/edit');
    
    // Verify the updated data source appears in the list
    cy.contains('table tbody tr', updatedName).should('be.visible');
    
    // Verify the original name is no longer present
    cy.get('@originalName').then(originalName => {
      cy.contains('table tbody tr', String(originalName)).should('not.exist');
    });
  });

  /**
   * Test: Verify deleting a data source
   */
  it('should delete a data source', () => {
    // Intercept the DELETE request
    cy.intercept('DELETE', '/api/v1/data-sources/*').as('deleteDataSource');
    
    // Store the name of the data source to be deleted
    cy.get('table tbody tr').first().find('td').eq(0).invoke('text').as('dataSourceName');
    
    // Get the initial count of data sources
    cy.get('table tbody tr').its('length').as('initialRowCount');
    
    // Click the delete button (x symbol in wireframe) for the first data source
    cy.get('table tbody tr').first().find('td').last().contains(/x|Delete/).click();
    
    // Verify the confirmation modal appears
    cy.get('.modal, .dialog, [role="dialog"]').should('be.visible');
    
    // Confirm the deletion
    cy.get('.modal, .dialog, [role="dialog"]')
      .contains('button', /Confirm|Yes|Delete/)
      .click();
    
    // Wait for the DELETE request to complete
    cy.wait('@deleteDataSource').its('response.statusCode').should('eq', 200);
    
    // Verify success notification
    cy.contains('Data source deleted successfully').should('be.visible');
    
    // Verify the data source count decreased by 1
    cy.get('@initialRowCount').then(initialCount => {
      cy.get('table tbody tr').should('have.length', Number(initialCount) - 1);
    });
    
    // Verify the deleted data source is no longer in the list
    cy.get('@dataSourceName').then(name => {
      cy.contains('table tbody tr', String(name)).should('not.exist');
    });
  });

  /**
   * Test: Verify syncing a data source
   */
  it('should sync a data source', () => {
    // Intercept the sync request
    cy.intercept('POST', '/api/v1/data-sources/*/sync').as('syncDataSource');
    
    // Click the sync button for the first data source
    // Note: The wireframe doesn't specifically show a sync button, but it's a common action
    cy.get('table tbody tr').first().find('td').last().contains(/↻|Sync/).click();
    
    // Wait for the sync API request to complete
    cy.wait('@syncDataSource').its('response.statusCode').should('eq', 200);
    
    // Verify success notification
    cy.contains(/Data sync initiated|Synchronization started/).should('be.visible');
  });

  /**
   * Test: Verify pagination functionality
   */
  it('should paginate through data sources', () => {
    // Intercept the paginated API request
    cy.intercept('GET', '/api/v1/data-sources*').as('getDataSourcesPage');
    
    // Get the text of the first row on the first page for later comparison
    cy.get('table tbody tr').first().find('td').eq(0).invoke('text').as('firstPageFirstRowText');
    
    // Verify we're on the first page
    cy.contains(/Page 1|Page 1 of/).should('be.visible');
    
    // Click the next page button
    cy.contains('Next >').click();
    
    // Wait for the API request to complete
    cy.wait('@getDataSourcesPage');
    
    // Verify we're now on the second page
    cy.contains(/Page 2|Page 2 of/).should('be.visible');
    
    // Store the first row text from the second page
    cy.get('table tbody tr').first().find('td').eq(0).invoke('text').as('secondPageFirstRowText');
    
    // Click the previous page button
    cy.contains('< Previous').click();
    
    // Wait for the API request to complete
    cy.wait('@getDataSourcesPage');
    
    // Verify we're back on the first page
    cy.contains(/Page 1|Page 1 of/).should('be.visible');
    
    // Verify the current first row matches our stored first page row
    cy.get('table tbody tr').first().find('td').eq(0).invoke('text').then(currentFirstRowText => {
      cy.get('@firstPageFirstRowText').then(originalFirstRowText => {
        expect(currentFirstRowText).to.equal(originalFirstRowText);
      });
    });
    
    // Verify the first and second page contents are different
    cy.get('@firstPageFirstRowText').then(firstPageText => {
      cy.get('@secondPageFirstRowText').then(secondPageText => {
        expect(firstPageText).not.to.equal(secondPageText);
      });
    });
  });
});