# Import the application factory function from app.py
from .app import create_app  # Import the application factory function to create the FastAPI application

# Import FastAPI for type annotation
from fastapi import FastAPI  # Type annotation for the application instance


# Create the FastAPI application instance
app = create_app()


# Expose the FastAPI application instance for WSGI servers
application = app  # Alternative name for the application instance, commonly used by some WSGI servers