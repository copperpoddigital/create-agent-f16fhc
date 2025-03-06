/**
 * Barrel file for common UI components
 * 
 * This file re-exports all common UI components to simplify imports throughout the application.
 * Instead of importing from individual component files, consumers can import from this single file.
 * 
 * This implementation addresses the Component Library and UI Component Organization requirements
 * specified in the Technical Specifications section 7 USER INTERFACE DESIGN.
 */

// Import components from individual files
import Button from './Button';
import Badge from './Badge';
import Card from './Card';
import Checkbox from './Checkbox';
import DatePicker from './DatePicker';
import Icon from './Icon';
import Input from './Input';
import RadioButton from './RadioButton';
import Select from './Select';
import Spinner from './Spinner';
import Tooltip from './Tooltip';
import FormGroup from './FormGroup';
import Pagination from './Pagination';
import Table from './Table';
import { TableProps, TableColumn } from './Table';
import Tabs from './Tabs';
import Alert from './Alert';
import Modal from './Modal';

// Export all components with named exports
export {
  Button,
  Badge,
  Card,
  Checkbox,
  DatePicker,
  Icon,
  Input,
  RadioButton,
  Select,
  Spinner,
  Tooltip,
  FormGroup,
  Pagination,
  Table,
  TableProps,
  TableColumn,
  Tabs,
  Alert,
  Modal,
};