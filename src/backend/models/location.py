"""
Location model module for the Freight Price Movement Agent.

This module defines the Location SQLAlchemy model, which represents geographic 
locations used as origins and destinations in freight routes and pricing data.
"""

# External imports
import sqlalchemy  # version: ^1.4.40
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship, Session  # version: ^1.4.40
from typing import Optional, List, Dict, Any, Tuple  # version: standard library
import geoalchemy2  # version: ^0.12.0

# Internal imports
from ..core.db import Base
from .enums import LocationType
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Location(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing a geographic location in the system.
    
    Locations are used as origins and destinations in freight routes and
    pricing data, supporting global geographic coverage requirements.
    """
    __tablename__ = "location"
    
    # Basic attributes
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    country = Column(String(2), nullable=False, index=True)
    region = Column(String(100), nullable=True)
    type = Column(Enum(LocationType), nullable=False, index=True)
    coordinates = Column(geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=True)
    active = Column(Boolean, default=True, index=True)
    
    # Relationships
    origin_routes = relationship('Route', foreign_keys='Route.origin_id', back_populates='origin')
    destination_routes = relationship('Route', foreign_keys='Route.destination_id', back_populates='destination')
    origin_freight_data = relationship('FreightData', foreign_keys='FreightData.origin_id', back_populates='origin')
    destination_freight_data = relationship('FreightData', foreign_keys='FreightData.destination_id', back_populates='destination')
    
    def __init__(self, name: str, code: str, country: str, type: LocationType, 
                 region: Optional[str] = None, coordinates: Optional[Tuple] = None, 
                 active: bool = True):
        """
        Initialize a new Location instance.
        
        Args:
            name: The name of the location
            code: A unique code identifying the location (e.g., airport/port code)
            country: The country code (ISO 2-letter)
            type: The type of location (from LocationType enum)
            region: Optional region or state within the country
            coordinates: Optional tuple of (latitude, longitude)
            active: Whether the location is active in the system
        """
        self.name = name
        self.code = code.upper()  # Normalize codes to uppercase
        self.country = country.upper()  # Normalize country codes to uppercase
        self.type = type
        self.region = region
        
        # Set coordinates if provided
        if coordinates:
            lat, lon = coordinates
            self.set_coordinates(lat, lon)
        
        self.active = active
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Location.
        
        Returns:
            String representation
        """
        return f"<Location {self.name} ({self.code}), {self.country}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Location model to a dictionary.
        
        Returns:
            Dictionary representation of the location
        """
        result = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'country': self.country,
            'region': self.region,
            'type': self.type.name if self.type else None,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
        
        # Add coordinates if available
        coords = self.get_coordinates()
        if coords:
            lat, lon = coords
            result['coordinates'] = {
                'latitude': lat,
                'longitude': lon
            }
        else:
            result['coordinates'] = None
            
        return result
    
    def set_coordinates(self, latitude: float, longitude: float) -> None:
        """
        Sets the coordinates for the location.
        
        Args:
            latitude: The latitude value
            longitude: The longitude value
        """
        # Validate lat/lon values
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise ValueError("Invalid latitude or longitude values")
        
        # Create WKT (Well-Known Text) representation of the point
        wkt_point = f'POINT({longitude} {latitude})'
        self.coordinates = wkt_point
    
    def get_coordinates(self) -> Optional[Tuple[float, float]]:
        """
        Gets the coordinates as a latitude/longitude tuple.
        
        Returns:
            Tuple of (latitude, longitude) or None if not set
        """
        if not self.coordinates:
            return None
        
        # Extract point geometry from WKB
        point = geoalchemy2.shape.to_shape(self.coordinates)
        # Return as (latitude, longitude) tuple
        return (point.y, point.x)
    
    @classmethod
    def search(cls, session: Session, name: Optional[str] = None, 
               code: Optional[str] = None, country: Optional[str] = None,
               type: Optional[LocationType] = None, active_only: Optional[bool] = True,
               limit: Optional[int] = None, offset: Optional[int] = None) -> List['Location']:
        """
        Class method to search for locations by various criteria.
        
        Args:
            session: SQLAlchemy session
            name: Optional name to search for (partial match)
            code: Optional code to search for (exact match)
            country: Optional country code to filter by
            type: Optional location type to filter by
            active_only: If True, only include active locations
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching Location instances
        """
        query = session.query(cls)
        
        # Apply filters based on provided parameters
        if name:
            query = query.filter(cls.name.ilike(f'%{name}%'))
        
        if code:
            query = query.filter(cls.code.ilike(code))
        
        if country:
            query = query.filter(cls.country.ilike(country))
        
        if type:
            query = query.filter(cls.type == type)
        
        if active_only:
            query = query.filter(cls.active == True)
        
        # Filter out soft-deleted locations
        query = query.filter(cls.is_deleted == False)
        
        # Apply limit and offset if provided
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        return query.all()
    
    @classmethod
    def get_by_code(cls, session: Session, code: str) -> Optional['Location']:
        """
        Class method to retrieve a location by its code.
        
        Args:
            session: SQLAlchemy session
            code: The location code to search for
            
        Returns:
            Location instance or None if not found
        """
        return session.query(cls).filter(
            cls.code.ilike(code),
            cls.is_deleted == False
        ).first()