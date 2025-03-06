/**
 * End-to-end test suite for the login functionality
 * of the Freight Price Movement Agent web application.
 * 
 * @package cypress
 * @version 12.0.0
 */

describe('Login Page', () => {
  // Setup that runs before each test case
  beforeEach(() => {
    // Visit the login page before each test
    cy.visit('/login');
    
    // Intercept API calls to the authentication endpoint
    cy.intercept('POST', '/api/v1/auth/token').as('loginRequest');
  });

  it('should login successfully with valid credentials', () => {
    // Enter valid username in the username field
    cy.get('[data-testid="username-input"]').type('validuser@example.com');
    
    // Enter valid password in the password field
    cy.get('[data-testid="password-input"]').type('ValidPassword123');
    
    // Click the login button
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for the authentication API call to complete
    cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);
    
    // Verify successful redirection to the dashboard page
    cy.url().should('include', '/dashboard');
    
    // Verify authentication state is updated correctly
    cy.window().its('localStorage.token').should('exist');
    cy.get('[data-testid="user-menu"]').should('be.visible');
  });

  it('should show error message with invalid credentials', () => {
    // Enter invalid username in the username field
    cy.get('[data-testid="username-input"]').type('invalid@example.com');
    
    // Enter invalid password in the password field
    cy.get('[data-testid="password-input"]').type('WrongPassword123');
    
    // Click the login button
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for the authentication API call to complete
    cy.wait('@loginRequest').its('response.statusCode').should('eq', 401);
    
    // Verify error message is displayed
    cy.get('[data-testid="login-error"]').should('be.visible')
      .and('contain', 'Invalid username or password');
    
    // Verify user remains on the login page
    cy.url().should('include', '/login');
  });

  it('should validate required fields', () => {
    // Click the login button without entering any credentials
    cy.get('[data-testid="login-button"]').click();
    
    // Verify validation messages for required fields are displayed
    cy.get('[data-testid="username-error"]').should('be.visible')
      .and('contain', 'Username is required');
    
    cy.get('[data-testid="password-error"]').should('be.visible')
      .and('contain', 'Password is required');
    
    // Verify form submission is prevented
    cy.get('@loginRequest.all').should('have.length', 0);
    
    // Test partial validation - enter username only
    cy.get('[data-testid="username-input"]').type('user@example.com');
    cy.get('[data-testid="login-button"]').click();
    
    // Verify only password error remains
    cy.get('[data-testid="username-error"]').should('not.exist');
    cy.get('[data-testid="password-error"]').should('be.visible');
    
    // Test partial validation - enter password only
    cy.get('[data-testid="username-input"]').clear();
    cy.get('[data-testid="password-input"]').type('Password123');
    cy.get('[data-testid="login-button"]').click();
    
    // Verify only username error remains
    cy.get('[data-testid="username-error"]').should('be.visible');
    cy.get('[data-testid="password-error"]').should('not.exist');
  });

  it('should persist session with remember me option', () => {
    // Enter valid username in the username field
    cy.get('[data-testid="username-input"]').type('validuser@example.com');
    
    // Enter valid password in the password field
    cy.get('[data-testid="password-input"]').type('ValidPassword123');
    
    // Check the remember me checkbox
    cy.get('[data-testid="remember-me-checkbox"]').check();
    
    // Click the login button
    cy.get('[data-testid="login-button"]').click();
    
    // Wait for the authentication API call to complete
    cy.wait('@loginRequest').then(interception => {
      // Verify the remember me parameter is sent to the API
      expect(interception.request.body).to.have.property('remember_me', true);
    });
    
    // Verify session persistence by checking storage
    cy.getCookie('refresh_token').should('exist');
    
    // Verify cookie has extended expiration time for remembered session
    cy.getCookie('refresh_token').then((cookie) => {
      const expiryDate = new Date(cookie.expiry * 1000);
      const now = new Date();
      // For "remember me", expect at least 7-day expiration
      expect((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)).to.be.gt(6);
    });
  });

  it('should toggle password visibility', () => {
    // Enter a password in the password field
    cy.get('[data-testid="password-input"]')
      .type('TestPassword123')
      .should('have.attr', 'type', 'password');
    
    // Click the password visibility toggle icon
    cy.get('[data-testid="password-toggle"]').click();
    
    // Verify password is now visible (type='text')
    cy.get('[data-testid="password-input"]').should('have.attr', 'type', 'text');
    
    // Click the toggle icon again
    cy.get('[data-testid="password-toggle"]').click();
    
    // Verify password is masked again (type='password')
    cy.get('[data-testid="password-input"]').should('have.attr', 'type', 'password');
  });

  it('should navigate to forgot password page', () => {
    // Click the forgot password link
    cy.get('[data-testid="forgot-password-link"]').click();
    
    // Verify navigation to the forgot password page
    cy.url().should('include', '/forgot-password');
  });

  it('should handle network errors during login', () => {
    // Override the interceptor to simulate a network error
    cy.intercept('POST', '/api/v1/auth/token', {
      forceNetworkError: true
    }).as('networkError');
    
    // Enter credentials
    cy.get('[data-testid="username-input"]').type('user@example.com');
    cy.get('[data-testid="password-input"]').type('Password123');
    
    // Click the login button
    cy.get('[data-testid="login-button"]').click();
    
    // Verify appropriate error message is displayed
    cy.get('[data-testid="network-error"]').should('be.visible')
      .and('contain', 'Connection error');
  });

  it('should handle account lockout after multiple failed attempts', () => {
    // Setup interceptor for failed login with attempts remaining
    cy.intercept('POST', '/api/v1/auth/token', {
      statusCode: 401,
      body: {
        error: 'invalid_credentials',
        message: 'Invalid username or password',
        attempts_remaining: 2
      }
    }).as('failedLoginAttempt');
    
    // First failed attempt
    cy.get('[data-testid="username-input"]').type('user@example.com');
    cy.get('[data-testid="password-input"]').type('WrongPassword1');
    cy.get('[data-testid="login-button"]').click();
    cy.wait('@failedLoginAttempt');
    
    // Verify warning about remaining attempts
    cy.get('[data-testid="login-error"]').should('contain', 'attempts remaining');
    
    // Update interceptor for account lockout
    cy.intercept('POST', '/api/v1/auth/token', {
      statusCode: 429,
      body: {
        error: 'account_locked',
        message: 'Account temporarily locked due to multiple failed attempts',
        locked_until: new Date(Date.now() + 300000).toISOString() // 5 minutes from now
      }
    }).as('accountLockout');
    
    // Trigger account lockout
    cy.get('[data-testid="password-input"]').clear().type('WrongPassword2');
    cy.get('[data-testid="login-button"]').click();
    cy.wait('@accountLockout');
    
    // Verify lockout message is displayed
    cy.get('[data-testid="login-error"]')
      .should('contain', 'Account temporarily locked')
      .and('contain', 'multiple failed attempts');
  });
});