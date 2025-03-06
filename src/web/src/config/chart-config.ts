/**
 * chart-config.ts
 *
 * Configuration for chart visualization settings in the Freight Price Movement Agent web application.
 * This file defines default chart options, styling, and behavior for different chart types
 * used to visualize freight price movement data.
 *
 * The configurations implement the visualization requirements specified in:
 * - Technical Specifications/2.1 FEATURE CATALOG/2.1.4 Result Presentation
 * - Technical Specifications/6.3 PRESENTATION SERVICE/6.3.3 Visualization Types
 * - Technical Specifications/7.5 RESPONSIVE DESIGN
 * - Technical Specifications/7.6 VISUAL DESIGN ELEMENTS
 */

import { ChartOptions } from 'chart.js'; // v4.3.0
import { CHART_COLORS, BREAKPOINTS } from './constants';
import { TrendDirection } from '../types';

/**
 * Global chart configuration defaults applied to all charts
 */
export const CHART_CONFIG = {
  // Default settings used for all chart types
  defaults: {
    font: {
      family: 'Open Sans, sans-serif',
      size: 14
    },
    color: '#2C3E50', // Dark gray for text
    backgroundColor: '#FFFFFF', // White background
    borderColor: '#E0E0E0', // Light gray border
    animations: {
      duration: 1000,
      easing: 'easeOutQuart'
    }
  },
  
  // Responsive configuration for different screen sizes
  responsive: {
    maintainAspectRatio: true,
    aspectRatio: 2, // Default aspect ratio
    resizeDelay: 200, // Debounce resize events
  },
  
  // Animation settings
  animation: {
    duration: 1000,
    easing: 'easeInOutQuad',
    delay: (context) => context.dataIndex * 100
  }
};

/**
 * Configuration specific to line charts for time series visualization
 */
export const LINE_CHART_CONFIG: { options: ChartOptions<'line'> } = {
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          tooltipFormat: 'MMM DD, YYYY',
          displayFormats: {
            day: 'MMM DD',
            week: 'MMM DD',
            month: 'MMM YYYY'
          }
        },
        grid: {
          display: true,
          drawBorder: true,
          color: 'rgba(224, 224, 224, 0.5)' // Light gray grid lines
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        beginAtZero: false,
        grace: '5%', // Add some padding at the top
        grid: {
          display: true,
          drawBorder: true,
          color: 'rgba(224, 224, 224, 0.5)' // Light gray grid lines
        },
        ticks: {
          callback: function(value) {
            // Format currency values properly
            return '$' + value.toLocaleString('en-US');
          }
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(26, 82, 118, 0.8)', // Deep blue with opacity
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 4,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `$${context.parsed.y.toLocaleString('en-US')}`;
          }
        }
      },
      legend: {
        display: true,
        position: 'top',
        align: 'center',
        labels: {
          boxWidth: 12,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      title: {
        display: true,
        text: 'Freight Price Movement',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    elements: {
      line: {
        tension: 0.3, // Smooth curve
        borderWidth: 2,
        fill: false
      },
      point: {
        radius: 3,
        hoverRadius: 5,
        hitRadius: 10,
        borderWidth: 2
      }
    }
  }
};

/**
 * Configuration specific to bar charts for comparison visualization
 */
export const BAR_CHART_CONFIG: { options: ChartOptions<'bar'> } = {
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: true
        }
      },
      y: {
        beginAtZero: false,
        grace: '5%', // Add some padding at the top
        grid: {
          display: true,
          drawBorder: true,
          color: 'rgba(224, 224, 224, 0.5)' // Light gray grid lines
        },
        ticks: {
          callback: function(value) {
            // Format currency values properly
            return '$' + value.toLocaleString('en-US');
          }
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(26, 82, 118, 0.8)', // Deep blue with opacity
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 4,
        displayColors: true
      },
      legend: {
        display: true,
        position: 'top',
        align: 'center',
        labels: {
          boxWidth: 12,
          usePointStyle: false
        }
      },
      title: {
        display: true,
        text: 'Price Comparison',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    elements: {
      bar: {
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }
    }
  }
};

/**
 * Configuration specific to trend charts with direction highlighting
 */
export const TREND_CHART_CONFIG: { options: ChartOptions<'line'> } = {
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          tooltipFormat: 'MMM DD, YYYY',
          displayFormats: {
            day: 'MMM DD',
            week: 'MMM DD',
            month: 'MMM YYYY'
          }
        },
        grid: {
          display: true,
          drawBorder: true,
          color: 'rgba(224, 224, 224, 0.5)' // Light gray grid lines
        },
        ticks: {
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        beginAtZero: false,
        grace: '5%', // Add some padding at the top
        grid: {
          display: true,
          drawBorder: true,
          color: 'rgba(224, 224, 224, 0.5)' // Light gray grid lines
        },
        ticks: {
          callback: function(value) {
            // Format currency values properly
            return '$' + value.toLocaleString('en-US');
          }
        }
      }
    },
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      tooltip: {
        enabled: true,
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(26, 82, 118, 0.8)', // Deep blue with opacity
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 4,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `$${context.parsed.y.toLocaleString('en-US')}`;
          },
          afterLabel: function(context) {
            // Add trend information if available
            if (context.dataset.trendDirection) {
              return `Trend: ${context.dataset.trendDirection}`;
            }
            return '';
          }
        }
      },
      legend: {
        display: true,
        position: 'top',
        align: 'center',
        labels: {
          boxWidth: 12,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      title: {
        display: true,
        text: 'Price Trend Analysis',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    elements: {
      line: {
        tension: 0.3, // Smooth curve
        borderWidth: 2,
        fill: 'origin' // Fill area below the line
      },
      point: {
        radius: 3,
        hoverRadius: 5,
        hitRadius: 10,
        borderWidth: 2
      }
    }
  }
};

/**
 * Theme-specific color schemes for charts
 */
export const CHART_THEME_COLORS = {
  light: {
    background: '#FFFFFF',
    text: '#2C3E50',
    grid: 'rgba(224, 224, 224, 0.5)',
    primary: CHART_COLORS.PRIMARY,
    secondary: CHART_COLORS.SECONDARY,
    success: CHART_COLORS.SUCCESS,
    warning: CHART_COLORS.WARNING,
    danger: CHART_COLORS.DANGER,
    tooltip: {
      background: 'rgba(26, 82, 118, 0.8)',
      text: '#FFFFFF',
      border: 'rgba(255, 255, 255, 0.2)'
    }
  },
  dark: {
    background: '#2C3E50',
    text: '#F8F9F9',
    grid: 'rgba(255, 255, 255, 0.1)',
    primary: '#2980B9', // Lighter blue for dark mode
    secondary: '#1ABC9C', // Lighter teal for dark mode
    success: '#2ECC71', // Lighter green for dark mode
    warning: '#F1C40F', // Lighter amber for dark mode
    danger: '#E74C3C', // Lighter red for dark mode
    tooltip: {
      background: 'rgba(22, 45, 67, 0.9)',
      text: '#FFFFFF',
      border: 'rgba(255, 255, 255, 0.2)'
    }
  }
};

/**
 * Color definitions for different trend directions
 */
export const TREND_COLORS = {
  [TrendDirection.INCREASING]: CHART_COLORS.SUCCESS, // Green for increasing trend
  [TrendDirection.DECREASING]: CHART_COLORS.DANGER,  // Red for decreasing trend
  [TrendDirection.STABLE]: CHART_COLORS.WARNING      // Amber for stable trend
};

/**
 * Responsive dimension settings for different device sizes
 */
export const CHART_DIMENSIONS = {
  mobile: {
    aspectRatio: 1.2,  // More square on mobile
    height: 250,
    padding: 10,
    fontSize: 12,
    legendDisplay: false,
    maxWidth: BREAKPOINTS.MOBILE
  },
  tablet: {
    aspectRatio: 1.5,
    height: 300,
    padding: 15,
    fontSize: 14,
    legendDisplay: true,
    maxWidth: BREAKPOINTS.TABLET
  },
  laptop: {
    aspectRatio: 2,
    height: 350,
    padding: 20,
    fontSize: 14,
    legendDisplay: true,
    maxWidth: BREAKPOINTS.LAPTOP
  },
  desktop: {
    aspectRatio: 2.5, // Wider on desktop
    height: 400,
    padding: 20,
    fontSize: 14,
    legendDisplay: true,
    maxWidth: BREAKPOINTS.DESKTOP
  }
};

/**
 * Formatter functions for chart tooltips
 */
export const TOOLTIP_FORMATTERS = {
  /**
   * Formats price values for tooltips
   * @param value - The price value to format
   * @param currency - Optional currency code (defaults to USD)
   * @returns Formatted price string
   */
  price: (value: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: currency 
    }).format(value);
  },
  
  /**
   * Formats percentage values for tooltips
   * @param value - The percentage value to format
   * @returns Formatted percentage string
   */
  percentage: (value: number): string => {
    const formattedValue = value.toFixed(2);
    const sign = value > 0 ? '+' : '';
    return `${sign}${formattedValue}%`;
  },
  
  /**
   * Formats date values for tooltips
   * @param date - The date to format (string or Date object)
   * @param format - Optional format type ('short', 'medium', 'long')
   * @returns Formatted date string
   */
  date: (date: string | Date, format: 'short' | 'medium' | 'long' = 'medium'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: format === 'short' ? 'short' : 'long',
      day: 'numeric'
    };
    
    return dateObj.toLocaleDateString('en-US', options);
  }
};