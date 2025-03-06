"""
Alembic environment configuration script for database migrations in the Freight Price Movement Agent.

This file sets up the migration environment, connects to the database, and provides context
for running migrations. It integrates with SQLAlchemy models to generate and apply schema changes.
"""

import logging
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import SQLAlchemy metadata from models
from ..core.db import Base
from ..core.config import settings
from .. import models  # Import all models to ensure they are registered with SQLAlchemy

# Alembic Config object
config = context.config

# Set up logger
logger = logging.getLogger('alembic.env')

# Target metadata for autogenerate support
target_metadata = Base.metadata

# Use DATABASE_URL from settings if not set in alembic.ini
if config.get_main_option('sqlalchemy.url', None) is None:
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode, generating SQL scripts without connecting to the database.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode, connecting to the database and applying changes directly.
    
    In this scenario we need to create an Engine and associate a connection with the context.
    """
    # Get database URL from settings or config
    url = config.get_main_option("sqlalchemy.url")
    
    # Create SQLAlchemy engine with URL
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter function to determine which database objects should be included in migrations.
    
    Args:
        object: Database object (table, index, etc.)
        name: Name of the object
        type_: Type of the object
        reflected: Whether the object was reflected from the database
        compare_to: Object being compared against
        
    Returns:
        bool: True if object should be included, False otherwise
    """
    # Skip TimescaleDB internal tables
    if type_ == "table":
        if name.startswith('_timescaledb'):
            return False
    
    # Skip TimescaleDB-managed indexes
    if type_ == "index":
        if "timescaledb" in name.lower():
            return False
    
    # Include all other database objects
    return True


def process_revision_directives(context, revision, directives):
    """
    Process and modify revision directives before they are written to migration scripts.
    
    Args:
        context: Alembic migration context
        revision: Revision directive
        directives: List of directives
    """
    # Customize migration script generation if needed
    # For example, add comments or modify operations for TimescaleDB compatibility
    pass


# Entry point for running migrations
if context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()