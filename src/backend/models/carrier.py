"""
Defines the Carrier SQLAlchemy model for the Freight Price Movement Agent application.

This model represents freight carriers and their attributes, providing a reference
entity for freight pricing data analysis.
"""

import typing

import sqlalchemy
from sqlalchemy.orm import relationship

from ..core.db import Base
from .enums import CarrierType
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Carrier(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    SQLAlchemy model representing a freight carrier in the system.
    """
    __tablename__ = 'carriers'
    
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, index=True)
    code = sqlalchemy.Column(sqlalchemy.String(50), nullable=True, unique=True, index=True)
    type = sqlalchemy.Column(sqlalchemy.Enum(CarrierType), nullable=False, index=True)
    active = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)
    
    # Relationships
    freight_data = relationship('FreightData', back_populates='carrier', cascade='all, delete-orphan')
    
    def __init__(self, name: str, type: CarrierType, code: typing.Optional[str] = None, active: bool = True):
        """
        Initializes a new Carrier instance.
        
        Args:
            name: Carrier name
            type: Carrier type (from CarrierType enum)
            code: Optional carrier code (unique identifier)
            active: Whether the carrier is active (default: True)
        """
        self.name = name
        self.type = type
        self.code = code
        self.active = active
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Carrier.
        
        Returns:
            String representation
        """
        return f"<Carrier(name='{self.name}', code='{self.code}', type='{self.type}')>"
    
    def to_dict(self) -> dict:
        """
        Converts the Carrier model to a dictionary.
        
        Returns:
            Dictionary representation of the carrier
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type.name if self.type else None,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }