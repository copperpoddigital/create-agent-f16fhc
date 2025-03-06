"""
Reusable SQLAlchemy model mixins for the Freight Price Movement Agent application.

These mixins provide standardized functionality for ORM models including:
- UUID primary keys
- Timestamp tracking
- Soft deletion
- User tracking
- TimescaleDB integration
- Audit logging
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

import sqlalchemy
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, Session

from ..core.db import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamp fields to models.
    
    Tracks when records are created and last updated automatically.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """
    Mixin that adds a UUID primary key to models.
    
    Generates a unique UUID string as the primary key for each record.
    """
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class SoftDeleteMixin:
    """
    Mixin that adds soft deletion capability to models.
    
    Instead of physically deleting records, they are marked as deleted and
    filtered out of normal queries. Allows for data recovery if needed.
    """
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def delete(self):
        """
        Marks the record as deleted rather than physically removing it.
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """
        Restores a soft-deleted record.
        """
        self.is_deleted = False
        self.deleted_at = None


class UserTrackingMixin:
    """
    Mixin that adds user tracking fields to models.
    
    Tracks which users created, updated, and deleted records by storing
    references to the user IDs and providing relationships to the User model.
    """
    created_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    updated_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    deleted_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def creator(cls):
        return relationship('User', foreign_keys=[cls.created_by], 
                           primaryjoin="User.id == %s.created_by" % cls.__name__)
    
    @declared_attr
    def updater(cls):
        return relationship('User', foreign_keys=[cls.updated_by], 
                           primaryjoin="User.id == %s.updated_by" % cls.__name__)
    
    @declared_attr
    def deleter(cls):
        return relationship('User', foreign_keys=[cls.deleted_by], 
                           primaryjoin="User.id == %s.deleted_by" % cls.__name__)


class TimescaleDBModelMixin:
    """
    Mixin that provides TimescaleDB-specific functionality for time-series models.
    
    Enables TimescaleDB features like hypertables, compression, and retention policies
    for efficient time-series data storage and querying.
    """
    
    @classmethod
    def setup_timescaledb(cls, engine, time_column_name: str, chunk_time_interval: Optional[int] = None):
        """
        Class method to set up TimescaleDB features for a model.
        
        Args:
            engine: SQLAlchemy engine instance
            time_column_name: Name of the column to use as the time dimension
            chunk_time_interval: Optional time interval for chunks in days
        """
        table_name = cls.__tablename__
        
        # SQL to create a hypertable
        create_hypertable_sql = f"""
        SELECT create_hypertable(
            '{table_name}', 
            '{time_column_name}', 
            if_not_exists => TRUE
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_hypertable_sql))
            
            # Set chunk time interval if provided
            if chunk_time_interval:
                interval_sql = f"""
                SELECT set_chunk_time_interval(
                    '{table_name}', 
                    INTERVAL '{chunk_time_interval} days'
                );
                """
                conn.execute(text(interval_sql))
            
            # You could add additional TimescaleDB configurations here like:
            # - Compression policy
            # - Retention policy
            # - Continuous aggregates


class AuditableMixin:
    """
    Mixin that adds audit logging capability to models.
    
    Provides methods to log record creation, updates, and deletions to an audit log
    table for compliance and traceability.
    """
    
    def log_create(self, session: Session, user_id: Optional[str] = None) -> None:
        """
        Logs the creation of a record.
        
        Args:
            session: SQLAlchemy session
            user_id: Optional ID of the user performing the action
        """
        # Create an audit log entry
        from ..models.audit import AuditLog  # Import here to avoid circular imports
        
        audit_entry = AuditLog(
            action="CREATE",
            resource_type=self.__tablename__,
            resource_id=self.id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details={"action": "Record created"}
        )
        
        session.add(audit_entry)
    
    def log_update(self, session: Session, user_id: Optional[str] = None, changes: Optional[Dict[str, Any]] = None) -> None:
        """
        Logs the update of a record.
        
        Args:
            session: SQLAlchemy session
            user_id: Optional ID of the user performing the action
            changes: Optional dictionary of changes made to the record
        """
        # Create an audit log entry
        from ..models.audit import AuditLog  # Import here to avoid circular imports
        
        details = {"action": "Record updated"}
        
        if changes:
            details["changes"] = changes
        
        audit_entry = AuditLog(
            action="UPDATE",
            resource_type=self.__tablename__,
            resource_id=self.id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details=details
        )
        
        session.add(audit_entry)
    
    def log_delete(self, session: Session, user_id: Optional[str] = None) -> None:
        """
        Logs the deletion of a record.
        
        Args:
            session: SQLAlchemy session
            user_id: Optional ID of the user performing the action
        """
        # Create an audit log entry
        from ..models.audit import AuditLog  # Import here to avoid circular imports
        
        audit_entry = AuditLog(
            action="DELETE",
            resource_type=self.__tablename__,
            resource_id=self.id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details={"action": "Record deleted"}
        )
        
        session.add(audit_entry)