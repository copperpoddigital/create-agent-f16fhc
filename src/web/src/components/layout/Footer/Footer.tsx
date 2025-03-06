import React from 'react';
import classNames from 'classnames'; // v2.3.2
import { APP_NAME, APP_VERSION } from '../../../config/constants';

/**
 * Props interface for the Footer component
 */
interface FooterProps {
  /**
   * Optional CSS class name to override default styles
   */
  className?: string;
}

/**
 * Footer component displays copyright information, version details, and important links
 * at the bottom of the application pages
 */
const Footer: React.FC<FooterProps> = ({ className }) => {
  // Get current year for copyright text
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className={classNames('footer', className)} role="contentinfo">
      <div className="footer-content">
        <div className="footer-copyright">
          &copy; {currentYear} {APP_NAME}. All rights reserved.
        </div>
        
        <nav className="footer-links" aria-label="Footer navigation">
          <a href="/help" className="footer-link">Help</a>
          <a href="/privacy" className="footer-link">Privacy Policy</a>
          <a href="/terms" className="footer-link">Terms of Service</a>
        </nav>
        
        <div className="footer-version">
          Version {APP_VERSION}
        </div>
      </div>
    </footer>
  );
};

export default Footer;