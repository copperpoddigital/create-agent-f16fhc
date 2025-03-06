"""
Route model for the Freight Price Movement Agent application.

This module defines the SQLAlchemy model for routes, which represent
predefined origin-destination pairs with associated transport mode and
distance information. Routes serve as reference entities for freight
pricing data analysis.
"""

from typing import Optional, Tuple, List

import sqlalchemy
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, Session

from ..core.db import Base
from .enums import TransportMode
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Route(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing a predefined route (origin-destination pair) in the system.
    
    A route defines a specific path between an origin and destination location
    with an associated transport mode and optional distance information.
    Routes are used as reference data for freight pricing analysis.
    """
    __tablename__ = 'route'
    
    # Foreign keys to Location model
    origin_id = Column(String(36), ForeignKey('location.id'), nullable=False, index=True)
    destination_id = Column(String(36), ForeignKey('location.id'), nullable=False, index=True)
    
    # Route properties
    transport_mode = Column(Enum(TransportMode), nullable=False, index=True)
    distance = Column(Numeric(precision=10, scale=2), nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    origin = relationship('Location', foreign_keys=[origin_id], back_populates='origin_routes')
    destination = relationship('Location', foreign_keys=[destination_id], back_populates='destination_routes')
    freight_data = relationship('FreightData', secondary='freight_data_route', back_populates='routes')
    
    def __init__(self, origin_id: str, destination_id: str, transport_mode: TransportMode, 
                 distance: Optional[float] = None, active: bool = True):
        """
        Initialize a new Route instance.
        
        Args:
            origin_id: ID of the origin location
            destination_id: ID of the destination location
            transport_mode: Mode of transportation for this route
            distance: Optional distance between origin and destination in km
            active: Whether the route is active (default True)
        """
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.transport_mode = transport_mode
        self.distance = distance
        self.active = active
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Route.
        
        Returns:
            String representation including origin ID, destination ID, and transport mode
        """
        return f"Route(origin_id='{self.origin_id}', destination_id='{self.destination_id}', transport_mode={self.transport_mode})"
    
    def to_dict(self) -> dict:
        """
        Converts the Route model to a dictionary.
        
        Returns:
            Dictionary representation of the route
        """
        return {
            'id': self.id,
            'origin_id': self.origin_id,
            'destination_id': self.destination_id,
            'transport_mode': self.transport_mode.name if self.transport_mode else None,
            'distance': float(self.distance) if self.distance is not None else None,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
    
    @classmethod
    def get_by_locations(cls, session: Session, origin_id: str, 
                         destination_id: str, transport_mode: TransportMode) -> Optional['Route']:
        """
        Class method to retrieve a route by origin and destination IDs and transport mode.
        
        Args:
            session: SQLAlchemy session
            origin_id: ID of the origin location
            destination_id: ID of the destination location
            transport_mode: Mode of transportation
            
        Returns:
            Route instance or None if not found
        """
        return session.query(cls).filter(
            cls.origin_id == origin_id,
            cls.destination_id == destination_id,
            cls.transport_mode == transport_mode,
            cls.is_deleted == False
        ).first()
    
    @classmethod
    def search(cls, session: Session, origin_id: Optional[str] = None, 
               destination_id: Optional[str] = None, transport_mode: Optional[TransportMode] = None,
               active_only: Optional[bool] = True, limit: Optional[int] = None, 
               offset: Optional[int] = None) -> List['Route']:
        """
        Class method to search for routes by various criteria.
        
        Args:
            session: SQLAlchemy session
            origin_id: Optional filter by origin location ID
            destination_id: Optional filter by destination location ID
            transport_mode: Optional filter by transport mode
            active_only: If True, only return active routes
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of matching Route instances
        """
        query = session.query(cls).filter(cls.is_deleted == False)
        
        # Apply filters if provided
        if origin_id:
            query = query.filter(cls.origin_id == origin_id)
        
        if destination_id:
            query = query.filter(cls.destination_id == destination_id)
        
        if transport_mode:
            query = query.filter(cls.transport_mode == transport_mode)
        
        if active_only:
            query = query.filter(cls.active == True)
        
        # Apply pagination if provided
        if limit is not None:
            query = query.limit(limit)
        
        if offset is not None:
            query = query.offset(offset)
        
        return query.all()
    
    @classmethod
    def get_or_create(cls, session: Session, origin_id: str, destination_id: str, 
                      transport_mode: TransportMode, distance: Optional[float] = None) -> Tuple['Route', bool]:
        """
        Class method to get an existing route or create a new one if it doesn't exist.
        
        Args:
            session: SQLAlchemy session
            origin_id: ID of the origin location
            destination_id: ID of the destination location
            transport_mode: Mode of transportation
            distance: Optional distance between origin and destination
            
        Returns:
            Tuple of (route, created) where created is True if a new route was created
        """
        # Try to find existing route
        existing_route = cls.get_by_locations(
            session=session,
            origin_id=origin_id,
            destination_id=destination_id,
            transport_mode=transport_mode
        )
        
        if existing_route:
            return existing_route, False
        
        # Create new route if not found
        new_route = cls(
            origin_id=origin_id,
            destination_id=destination_id,
            transport_mode=transport_mode,
            distance=distance
        )
        
        session.add(new_route)
        return new_route, True