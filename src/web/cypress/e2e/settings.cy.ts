// Cypress end-to-end test file for the settings page of the Freight Price Movement Agent web application.
// Tests the functionality, form interactions, and access control of the user preferences, notification settings,
// and system settings components.

describe('Settings Page', () => {
  // Setup before each test
  beforeEach(() => {
    // Mock API responses for settings data
    cy.intercept('GET', '/api/v1/user/preferences', {
      statusCode: 200,
      body: {
        displayName: 'John Smith',
        email: 'testuser@example.com',
        defaultCurrency: 'USD',
        dateFormat: 'MM/DD/YYYY',
        theme: 'dark'
      }
    }).as('getUserPreferences');
    
    cy.intercept('GET', '/api/v1/user/notifications', {
      statusCode: 200,
      body: {
        emailNotifications: true,
        smsNotifications: false,
        inAppNotifications: true,
        notifyPriceChanges: true,
        notifyDataSourceUpdates: true,
        notifySystemMaintenance: false,
        priceChangeThreshold: 5
      }
    }).as('getNotificationSettings');
    
    cy.intercept('GET', '/api/v1/system/settings', {
      statusCode: 200,
      body: {
        dataRetention: '3years',
        refreshInterval: '24hours',
        apiRateLimit: 100,
        auditLogging: true
      }
    }).as('getSystemSettings');
    
    // Log in using custom command defined in cypress/support/commands.ts
    // The command handles authentication and sets the necessary cookies/tokens
    cy.login('testuser@example.com', 'password');
    
    // Navigate to settings page
    cy.visit('/settings');
    
    // Wait for data to load
    cy.wait('@getUserPreferences');
    cy.wait('@getNotificationSettings');
  });

  // Test page loading
  it('should load the settings page correctly', () => {
    // Verify URL and page title
    cy.url().should('include', '/settings');
    cy.get('[data-testid="page-title"]').should('contain', 'Settings');
    
    // Verify tabs are visible
    cy.get('[data-testid="settings-tabs"]').should('be.visible');
    cy.get('[data-testid="tab-user-preferences"]').should('be.visible');
    cy.get('[data-testid="tab-notifications"]').should('be.visible');
    
    // System Settings tab should not be visible for regular users
    cy.get('[data-testid="tab-system-settings"]').should('not.exist');
  });

  // User Preferences Tests
  describe('User Preferences', () => {
    beforeEach(() => {
      // Ensure we're on the User Preferences tab
      cy.get('[data-testid="tab-user-preferences"]').click();
    });
    
    it('should update user preferences successfully', () => {
      // Verify initial form values
      cy.get('[data-testid="input-display-name"]').should('have.value', 'John Smith');
      cy.get('[data-testid="select-currency"]').should('have.value', 'USD');
      cy.get('[data-testid="select-date-format"]').should('have.value', 'MM/DD/YYYY');
      cy.get('[data-testid="radio-theme-dark"]').should('be.checked');
      
      // Update values
      cy.get('[data-testid="input-display-name"]').clear().type('Jane Smith');
      cy.get('[data-testid="select-currency"]').select('EUR');
      cy.get('[data-testid="select-date-format"]').select('DD/MM/YYYY');
      cy.get('[data-testid="radio-theme-light"]').check();
      
      // Intercept the save request
      cy.intercept('PUT', '/api/v1/user/preferences', {
        statusCode: 200,
        body: {
          success: true,
          message: 'Preferences updated successfully'
        }
      }).as('updatePreferences');
      
      // Save
      cy.get('[data-testid="btn-save-preferences"]').click();
      
      // Verify API call
      cy.wait('@updatePreferences').its('request.body').should('deep.equal', {
        displayName: 'Jane Smith',
        email: 'testuser@example.com',
        defaultCurrency: 'EUR',
        dateFormat: 'DD/MM/YYYY',
        theme: 'light'
      });
      
      // Verify success message
      cy.get('[data-testid="toast-success"]').should('be.visible')
        .and('contain', 'Preferences updated successfully');
      
      // Verify form reflects updates
      cy.get('[data-testid="input-display-name"]').should('have.value', 'Jane Smith');
      cy.get('[data-testid="select-currency"]').should('have.value', 'EUR');
      cy.get('[data-testid="select-date-format"]').should('have.value', 'DD/MM/YYYY');
      cy.get('[data-testid="radio-theme-light"]').should('be.checked');
    });
    
    it('should validate user preferences form fields', () => {
      // Clear required fields
      cy.get('[data-testid="input-display-name"]').clear();
      cy.get('[data-testid="input-email"]').clear();
      
      // Try to save
      cy.get('[data-testid="btn-save-preferences"]').click();
      
      // Verify validation errors
      cy.get('[data-testid="error-display-name"]').should('be.visible')
        .and('contain', 'Display Name is required');
        
      cy.get('[data-testid="error-email"]').should('be.visible')
        .and('contain', 'Email is required');
      
      // Fill display name but use invalid email
      cy.get('[data-testid="input-display-name"]').type('Test User');
      cy.get('[data-testid="input-email"]').type('invalid-email');
      
      // Try to save
      cy.get('[data-testid="btn-save-preferences"]').click();
      
      // Verify email validation error
      cy.get('[data-testid="error-email"]').should('be.visible')
        .and('contain', 'Invalid email format');
      
      // Verify form isn't submitted (no network request)
      cy.get('@updatePreferences.all').should('have.length', 0);
    });
    
    it('should preview theme changes immediately', () => {
      // Select light theme
      cy.get('[data-testid="radio-theme-light"]').check();
      
      // Verify theme change in UI without saving
      cy.get('body').should('have.class', 'light-theme')
        .and('not.have.class', 'dark-theme');
      
      // Select dark theme
      cy.get('[data-testid="radio-theme-dark"]').check();
      
      // Verify theme change in UI without saving
      cy.get('body').should('have.class', 'dark-theme')
        .and('not.have.class', 'light-theme');
      
      // Select system theme
      cy.get('[data-testid="radio-theme-system"]').check();
      
      // Verify theme change based on system preference
      cy.get('body').should('satisfy', ($body) => {
        return $body.hasClass('light-theme') || $body.hasClass('dark-theme');
      });
    });
    
    it('should discard changes when cancel button is clicked', () => {
      // Store original values
      let originalName, originalCurrency, originalDateFormat;
      
      cy.get('[data-testid="input-display-name"]').then($input => {
        originalName = $input.val();
      });
      
      cy.get('[data-testid="select-currency"]').then($select => {
        originalCurrency = $select.val();
      });
      
      cy.get('[data-testid="select-date-format"]').then($select => {
        originalDateFormat = $select.val();
      });
      
      // Make changes
      cy.get('[data-testid="input-display-name"]').clear().type('Changed Name');
      cy.get('[data-testid="select-currency"]').select('EUR');
      cy.get('[data-testid="select-date-format"]').select('YYYY-MM-DD');
      cy.get('[data-testid="radio-theme-light"]').check();
      
      // Intercept any potential save requests
      cy.intercept('PUT', '/api/v1/user/preferences').as('updatePreferences');
      
      // Click cancel
      cy.get('[data-testid="btn-cancel"]').click();
      
      // Verify form is reset to original values
      cy.get('[data-testid="input-display-name"]').should('have.value', originalName);
      cy.get('[data-testid="select-currency"]').should('have.value', originalCurrency);
      cy.get('[data-testid="select-date-format"]').should('have.value', originalDateFormat);
      cy.get('[data-testid="radio-theme-dark"]').should('be.checked');
      
      // Verify no API request was made
      cy.get('@updatePreferences.all').should('have.length', 0);
    });
    
    it('should open password change modal and update password', () => {
      // Click change password button
      cy.get('[data-testid="btn-change-password"]').click();
      
      // Verify modal is open
      cy.get('[data-testid="password-change-modal"]').should('be.visible');
      
      // Fill password fields
      cy.get('[data-testid="input-current-password"]').type('oldpassword');
      cy.get('[data-testid="input-new-password"]').type('newStrongPassword123!');
      cy.get('[data-testid="input-confirm-password"]').type('newStrongPassword123!');
      
      // Intercept password change request
      cy.intercept('POST', '/api/v1/user/change-password', {
        statusCode: 200,
        body: {
          success: true,
          message: 'Password changed successfully'
        }
      }).as('changePassword');
      
      // Submit form
      cy.get('[data-testid="btn-submit-password-change"]').click();
      
      // Verify API call
      cy.wait('@changePassword').its('request.body').should('deep.equal', {
        currentPassword: 'oldpassword',
        newPassword: 'newStrongPassword123!'
      });
      
      // Verify success message
      cy.get('[data-testid="toast-success"]').should('be.visible')
        .and('contain', 'Password changed successfully');
      
      // Verify modal is closed
      cy.get('[data-testid="password-change-modal"]').should('not.exist');
    });
  });

  // Notification Settings Tests
  describe('Notification Settings', () => {
    beforeEach(() => {
      // Navigate to Notifications tab
      cy.get('[data-testid="tab-notifications"]').click();
    });
    
    it('should update notification settings successfully', () => {
      // Verify form fields
      cy.get('[data-testid="checkbox-email-notifications"]').should('be.checked');
      cy.get('[data-testid="checkbox-sms-notifications"]').should('not.be.checked');
      cy.get('[data-testid="checkbox-in-app-notifications"]').should('be.checked');
      
      cy.get('[data-testid="checkbox-notify-price-changes"]').should('be.checked');
      cy.get('[data-testid="checkbox-notify-data-source-updates"]').should('be.checked');
      cy.get('[data-testid="checkbox-notify-system-maintenance"]').should('not.be.checked');
      cy.get('[data-testid="input-price-change-threshold"]').should('have.value', '5');
      
      // Update values
      cy.get('[data-testid="checkbox-email-notifications"]').uncheck();
      cy.get('[data-testid="checkbox-sms-notifications"]').check();
      cy.get('[data-testid="checkbox-notify-system-maintenance"]').check();
      cy.get('[data-testid="input-price-change-threshold"]').clear().type('10');
      
      // Intercept the save request
      cy.intercept('PUT', '/api/v1/user/notifications', {
        statusCode: 200,
        body: {
          success: true,
          message: 'Notification settings updated successfully'
        }
      }).as('updateNotifications');
      
      // Save
      cy.get('[data-testid="btn-save-notifications"]').click();
      
      // Verify API call
      cy.wait('@updateNotifications').its('request.body').should('deep.equal', {
        emailNotifications: false,
        smsNotifications: true,
        inAppNotifications: true,
        notifyPriceChanges: true,
        notifyDataSourceUpdates: true,
        notifySystemMaintenance: true,
        priceChangeThreshold: 10
      });
      
      // Verify success message
      cy.get('[data-testid="toast-success"]').should('be.visible')
        .and('contain', 'Notification settings updated successfully');
      
      // Verify form reflects updates
      cy.get('[data-testid="checkbox-email-notifications"]').should('not.be.checked');
      cy.get('[data-testid="checkbox-sms-notifications"]').should('be.checked');
      cy.get('[data-testid="checkbox-notify-system-maintenance"]').should('be.checked');
      cy.get('[data-testid="input-price-change-threshold"]').should('have.value', '10');
    });
    
    it('should validate notification settings form fields', () => {
      // Enter invalid threshold
      cy.get('[data-testid="input-price-change-threshold"]').clear().type('-5');
      
      // Try to save
      cy.get('[data-testid="btn-save-notifications"]').click();
      
      // Verify validation error
      cy.get('[data-testid="error-threshold"]').should('be.visible')
        .and('contain', 'Threshold must be a positive number');
      
      // Verify form isn't submitted (no network request)
      cy.get('@updateNotifications.all').should('have.length', 0);
    });
  });

  // System Settings Tests (Admin Only)
  describe('System Settings (Admin Only)', () => {
    it('should show system settings tab only for admin users', () => {
      // As regular user, system settings should not be visible
      cy.get('[data-testid="tab-system-settings"]').should('not.exist');
      
      // Log out
      cy.get('[data-testid="btn-logout"]').click();
      
      // Log in as admin
      cy.login('admin@example.com', 'adminpassword');
      
      // Mock responses for admin user
      cy.intercept('GET', '/api/v1/user/preferences', {
        statusCode: 200,
        body: {
          displayName: 'Admin User',
          email: 'admin@example.com',
          defaultCurrency: 'USD',
          dateFormat: 'MM/DD/YYYY',
          theme: 'dark'
        }
      }).as('getAdminPreferences');
      
      cy.intercept('GET', '/api/v1/user/notifications', {
        statusCode: 200,
        body: {
          emailNotifications: true,
          smsNotifications: true,
          inAppNotifications: true,
          notifyPriceChanges: true,
          notifyDataSourceUpdates: true,
          notifySystemMaintenance: true,
          priceChangeThreshold: 5
        }
      }).as('getAdminNotifications');
      
      cy.visit('/settings');
      
      // Wait for data to load
      cy.wait('@getAdminPreferences');
      cy.wait('@getAdminNotifications');
      cy.wait('@getSystemSettings');
      
      // System settings should be visible for admin
      cy.get('[data-testid="tab-system-settings"]').should('be.visible');
    });
    
    it('should update system settings successfully (admin only)', () => {
      // Log in as admin and visit settings page
      cy.login('admin@example.com', 'adminpassword');
      cy.visit('/settings');
      
      // Wait for system settings to load
      cy.wait('@getSystemSettings');
      
      // Navigate to System Settings tab
      cy.get('[data-testid="tab-system-settings"]').click();
      
      // Verify form fields
      cy.get('[data-testid="select-data-retention"]').should('have.value', '3years');
      cy.get('[data-testid="select-refresh-interval"]').should('have.value', '24hours');
      cy.get('[data-testid="input-api-rate-limit"]').should('have.value', '100');
      cy.get('[data-testid="checkbox-audit-logging"]').should('be.checked');
      
      // Update values
      cy.get('[data-testid="select-data-retention"]').select('5years');
      cy.get('[data-testid="select-refresh-interval"]').select('12hours');
      cy.get('[data-testid="input-api-rate-limit"]').clear().type('150');
      
      // Intercept the save request
      cy.intercept('PUT', '/api/v1/system/settings', {
        statusCode: 200,
        body: {
          success: true,
          message: 'System settings updated successfully'
        }
      }).as('updateSystemSettings');
      
      // Save
      cy.get('[data-testid="btn-save-system-settings"]').click();
      
      // Verify API call
      cy.wait('@updateSystemSettings').its('request.body').should('deep.equal', {
        dataRetention: '5years',
        refreshInterval: '12hours',
        apiRateLimit: 150,
        auditLogging: true
      });
      
      // Verify success message
      cy.get('[data-testid="toast-success"]').should('be.visible')
        .and('contain', 'System settings updated successfully');
      
      // Verify form reflects updates
      cy.get('[data-testid="select-data-retention"]').should('have.value', '5years');
      cy.get('[data-testid="select-refresh-interval"]').should('have.value', '12hours');
      cy.get('[data-testid="input-api-rate-limit"]').should('have.value', '150');
    });
  });
});