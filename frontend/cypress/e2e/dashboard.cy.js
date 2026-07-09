describe('SmartArena Dashboard E2E Tests', () => {
  beforeEach(() => {
    // Dynamically resolve base URL or default to localhost
    const baseUrl = Cypress.config('baseUrl') || 'http://localhost:5000';
    
    // Programmatic login stub: mock Firebase auth and session cookie for CI testing
    cy.setCookie('session', 'mock-ci-session-token');
    
    // Intercept the /auth/me backend call to return a valid admin profile
    cy.intercept('GET', '**/api/v1/auth/me', {
      statusCode: 200,
      body: {
        status: "success",
        data: { uid: "test-uid-123", email: "judge@smartarena.ai", role: "admin" }
      }
    }).as('getProfile');

    cy.visit(`${baseUrl}/pages/dashboard.html`);
    
    // Wait for the mocked profile to load
    cy.wait('@getProfile');
  });

  it('Displays the main dashboard title', () => {
    cy.get('h1').contains('SmartArena Operations');
  });

  it('Can open the AI Assistant Chat Modal', () => {
    // Click the toggle button
    cy.get('#ai-chat-toggle').click();
    
    // Check that modal is visible
    cy.get('#ai-chat-window').should('not.have.class', 'hidden');

    // Type a query
    cy.get('#ai-chat-input').type('Where is the nearest medical team?');
    
    // Submit
    cy.get('#ai-chat-form').submit();

    // Verify typing indicator or sent message appears
    cy.get('#ai-chat-messages').should('contain', 'Where is the nearest medical team?');
  });
});
