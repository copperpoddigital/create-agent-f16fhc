/**
 * Dashboard Page End-to-End Tests
 * Tests the functionality, data display, and interactions of the main dashboard components
 * of the Freight Price Movement Agent.
 * 
 * @packageDocumentation
 * @version 1.0.0
 */

// Cypress testing framework - version 12.0.0
import 'cypress';

describe('Dashboard Page', () => {
  beforeEach(() => {
    // Log in and navigate to dashboard before each test
    cy.visit('/login');
    cy.get('[data-cy=username-input]').type('testuser');
    cy.get('[data-cy=password-input]').type('Password123!');
    cy.get('[data-cy=login-button]').click();
    
    // Intercept API requests to mock responses
    cy.intercept('GET', '/api/v1/analysis/recent', { fixture: 'recent-price-changes.json' }).as('recentChanges');
    cy.intercept('GET', '/api/v1/analysis/trend', { fixture: 'price-trend-data.json' }).as('trendData');
    cy.intercept('GET', '/api/v1/analysis/saved', { fixture: 'saved-analyses.json' }).as('savedAnalyses');
    cy.intercept('GET', '/api/v1/alerts', { fixture: 'alerts.json' }).as('alerts');
    
    // Navigate to dashboard and wait for API responses
    cy.visit('/dashboard');
    cy.wait(['@recentChanges', '@trendData', '@savedAnalyses', '@alerts']);
  });

  it('should load the dashboard page correctly', () => {
    // Verify URL and page title
    cy.url().should('include', '/dashboard');
    cy.title().should('contain', 'Dashboard | Freight Price Movement Agent');
    
    // Verify all dashboard widgets are visible
    cy.get('[data-cy=dashboard-container]').should('be.visible');
    cy.get('[data-cy=recent-price-changes]').should('be.visible');
    cy.get('[data-cy=price-trend-chart]').should('be.visible');
    cy.get('[data-cy=saved-analyses]').should('be.visible');
    cy.get('[data-cy=alerts-widget]').should('be.visible');
  });

  it('should display the page header with correct title', () => {
    cy.get('[data-cy=page-header]').should('be.visible');
    cy.get('[data-cy=page-header]').should('contain', 'FREIGHT PRICE MOVEMENT DASHBOARD');
    cy.get('[data-cy=user-menu]').should('be.visible');
    cy.get('[data-cy=help-icon]').should('be.visible');
    cy.get('[data-cy=settings-icon]').should('be.visible');
    cy.get('[data-cy=logout-icon]').should('be.visible');
  });

  it('should display the Recent Price Changes widget correctly', () => {
    // Verify widget title and subtitle
    cy.get('[data-cy=recent-price-changes]').within(() => {
      cy.get('[data-cy=widget-title]').should('contain', 'RECENT PRICE CHANGES');
      cy.get('[data-cy=widget-subtitle]').should('contain', 'Last 7 days');
      
      // Verify freight modes and their changes
      cy.get('[data-cy=freight-mode-item]').should('have.length', 4);
      
      // Ocean item
      cy.get('[data-cy=freight-mode-ocean]').should('be.visible');
      cy.get('[data-cy=freight-mode-ocean]').should('contain', 'Ocean:');
      cy.get('[data-cy=freight-mode-ocean]').should('contain', '+3.2%');
      cy.get('[data-cy=trend-indicator-up]').should('be.visible');
      
      // Air item
      cy.get('[data-cy=freight-mode-air]').should('be.visible');
      cy.get('[data-cy=freight-mode-air]').should('contain', 'Air:');
      cy.get('[data-cy=freight-mode-air]').should('contain', '-1.5%');
      cy.get('[data-cy=trend-indicator-down]').should('be.visible');
      
      // Road item
      cy.get('[data-cy=freight-mode-road]').should('be.visible');
      cy.get('[data-cy=freight-mode-road]').should('contain', 'Road:');
      cy.get('[data-cy=freight-mode-road]').should('contain', '+0.8%');
      cy.get('[data-cy=trend-indicator-up]').should('be.visible');
      
      // Rail item
      cy.get('[data-cy=freight-mode-rail]').should('be.visible');
      cy.get('[data-cy=freight-mode-rail]').should('contain', 'Rail:');
      cy.get('[data-cy=freight-mode-rail]').should('contain', '+0.2%');
      cy.get('[data-cy=trend-indicator-stable]').should('be.visible');
      
      // Verify View Details button
      cy.get('[data-cy=view-details-button]').should('be.visible');
      cy.get('[data-cy=view-details-button]').should('contain', 'View Details');
    });
  });

  it('should render the Price Trend Chart widget properly', () => {
    cy.get('[data-cy=price-trend-chart]').within(() => {
      cy.get('[data-cy=widget-title]').should('contain', 'PRICE TREND (30 DAYS)');
      
      // Verify chart is rendered
      cy.get('[data-cy=trend-chart]').should('be.visible');
      
      // Verify chart elements
      cy.get('[data-cy=chart-axis-x]').should('be.visible');
      cy.get('[data-cy=chart-axis-y]').should('be.visible');
      cy.get('[data-cy=chart-line]').should('be.visible');
      cy.get('[data-cy=data-points]').should('have.length.at.least', 5);
      
      // Verify View Full Chart button
      cy.get('[data-cy=view-full-chart-button]').should('be.visible');
      cy.get('[data-cy=view-full-chart-button]').should('contain', 'View Full Chart');
    });
  });

  it('should display the Saved Analyses widget with user analyses', () => {
    cy.get('[data-cy=saved-analyses]').within(() => {
      cy.get('[data-cy=widget-title]').should('contain', 'SAVED ANALYSES');
      
      // Verify saved analyses are listed
      cy.get('[data-cy=analysis-item]').should('have.length', 2);
      
      // First analysis
      cy.get('[data-cy=analysis-item]').first().within(() => {
        cy.get('[data-cy=analysis-name]').should('contain', 'Q2 Ocean Freight');
        cy.get('[data-cy=last-updated]').should('contain', 'Last updated: Today');
      });
      
      // Second analysis
      cy.get('[data-cy=analysis-item]').eq(1).within(() => {
        cy.get('[data-cy=analysis-name]').should('contain', 'Air vs Ocean 2023');
        cy.get('[data-cy=last-updated]').should('contain', 'Last updated: 3d ago');
      });
      
      // Verify New Analysis button
      cy.get('[data-cy=new-analysis-button]').should('be.visible');
      cy.get('[data-cy=new-analysis-button]').should('contain', '+ New Analysis');
    });
  });

  it('should display the Alerts widget with system notifications', () => {
    cy.get('[data-cy=alerts-widget]').within(() => {
      cy.get('[data-cy=widget-title]').should('contain', 'ALERTS');
      
      // Verify alerts are displayed
      cy.get('[data-cy=alert-item]').should('have.length', 2);
      
      // First alert
      cy.get('[data-cy=alert-item]').first().within(() => {
        cy.get('[data-cy=alert-icon]').should('be.visible');
        cy.get('[data-cy=alert-message]').should('contain', 'Significant price increase detected on APAC routes');
      });
      
      // Second alert
      cy.get('[data-cy=alert-item]').eq(1).within(() => {
        cy.get('[data-cy=alert-icon]').should('be.visible');
        cy.get('[data-cy=alert-message]').should('contain', '3 data sources need updating');
      });
      
      // Test dismissing an alert
      cy.get('[data-cy=dismiss-alert]').first().click();
      cy.get('[data-cy=alert-item]').should('have.length', 1);
    });
  });

  it('should navigate to detailed analysis when clicking View Details', () => {
    // Intercept the navigation request
    cy.intercept('GET', '/api/v1/analysis/details*').as('analysisDetails');
    
    // Click the View Details button
    cy.get('[data-cy=recent-price-changes]')
      .find('[data-cy=view-details-button]')
      .click();
    
    // Verify navigation occurred
    cy.url().should('include', '/analysis/details');
    cy.wait('@analysisDetails');
    cy.get('[data-cy=analysis-details-container]').should('be.visible');
    cy.get('[data-cy=details-header]').should('contain', 'ANALYSIS RESULTS');
  });

  it('should navigate to new analysis page when clicking + New Analysis', () => {
    // Click the New Analysis button
    cy.get('[data-cy=saved-analyses]')
      .find('[data-cy=new-analysis-button]')
      .click();
    
    // Verify navigation occurred
    cy.url().should('include', '/analysis/new');
    cy.get('[data-cy=new-analysis-container]').should('be.visible');
    cy.get('[data-cy=analysis-header]').should('contain', 'NEW PRICE MOVEMENT ANALYSIS');
  });

  it('should navigate to saved analysis details when clicking on a saved analysis', () => {
    // Intercept the navigation request
    cy.intercept('GET', '/api/v1/analysis/saved/*').as('savedAnalysis');
    
    // Click on the first saved analysis
    cy.get('[data-cy=saved-analyses]')
      .find('[data-cy=analysis-item]')
      .first()
      .click();
    
    // Verify navigation occurred
    cy.url().should('include', '/analysis/saved/');
    cy.wait('@savedAnalysis');
    cy.get('[data-cy=analysis-details-container]').should('be.visible');
    cy.get('[data-cy=analysis-title]').should('contain', 'Q2 Ocean Freight');
  });

  it('should display correctly on different screen sizes', () => {
    // Test desktop layout (1200px width)
    cy.viewport(1200, 800);
    cy.get('[data-cy=dashboard-container]').should('be.visible');
    cy.get('[data-cy=recent-price-changes]').should('be.visible');
    cy.get('[data-cy=price-trend-chart]').should('be.visible');
    // Verify side-by-side layout for desktop
    cy.get('[data-cy=dashboard-row]').first().within(() => {
      cy.get('[data-cy=recent-price-changes]').should('be.visible');
      cy.get('[data-cy=price-trend-chart]').should('be.visible');
    });
    
    // Test tablet layout (768px width)
    cy.viewport(768, 1024);
    cy.get('[data-cy=dashboard-container]').should('be.visible');
    // Verify stacked layout for tablet
    cy.get('[data-cy=dashboard-container]').should('have.class', 'tablet-layout');
    
    // Test mobile layout (375px width)
    cy.viewport(375, 667);
    cy.get('[data-cy=dashboard-container]').should('be.visible');
    // Verify single column layout for mobile
    cy.get('[data-cy=dashboard-container]').should('have.class', 'mobile-layout');
    // Verify menu becomes a hamburger on mobile
    cy.get('[data-cy=hamburger-menu]').should('be.visible');
    cy.get('[data-cy=navigation-sidebar]').should('not.be.visible');
    // Open the menu and verify it works
    cy.get('[data-cy=hamburger-menu]').click();
    cy.get('[data-cy=navigation-sidebar]').should('be.visible');
  });

  it('should allow navigation using sidebar menu', () => {
    // Test navigation to Data Sources
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-data-sources]').click();
    });
    cy.url().should('include', '/data-sources');
    
    // Navigate back to dashboard
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-dashboard]').click();
    });
    cy.url().should('include', '/dashboard');
    
    // Test navigation to Analysis
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-analysis]').click();
    });
    cy.url().should('include', '/analysis');
    
    // Navigate back to dashboard
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-dashboard]').click();
    });
    cy.url().should('include', '/dashboard');
    
    // Test navigation to Reports
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-reports]').click();
    });
    cy.url().should('include', '/reports');
    
    // Navigate back to dashboard
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-dashboard]').click();
    });
    cy.url().should('include', '/dashboard');
    
    // Test navigation to Settings
    cy.get('[data-cy=sidebar-menu]').within(() => {
      cy.get('[data-cy=menu-settings]').click();
    });
    cy.url().should('include', '/settings');
  });
});