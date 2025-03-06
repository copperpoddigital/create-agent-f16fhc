import React from 'react';
import { describe, it, expect } from '@jest/globals';
import { render, screen } from '../../../utils/test-utils';
import Footer from './Footer';
import { APP_NAME, APP_VERSION } from '../../../config/constants';

describe('Footer', () => {
  /**
   * Helper function to render the Footer component with optional props
   * @param props - Component props to pass to the Footer
   */
  const renderFooter = (props = {}) => {
    return render(<Footer {...props} />);
  };

  it('renders the footer with correct structure', () => {
    renderFooter();
    const footer = screen.getByRole('contentinfo');
    expect(footer).toBeInTheDocument();
    expect(footer).toHaveClass('footer');
    expect(screen.getByClassName('footer-content')).toBeInTheDocument();
  });

  it('displays the correct copyright text with current year', () => {
    renderFooter();
    const currentYear = new Date().getFullYear();
    const copyrightText = screen.getByText(new RegExp(`© ${currentYear} ${APP_NAME}`));
    expect(copyrightText).toBeInTheDocument();
    expect(copyrightText).toHaveTextContent('All rights reserved');
  });

  it('displays the correct version information', () => {
    renderFooter();
    const versionText = screen.getByText(new RegExp(`Version ${APP_VERSION}`));
    expect(versionText).toBeInTheDocument();
    expect(versionText).toHaveClass('footer-version');
  });

  it('renders all required links', () => {
    renderFooter();
    
    // Check each link exists and has correct href
    const helpLink = screen.getByText('Help');
    expect(helpLink).toBeInTheDocument();
    expect(helpLink).toHaveAttribute('href', '/help');
    
    const privacyLink = screen.getByText('Privacy Policy');
    expect(privacyLink).toBeInTheDocument();
    expect(privacyLink).toHaveAttribute('href', '/privacy');
    
    const termsLink = screen.getByText('Terms of Service');
    expect(termsLink).toBeInTheDocument();
    expect(termsLink).toHaveAttribute('href', '/terms');
  });

  it('applies custom className when provided', () => {
    const customClass = 'custom-footer-class';
    renderFooter({ className: customClass });
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('footer');
    expect(footer).toHaveClass(customClass);
  });

  it('has accessible links with proper attributes', () => {
    renderFooter();
    
    // Check navigation has proper aria label
    const navElement = screen.getByRole('navigation');
    expect(navElement).toHaveAttribute('aria-label', 'Footer navigation');
    
    // Get all links in the footer
    const links = screen.getAllByRole('link');
    
    // Verify there are exactly 3 links
    expect(links).toHaveLength(3);
    
    // Each link should have footer-link class
    links.forEach(link => {
      expect(link).toHaveClass('footer-link');
    });
  });
});