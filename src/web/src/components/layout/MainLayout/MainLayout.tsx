import React, { useState, useEffect } from 'react';
import classNames from 'classnames'; // ^2.3.2

import Header from '../Header';
import Sidebar from '../Sidebar';
import Footer from '../Footer';
import Alert from '../../common/Alert';
import useMediaQuery from '../../../hooks/useMediaQuery';
import { useAlertContext } from '../../../contexts/AlertContext';

/**
 * Props interface for the MainLayout component
 */
interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * Main layout component that provides the overall structure for the application
 * Implements responsive behavior and integrates alert system for notifications
 */
const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  // State for sidebar expanded/collapsed
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  
  // Get alerts and hideAlert function from the alert context
  const { alerts, hideAlert } = useAlertContext();
  
  // Check if screen is mobile using media query
  const isMobile = useMediaQuery('(max-width: 767px)');
  
  // Automatically collapse sidebar on mobile screens
  useEffect(() => {
    if (isMobile) {
      setSidebarExpanded(false);
    }
  }, [isMobile]);
  
  // Toggle sidebar expanded state
  const toggleSidebar = () => {
    setSidebarExpanded(prevExpanded => !prevExpanded);
  };
  
  return (
    <div 
      className={classNames('main-layout', {
        'main-layout--sidebar-expanded': sidebarExpanded,
        'main-layout--sidebar-collapsed': !sidebarExpanded,
        'main-layout--mobile': isMobile
      })}
      data-testid="main-layout"
    >
      <Header 
        toggleSidebar={toggleSidebar} 
        isSidebarExpanded={sidebarExpanded} 
      />
      
      <div className="main-layout__container">
        <Sidebar 
          expanded={sidebarExpanded} 
          onToggle={toggleSidebar} 
        />
        
        <main className="main-layout__content">
          {/* Alert container */}
          {alerts.length > 0 && (
            <div className="main-layout__alerts">
              {alerts.map(alert => (
                <Alert
                  key={alert.id}
                  type={alert.type}
                  title={alert.title}
                  dismissible={alert.dismissible}
                  onDismiss={() => hideAlert(alert.id)}
                >
                  {alert.message}
                </Alert>
              ))}
            </div>
          )}
          
          {/* Main content area */}
          <div className="main-layout__main">
            {children}
          </div>
        </main>
      </div>
      
      <Footer />
    </div>
  );
};

export default MainLayout;