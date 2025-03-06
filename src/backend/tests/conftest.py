import pytest # version ^7.0.0
from fastapi.testclient import TestClient # version ^0.95.0
from sqlalchemy import create_engine # version ^1.4.40
from sqlalchemy.orm import sessionmaker # version ^1.4.40
from sqlalchemy.ext.declarative import declarative_base # version ^1.4.40
from datetime import datetime
import uuid
from decimal import Decimal
from typing import Generator, Callable
import os
import random

from ..app import create_app, get_db # src/backend/app.py
from ..core.db import Base # src/backend/core/db.py
from ..models.user import User # src/backend/models/user.py
from ..models.freight_data import FreightData # src/backend/models/freight_data.py
from ..models.location import Location # src/backend/models/location.py
from ..models.carrier import Carrier # src/backend/models/carrier.py
from ..models.route import Route # src/backend/models/route.py
from ..models.time_period import TimePeriod # src/backend/models/time_period.py
from ..models.analysis_result import AnalysisResult # src/backend/models/analysis_result.py
from ..models.enums import GranularityType, TransportMode, AnalysisStatus, TrendDirection, OutputFormat # src/backend/models/enums.py
from ..core.security import create_access_token # src/backend/core/security.py
from ..core.cache import initialize_cache # src/backend/core/cache.py

def pytest_configure(config: pytest.Config) -> None:
    """Pytest hook to configure the test environment"""
    # Set up environment variables for testing
    os.environ['TESTING'] = 'True'

    # Configure pytest markers
    config.addinivalue_line("markers", "integration: mark test as integration test.")
    config.addinivalue_line("markers", "unit: mark test as unit test.")
    config.addinivalue_line("markers", "api: mark test as api test.")

    # Set up any global test configuration
    # For example, configure logging, database connections, etc.
    pass

@pytest.fixture(scope="session")
def app() -> Generator:
    """Fixture that provides a FastAPI application instance for testing"""
    # Create a FastAPI application using create_app()
    app = create_app()

    # Configure the application for testing
    # For example, override database settings, etc.
    app.dependency_overrides[get_db] = lambda: None  # Override get_db dependency

    # Return the application instance
    yield app

@pytest.fixture(scope="function")
def client(app: "fastapi.FastAPI") -> "fastapi.testclient.TestClient":
    """Fixture that provides a TestClient for making requests to the FastAPI application"""
    # Create a TestClient instance with the app fixture
    client = TestClient(app)

    # Return the TestClient instance
    yield client

@pytest.fixture(scope="session")
def engine() -> "sqlalchemy.engine.Engine":
    """Fixture that provides a SQLAlchemy engine for the test database"""
    # Create an in-memory SQLite database engine
    engine = create_engine("sqlite:///:memory:")

    # Return the engine instance
    yield engine

@pytest.fixture(scope="session")
def tables(engine: "sqlalchemy.engine.Engine") -> None:
    """Fixture that creates all database tables for testing"""
    # Create all tables defined in Base.metadata
    Base.metadata.create_all(engine)

    # Yield to allow tests to run
    yield

    # Drop all tables after tests complete
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine: "sqlalchemy.engine.Engine", tables) -> "sqlalchemy.orm.Session":
    """Fixture that provides a SQLAlchemy session for database operations"""
    # Create a new SQLAlchemy session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Begin a transaction
    connection = engine.connect()
    transaction = connection.begin()
    db = SessionLocal(bind=connection)

    # Yield the session to the test
    yield db

    # Rollback the transaction after the test
    db.rollback()
    connection.close()

@pytest.fixture(scope="function")
def override_get_db(db_session: "sqlalchemy.orm.Session") -> "typing.Generator[sqlalchemy.orm.Session, None, None]":
    """Fixture that overrides the get_db dependency to use the test database"""
    # Define a function that yields the test db_session
    def _override_get_db():
        yield db_session

    # Return the function
    return _override_get_db

@pytest.fixture(scope="function")
def app_with_db(app: "fastapi.FastAPI", override_get_db: "typing.Callable") -> "fastapi.FastAPI":
    """Fixture that provides a FastAPI application with the test database"""
    # Override the get_db dependency in the app with override_get_db
    app.dependency_overrides[get_db] = override_get_db

    # Return the app with the overridden dependency
    yield app

@pytest.fixture(scope="function")
def client_with_db(app_with_db: "fastapi.FastAPI") -> "fastapi.testclient.TestClient":
    """Fixture that provides a TestClient with the test database"""
    # Create a TestClient instance with the app_with_db fixture
    client = TestClient(app_with_db)

    # Return the TestClient instance
    yield client

@pytest.fixture(scope="function")
def test_user(db_session: "sqlalchemy.orm.Session") -> "User":
    """Fixture that creates a test user for authentication tests"""
    # Create a test user with username, email, and password
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Set the user's password using set_password
    user.set_password("testpassword")

    # Add the user to the database session
    db_session.add(user)

    # Commit the session
    db_session.commit()

    # Return the user instance
    yield user

@pytest.fixture(scope="function")
def auth_headers(test_user: "User") -> dict:
    """Fixture that provides authentication headers for authenticated requests"""
    # Create an access token for the test user
    access_token = create_access_token(data={"sub": str(test_user.id)})

    # Return headers with the Authorization header set to 'Bearer {token}'
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def test_locations(db_session: "sqlalchemy.orm.Session") -> "list[Location]":
    """Fixture that creates test locations for freight data"""
    # Create multiple test locations with different names, codes, and countries
    location1 = Location(name="New York", code="NYC", country="US", type=TransportMode.AIR)
    location2 = Location(name="London", code="LON", country="GB", type=TransportMode.OCEAN)
    location3 = Location(name="Tokyo", code="TYO", country="JP", type=TransportMode.RAIL)

    # Add the locations to the database session
    db_session.add_all([location1, location2, location3])

    # Commit the session
    db_session.commit()

    # Return the list of location instances
    yield [location1, location2, location3]

@pytest.fixture(scope="function")
def test_carriers(db_session: "sqlalchemy.orm.Session") -> "list[Carrier]":
    """Fixture that creates test carriers for freight data"""
    # Create multiple test carriers with different names and codes
    carrier1 = Carrier(name="United Airlines", code="UA", type=TransportMode.AIR)
    carrier2 = Carrier(name="Maersk", code="MSK", type=TransportMode.OCEAN)
    carrier3 = Carrier(name="Union Pacific", code="UP", type=TransportMode.RAIL)

    # Add the carriers to the database session
    db_session.add_all([carrier1, carrier2, carrier3])

    # Commit the session
    db_session.commit()

    # Return the list of carrier instances
    yield [carrier1, carrier2, carrier3]

@pytest.fixture(scope="function")
def test_routes(db_session: "sqlalchemy.orm.Session", test_locations: "list[Location]") -> "list[Route]":
    """Fixture that creates test routes for freight data"""
    # Extract locations from test_locations fixture
    location1, location2, location3 = test_locations

    # Create multiple test routes with different origin-destination pairs
    route1 = Route(origin_id=location1.id, destination_id=location2.id, transport_mode=TransportMode.AIR)
    route2 = Route(origin_id=location2.id, destination_id=location3.id, transport_mode=TransportMode.OCEAN)
    route3 = Route(origin_id=location3.id, destination_id=location1.id, transport_mode=TransportMode.RAIL)

    # Add the routes to the database session
    db_session.add_all([route1, route2, route3])

    # Commit the session
    db_session.commit()

    # Return the list of route instances
    yield [route1, route2, route3]

@pytest.fixture(scope="function")
def test_freight_data(db_session: "sqlalchemy.orm.Session", test_locations: "list[Location]", test_carriers: "list[Carrier]") -> "list[FreightData]":
    """Fixture that creates test freight data for analysis"""
    # Extract locations and carriers from fixtures
    location1, location2, location3 = test_locations
    carrier1, carrier2, carrier3 = test_carriers

    # Create multiple test freight data records with different dates, origins, destinations, carriers, and prices
    freight_data1 = FreightData(record_date=datetime(2023, 1, 15), origin_id=location1.id, destination_id=location2.id, carrier_id=carrier1.id, freight_charge=1500.00, transport_mode=TransportMode.AIR)
    freight_data2 = FreightData(record_date=datetime(2023, 2, 20), origin_id=location2.id, destination_id=location3.id, carrier_id=carrier2.id, freight_charge=2200.50, transport_mode=TransportMode.OCEAN)
    freight_data3 = FreightData(record_date=datetime(2023, 3, 10), origin_id=location3.id, destination_id=location1.id, carrier_id=carrier3.id, freight_charge=800.75, transport_mode=TransportMode.RAIL)

    # Add the freight data to the database session
    db_session.add_all([freight_data1, freight_data2, freight_data3])

    # Commit the session
    db_session.commit()

    # Return the list of freight data instances
    yield [freight_data1, freight_data2, freight_data3]

@pytest.fixture(scope="function")
def test_time_period(db_session: "sqlalchemy.orm.Session") -> "TimePeriod":
    """Fixture that creates a test time period for analysis"""
    # Create a test time period with start date, end date, and granularity
    time_period = TimePeriod(name="Test Period", start_date=datetime(2023, 1, 1), end_date=datetime(2023, 3, 31), granularity=GranularityType.MONTHLY)

    # Add the time period to the database session
    db_session.add(time_period)

    # Commit the session
    db_session.commit()

    # Return the time period instance
    yield time_period

@pytest.fixture(scope="function")
def test_analysis_result(db_session: "sqlalchemy.orm.Session", test_time_period: "TimePeriod", test_user: "User") -> "AnalysisResult":
    """Fixture that creates a test analysis result"""
    # Create a test analysis result with time period, parameters, and status
    analysis_result = AnalysisResult(time_period_id=test_time_period.id, parameters={"test": "value"}, created_by=test_user.id)

    # Add the analysis result to the database session
    db_session.add(analysis_result)

    # Commit the session
    db_session.commit()

    # Return the analysis result instance
    yield analysis_result

@pytest.fixture(scope="function")
def mock_cache() -> dict:
    """Fixture that provides a mock cache for testing"""
    # Create a dictionary to serve as a mock cache
    cache = {}

    # Return the mock cache dictionary
    yield cache

def generate_freight_data(db_session: "sqlalchemy.orm.Session", locations: "list[Location]", carriers: "list[Carrier]", start_date: datetime, end_date: datetime, num_records: int, transport_mode: TransportMode, base_price: float, price_trend_factor: float) -> "list[FreightData]":
    """Helper function to generate freight data for a specific time period"""
    # Calculate date range between start_date and end_date
    date_range = end_date - start_date

    # Generate num_records freight data instances with dates within the range
    freight_data = []
    for i in range(num_records):
        random_date = start_date + date_range * random.random()
        origin = random.choice(locations)
        destination = random.choice(locations)
        carrier = random.choice(carriers)
        price = base_price + (i * price_trend_factor)
        freight_data_record = FreightData(
            record_date=random_date,
            origin_id=origin.id,
            destination_id=destination.id,
            carrier_id=carrier.id,
            freight_charge=price,
            transport_mode=transport_mode
        )
        freight_data.append(freight_data_record)

    # Add the freight data to the database session
    db_session.add_all(freight_data)

    # Commit the session
    db_session.commit()

    # Return the list of freight data instances
    return freight_data