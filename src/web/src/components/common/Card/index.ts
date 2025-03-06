/**
 * Barrel file for the Card component
 * 
 * This file re-exports the Card component to simplify imports throughout the application.
 * Consumers can import the Card component using:
 * import Card from 'components/common/Card';
 */

// Import the Card component from its implementation file
import Card from './Card';

// Re-export the Card component as the default export
export default Card;

// Re-export the Card component types for consumers that need them
export type { CardProps } from './Card';