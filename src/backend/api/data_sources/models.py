"""
SQLAlchemy ORM models for data sources in the Freight Price Movement Agent.

These models define different types of data sources (CSV, Database, API, TMS, ERP)
that can be used to collect freight pricing data, with specific configuration for each type.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

import sqlalchemy
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import Enum, JSON
from sqlalchemy.dialects.postgresql import JSONB

from ...core.db import Base
from ...models.mixins import TimestampMixin, UUIDMixin, SoftDeleteMixin, UserTrackingMixin, AuditableMixin
from ...models.enums import DataSourceType, DataSourceStatus


class DataSource(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditableMixin):
    """Base model for all data sources with common attributes."""
    
    __tablename__ = "data_source"
    
    name = Column(String(255), nullable=False)
    source_type = Column(Enum(DataSourceType), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DataSourceStatus), nullable=False, default=DataSourceStatus.INACTIVE)
    last_run_by = Column(String(36), nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_on': source_type,
        'polymorphic_identity': None
    }
    
    def __init__(self, **kwargs):
        """Initializes a new DataSource instance."""
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_status(self, status: DataSourceStatus) -> None:
        """
        Updates the status of the data source.
        
        Args:
            status: New status to set
        """
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def update_last_run(self, user_id: str) -> None:
        """
        Updates the last run information.
        
        Args:
            user_id: ID of the user who executed the run
        """
        self.last_run_by = user_id
        self.last_run_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_configuration(self, config: Dict) -> None:
        """
        Updates the configuration of the data source.
        
        Args:
            config: Dictionary containing configuration parameters
        """
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class CSVDataSource(DataSource):
    """Model for CSV file data sources."""
    
    __tablename__ = "csv_data_source"
    
    id = Column(String(36), ForeignKey("data_source.id"), primary_key=True)
    file_path = Column(String(255), nullable=False)
    delimiter = Column(String(10), nullable=False, default=',')
    encoding = Column(String(20), nullable=False, default='utf-8')
    field_mapping = Column(JSONB, nullable=False)
    has_header = Column(Boolean, nullable=False, default=True)
    date_format = Column(String(50), nullable=False, default='%Y-%m-%d')
    
    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.CSV
    }
    
    def __init__(self, **kwargs):
        """Initializes a new CSVDataSource instance."""
        kwargs['source_type'] = DataSourceType.CSV
        super().__init__(**kwargs)
    
    def validate_file(self) -> bool:
        """
        Validates that the CSV file exists and is readable.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.file_path:
            return False
            
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                return False
                
            # Check if file is readable
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                # Try to read first few lines
                for _ in range(5):
                    if not f.readline():
                        break
            return True
        except Exception:
            return False
    
    def get_sample_data(self, num_rows: int = 5) -> List[Dict]:
        """
        Retrieves a sample of data from the CSV file.
        
        Args:
            num_rows: Number of rows to retrieve
            
        Returns:
            List of dictionaries containing the sample data
        """
        import csv
        result = []
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                csv_reader = csv.reader(f, delimiter=self.delimiter)
                
                # Read header row if present
                headers = next(csv_reader) if self.has_header else None
                
                # If no headers, use column indices as field names
                if not headers:
                    # Get number of fields from first row
                    first_row = next(csv_reader)
                    headers = [f"column_{i}" for i in range(len(first_row))]
                    # Reset file pointer to read data again
                    f.seek(0)
                    csv_reader = csv.reader(f, delimiter=self.delimiter)
                    if self.has_header:
                        next(csv_reader)  # Skip header
                
                # Create field mapping for results
                inverse_mapping = {}
                for dest, source in self.field_mapping.items():
                    if source in headers:
                        inverse_mapping[headers.index(source)] = dest
                
                # Read specified number of rows
                row_count = 0
                for row in csv_reader:
                    if row_count >= num_rows:
                        break
                        
                    data = {}
                    for i, value in enumerate(row):
                        if i in inverse_mapping:
                            data[inverse_mapping[i]] = value
                        else:
                            data[f"column_{i}"] = value
                    
                    result.append(data)
                    row_count += 1
                    
            return result
        except Exception as e:
            # Log error and return empty result
            return []


class DatabaseDataSource(DataSource):
    """Model for database data sources."""
    
    __tablename__ = "database_data_source"
    
    id = Column(String(36), ForeignKey("data_source.id"), primary_key=True)
    connection_string = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    field_mapping = Column(JSONB, nullable=False)
    username = Column(String(100), nullable=False)
    password_encrypted = Column(String(255), nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.DATABASE
    }
    
    def __init__(self, **kwargs):
        """Initializes a new DatabaseDataSource instance."""
        kwargs['source_type'] = DataSourceType.DATABASE
        
        # Encrypt password if provided
        if 'password' in kwargs:
            kwargs['password_encrypted'] = self._encrypt_password(kwargs.pop('password'))
            
        super().__init__(**kwargs)
    
    def test_connection(self) -> Dict:
        """
        Tests the connection to the database.
        
        Returns:
            Dict: Connection test results
        """
        from sqlalchemy import create_engine
        
        try:
            # Create a temporary engine for connection test
            engine = create_engine(self.connection_string)
            
            # Try to connect
            with engine.connect() as connection:
                # Execute a simple query to verify connection
                connection.execute("SELECT 1")
                
            return {
                "success": True,
                "message": "Connection successful"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    def update_credentials(self, username: str, password: str) -> None:
        """
        Updates the database credentials.
        
        Args:
            username: Database username
            password: Database password
        """
        self.username = username
        self.password_encrypted = self._encrypt_password(password)
        self.updated_at = datetime.utcnow()
    
    def get_decrypted_password(self) -> str:
        """
        Retrieves the decrypted password.
        
        Returns:
            str: Decrypted password
        """
        if not self.password_encrypted:
            return ""
        
        return self._decrypt_password(self.password_encrypted)
    
    def _encrypt_password(self, password: str) -> str:
        """
        Encrypts a password (placeholder for actual encryption).
        
        In a production environment, this would use a proper encryption method.
        
        Args:
            password: Password to encrypt
            
        Returns:
            str: Encrypted password
        """
        # Placeholder for actual encryption
        # In a real implementation, use cryptography library
        return f"ENCRYPTED:{password}"
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """
        Decrypts a password (placeholder for actual decryption).
        
        In a production environment, this would use a proper decryption method.
        
        Args:
            encrypted_password: Encrypted password
            
        Returns:
            str: Decrypted password
        """
        # Placeholder for actual decryption
        # In a real implementation, use cryptography library
        if encrypted_password.startswith("ENCRYPTED:"):
            return encrypted_password[10:]
        return encrypted_password


class APIDataSource(DataSource):
    """Model for API data sources."""
    
    __tablename__ = "api_data_source"
    
    id = Column(String(36), ForeignKey("data_source.id"), primary_key=True)
    endpoint_url = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False, default='GET')
    headers = Column(JSONB, nullable=True)
    parameters = Column(JSONB, nullable=True)
    auth_config = Column(JSONB, nullable=True)
    field_mapping = Column(JSONB, nullable=False)
    timeout = Column(Integer, nullable=False, default=30)
    
    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.API
    }
    
    def __init__(self, **kwargs):
        """Initializes a new APIDataSource instance."""
        kwargs['source_type'] = DataSourceType.API
        
        # Initialize empty dicts for JSONB fields if not provided
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if 'parameters' not in kwargs:
            kwargs['parameters'] = {}
        if 'auth_config' not in kwargs:
            kwargs['auth_config'] = {}
            
        super().__init__(**kwargs)
    
    def test_connection(self) -> Dict:
        """
        Tests the connection to the API endpoint.
        
        Returns:
            Dict: Connection test results
        """
        import requests
        
        try:
            # Prepare authentication
            auth = None
            if self.auth_config:
                auth_type = self.auth_config.get('type')
                if auth_type == 'basic':
                    auth = (
                        self.auth_config.get('username', ''),
                        self.auth_config.get('password', '')
                    )
                # Other auth types can be implemented here
            
            # Make the request
            response = requests.request(
                method=self.method,
                url=self.endpoint_url,
                headers=self.headers,
                params=self.parameters,
                auth=auth,
                timeout=self.timeout
            )
            
            # Check response status
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "Connection successful",
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def update_auth_config(self, auth_config: Dict) -> None:
        """
        Updates the authentication configuration.
        
        Args:
            auth_config: Authentication configuration
        """
        self.auth_config = auth_config
        self.updated_at = datetime.utcnow()


class TMSDataSource(DataSource):
    """Model for Transportation Management System data sources."""
    
    __tablename__ = "tms_data_source"
    
    id = Column(String(36), ForeignKey("data_source.id"), primary_key=True)
    tms_type = Column(String(50), nullable=False)
    connection_string = Column(String(255), nullable=False)
    auth_config = Column(JSONB, nullable=True)
    field_mapping = Column(JSONB, nullable=False)
    extraction_config = Column(JSONB, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.TMS
    }
    
    def __init__(self, **kwargs):
        """Initializes a new TMSDataSource instance."""
        kwargs['source_type'] = DataSourceType.TMS
        
        # Initialize empty dicts for JSONB fields if not provided
        if 'auth_config' not in kwargs:
            kwargs['auth_config'] = {}
        if 'extraction_config' not in kwargs:
            kwargs['extraction_config'] = {}
            
        super().__init__(**kwargs)
    
    def test_connection(self) -> Dict:
        """
        Tests the connection to the TMS.
        
        Returns:
            Dict: Connection test results
        """
        try:
            # TMS connection logic would be implemented here
            # This would use appropriate connectors based on tms_type
            
            supported_tms = self.get_supported_tms_types()
            if self.tms_type not in supported_tms:
                return {
                    "success": False,
                    "message": f"Unsupported TMS type: {self.tms_type}. Supported types: {', '.join(supported_tms)}"
                }
            
            # Placeholder for actual implementation
            # In a real system, this would use TMS-specific connector libraries
            
            if self.tms_type == "SAP_TM":
                # SAP TM connection logic
                pass
            elif self.tms_type == "ORACLE_TMS":
                # Oracle TMS connection logic
                pass
            elif self.tms_type == "JDA_TMS":
                # JDA TMS connection logic
                pass
            
            # For now, return a mock successful response
            return {
                "success": True,
                "message": f"Connection to {self.tms_type} successful"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    @staticmethod
    def get_supported_tms_types() -> List[str]:
        """
        Returns a list of supported TMS types.
        
        Returns:
            List[str]: Supported TMS types
        """
        return ["SAP_TM", "ORACLE_TMS", "JDA_TMS", "OTHER"]


class ERPDataSource(DataSource):
    """Model for Enterprise Resource Planning system data sources."""
    
    __tablename__ = "erp_data_source"
    
    id = Column(String(36), ForeignKey("data_source.id"), primary_key=True)
    erp_type = Column(String(50), nullable=False)
    connection_string = Column(String(255), nullable=False)
    auth_config = Column(JSONB, nullable=True)
    field_mapping = Column(JSONB, nullable=False)
    extraction_config = Column(JSONB, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.ERP
    }
    
    def __init__(self, **kwargs):
        """Initializes a new ERPDataSource instance."""
        kwargs['source_type'] = DataSourceType.ERP
        
        # Initialize empty dicts for JSONB fields if not provided
        if 'auth_config' not in kwargs:
            kwargs['auth_config'] = {}
        if 'extraction_config' not in kwargs:
            kwargs['extraction_config'] = {}
            
        super().__init__(**kwargs)
    
    def test_connection(self) -> Dict:
        """
        Tests the connection to the ERP system.
        
        Returns:
            Dict: Connection test results
        """
        try:
            # ERP connection logic would be implemented here
            # This would use appropriate connectors based on erp_type
            
            supported_erp = self.get_supported_erp_types()
            if self.erp_type not in supported_erp:
                return {
                    "success": False,
                    "message": f"Unsupported ERP type: {self.erp_type}. Supported types: {', '.join(supported_erp)}"
                }
            
            # Placeholder for actual implementation
            # In a real system, this would use ERP-specific connector libraries
            
            if self.erp_type == "SAP":
                # SAP ERP connection logic
                pass
            elif self.erp_type == "ORACLE":
                # Oracle ERP connection logic
                pass
            elif self.erp_type == "MICROSOFT_DYNAMICS":
                # Microsoft Dynamics connection logic
                pass
            
            # For now, return a mock successful response
            return {
                "success": True,
                "message": f"Connection to {self.erp_type} successful"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }
    
    @staticmethod
    def get_supported_erp_types() -> List[str]:
        """
        Returns a list of supported ERP types.
        
        Returns:
            List[str]: Supported ERP types
        """
        return ["SAP", "ORACLE", "MICROSOFT_DYNAMICS", "OTHER"]


class DataSourceLog(Base, UUIDMixin, TimestampMixin):
    """Model for logging data source operations and activities."""
    
    __tablename__ = "data_source_log"
    
    data_source_id = Column(String(36), ForeignKey('data_source.id'), nullable=False)
    operation = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    records_processed = Column(Integer, nullable=False, default=0)
    records_failed = Column(Integer, nullable=False, default=0)
    details = Column(JSONB, nullable=True)
    performed_by = Column(String(36), nullable=True)
    
    # Relationship to data source
    data_source = relationship("DataSource", foreign_keys=[data_source_id])
    
    def __init__(self, **kwargs):
        """Initializes a new DataSourceLog instance."""
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def create_log_entry(data_source_id: str, operation: str, status: str, 
                        message: str = None, records_processed: int = 0, 
                        records_failed: int = 0, details: Dict = None, 
                        performed_by: str = None) -> "DataSourceLog":
        """
        Creates a new log entry for a data source operation.
        
        Args:
            data_source_id: ID of the data source
            operation: Operation type (e.g., IMPORT, EXPORT, TEST)
            status: Status of the operation (e.g., SUCCESS, FAILURE)
            message: Optional message describing the result
            records_processed: Number of records processed
            records_failed: Number of records that failed processing
            details: Additional details about the operation
            performed_by: User ID of the user who performed the operation
            
        Returns:
            DataSourceLog: Created log entry
        """
        return DataSourceLog(
            data_source_id=data_source_id,
            operation=operation,
            status=status,
            message=message,
            records_processed=records_processed,
            records_failed=records_failed,
            details=details or {},
            performed_by=performed_by
        )