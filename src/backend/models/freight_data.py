"""
Freight data model for the Freight Price Movement Agent application.

This module defines the FreightData SQLAlchemy model which represents the
core freight pricing data that will be analyzed for price movements over time.
It includes relationships to carriers, locations (origin/destination), and routes,
along with a junction table for many-to-many relationships with routes.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

import sqlalchemy
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import JSONB

from ..core.db import Base
from .enums import TransportMode
from .mixins import (
    UUIDMixin, 
    TimestampMixin, 
    SoftDeleteMixin, 
    UserTrackingMixin,
    TimescaleDBModelMixin,
    AuditableMixin
)


class FreightDataRoute(Base):
    """
    Junction table model for many-to-many relationship between FreightData and Route.
    """
    __tablename__ = "freight_data_route"
    
    freight_data_id = Column(String(36), ForeignKey('freight_data.id'), primary_key=True)
    route_id = Column(String(36), ForeignKey('route.id'), primary_key=True)


class FreightData(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, 
                 UserTrackingMixin, TimescaleDBModelMixin, AuditableMixin):
    """
    SQLAlchemy model representing freight pricing data for analysis.
    
    This model stores the core freight pricing data that will be analyzed 
    for price movements over time. It includes fields for freight charges,
    origins, destinations, carriers, and transportation modes, along with
    relationships to related entities.
    """
    __tablename__ = "freight_data"
    
    # Core data fields
    record_date = Column(DateTime, nullable=False, index=True)
    origin_id = Column(String(36), ForeignKey('location.id'), nullable=False, index=True)
    destination_id = Column(String(36), ForeignKey('location.id'), nullable=False, index=True)
    carrier_id = Column(String(36), ForeignKey('carrier.id'), nullable=False, index=True)
    freight_charge = Column(Numeric(precision=12, scale=2), nullable=False)
    currency_code = Column(String(3), nullable=False, default='USD')
    transport_mode = Column(Enum(TransportMode), nullable=False, index=True)
    service_level = Column(String(100), nullable=True)
    additional_charges = Column(JSONB, nullable=True)
    source_system = Column(String(100), nullable=True)
    data_quality_flag = Column(String(50), nullable=True)
    
    # Relationships
    origin = relationship('Location', foreign_keys=[origin_id], back_populates='origin_freight_data')
    destination = relationship('Location', foreign_keys=[destination_id], back_populates='destination_freight_data')
    carrier = relationship('Carrier', back_populates='freight_data')
    routes = relationship('Route', secondary='freight_data_route', back_populates='freight_data')
    
    def __init__(self, record_date: datetime, origin_id: str, destination_id: str, 
                carrier_id: str, freight_charge: float, transport_mode: TransportMode,
                currency_code: Optional[str] = 'USD', service_level: Optional[str] = None,
                additional_charges: Optional[dict] = None, source_system: Optional[str] = None,
                data_quality_flag: Optional[str] = None):
        """
        Initialize a FreightData instance.
        
        Args:
            record_date: Date and time of the freight data record
            origin_id: ID of the origin location
            destination_id: ID of the destination location
            carrier_id: ID of the carrier
            freight_charge: Freight charge amount
            transport_mode: Mode of transportation (OCEAN, AIR, ROAD, RAIL, etc.)
            currency_code: 3-letter currency code (default: 'USD')
            service_level: Optional service level description
            additional_charges: Optional JSON object for additional charges
            source_system: Optional source system identifier
            data_quality_flag: Optional flag indicating data quality issues
        """
        self.record_date = record_date
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.carrier_id = carrier_id
        self.freight_charge = freight_charge
        self.transport_mode = transport_mode
        self.currency_code = currency_code
        
        if service_level:
            self.service_level = service_level
        
        if additional_charges:
            self.additional_charges = additional_charges
            
        if source_system:
            self.source_system = source_system
            
        if data_quality_flag:
            self.data_quality_flag = data_quality_flag
    
    def __repr__(self) -> str:
        """
        Return a string representation of the FreightData.
        
        Returns:
            String representation including record date, origin, destination and freight charge
        """
        return f"<FreightData(id={self.id}, date={self.record_date}, origin={self.origin_id}, " \
               f"destination={self.destination_id}, charge={self.freight_charge})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the FreightData model to a dictionary.
        
        Returns:
            Dictionary representation of the freight data
        """
        return {
            'id': self.id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'origin_id': self.origin_id,
            'destination_id': self.destination_id,
            'carrier_id': self.carrier_id,
            'freight_charge': float(self.freight_charge) if self.freight_charge else None,
            'currency_code': self.currency_code,
            'transport_mode': self.transport_mode.name if self.transport_mode else None,
            'service_level': self.service_level,
            'additional_charges': self.additional_charges,
            'source_system': self.source_system,
            'data_quality_flag': self.data_quality_flag,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
    
    @classmethod
    def search(cls, session: Session, start_date: Optional[datetime] = None, 
              end_date: Optional[datetime] = None, origin_id: Optional[str] = None,
              destination_id: Optional[str] = None, carrier_id: Optional[str] = None,
              transport_mode: Optional[TransportMode] = None,
              limit: Optional[int] = None, offset: Optional[int] = None) -> List['FreightData']:
        """
        Search for freight data by various criteria.
        
        Args:
            session: SQLAlchemy session
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            origin_id: Optional origin location ID for filtering
            destination_id: Optional destination location ID for filtering
            carrier_id: Optional carrier ID for filtering
            transport_mode: Optional transport mode for filtering
            limit: Optional limit for results
            offset: Optional offset for pagination
            
        Returns:
            List of matching FreightData instances
        """
        query = session.query(cls)
        
        # Apply filters
        if start_date:
            query = query.filter(cls.record_date >= start_date)
        
        if end_date:
            query = query.filter(cls.record_date <= end_date)
            
        if origin_id:
            query = query.filter(cls.origin_id == origin_id)
            
        if destination_id:
            query = query.filter(cls.destination_id == destination_id)
            
        if carrier_id:
            query = query.filter(cls.carrier_id == carrier_id)
            
        if transport_mode:
            query = query.filter(cls.transport_mode == transport_mode)
        
        # Filter out soft-deleted records
        query = query.filter(cls.is_deleted == False)
        
        # Apply pagination
        if limit is not None:
            query = query.limit(limit)
            
        if offset is not None:
            query = query.offset(offset)
        
        return query.all()
    
    @classmethod
    def get_for_analysis(cls, session: Session, start_date: datetime, end_date: datetime,
                       origin_ids: Optional[List[str]] = None, 
                       destination_ids: Optional[List[str]] = None,
                       carrier_ids: Optional[List[str]] = None,
                       transport_modes: Optional[List[TransportMode]] = None) -> List['FreightData']:
        """
        Retrieve freight data for price movement analysis.
        
        Args:
            session: SQLAlchemy session
            start_date: Start date for analysis
            end_date: End date for analysis
            origin_ids: Optional list of origin location IDs
            destination_ids: Optional list of destination location IDs
            carrier_ids: Optional list of carrier IDs
            transport_modes: Optional list of transport modes
            
        Returns:
            List of FreightData instances for analysis
        """
        query = session.query(cls).filter(
            cls.record_date >= start_date,
            cls.record_date <= end_date,
            cls.is_deleted == False
        )
        
        # Apply optional filters
        if origin_ids:
            query = query.filter(cls.origin_id.in_(origin_ids))
            
        if destination_ids:
            query = query.filter(cls.destination_id.in_(destination_ids))
            
        if carrier_ids:
            query = query.filter(cls.carrier_id.in_(carrier_ids))
            
        if transport_modes:
            query = query.filter(cls.transport_mode.in_(transport_modes))
        
        # Order by record date
        query = query.order_by(cls.record_date)
        
        return query.all()
    
    @classmethod
    def setup_timescaledb_hypertable(cls, engine, chunk_time_interval: Optional[int] = None) -> None:
        """
        Set up TimescaleDB hypertable for time-series optimization.
        
        Args:
            engine: SQLAlchemy engine instance
            chunk_time_interval: Optional time interval for chunks in days (default: 7 days)
        """
        # Default chunk_time_interval to 7 days if not provided
        interval = chunk_time_interval or 7
        
        # Call the setup_timescaledb method from TimescaleDBModelMixin
        cls.setup_timescaledb(engine, 'record_date', interval)