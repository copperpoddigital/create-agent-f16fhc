import pytest  # version ^7.0.0
from datetime import datetime  # version: standard library
from decimal import Decimal  # version: standard library
from uuid import uuid4  # version: standard library
from sqlalchemy.exc import IntegrityError  # version ^1.4.40

from src.backend.models.freight_data import FreightData  # Import the FreightData model for testing
from src.backend.models.enums import TransportMode  # Import transport mode enumeration for testing
from src.backend.tests.conftest import db_session, test_freight_data  # Import database session fixture for testing


def test_freight_data_init():
    """Tests the initialization of a FreightData instance with valid parameters"""
    # Create a new FreightData instance with valid test data
    freight_data = FreightData(
        record_date=datetime.now(),
        origin_id=str(uuid4()),
        destination_id=str(uuid4()),
        carrier_id=str(uuid4()),
        freight_charge=1500.00,
        transport_mode=TransportMode.AIR
    )

    # Assert that all attributes are set correctly
    assert freight_data.record_date is not None
    assert freight_data.origin_id is not None
    assert freight_data.destination_id is not None
    assert freight_data.carrier_id is not None
    assert freight_data.freight_charge == Decimal('1500.00')
    assert freight_data.transport_mode == TransportMode.AIR

    # Assert that default values are applied where not specified
    assert freight_data.currency_code == 'USD'
    assert freight_data.service_level is None


def test_freight_data_required_fields(db_session):
    """Tests that required fields cannot be null"""
    # Create a FreightData instance with missing required fields
    freight_data = FreightData(
        record_date=datetime.now(),
        origin_id=str(uuid4()),
        destination_id=str(uuid4()),
        carrier_id=str(uuid4()),
        freight_charge=1500.00,
        transport_mode=TransportMode.AIR
    )
    freight_data.origin_id = None

    # Attempt to add to session and commit
    db_session.add(freight_data)
    with pytest.raises(IntegrityError):
        db_session.commit()

    # Rollback the session
    db_session.rollback()


def test_freight_data_defaults():
    """Tests that default values are applied correctly"""
    # Create a FreightData instance without specifying fields that have defaults
    freight_data = FreightData(
        record_date=datetime.now(),
        origin_id=str(uuid4()),
        destination_id=str(uuid4()),
        carrier_id=str(uuid4()),
        freight_charge=1500.00,
        transport_mode=TransportMode.AIR
    )

    # Assert that currency_code defaults to 'USD'
    assert freight_data.currency_code == 'USD'

    # Assert that is_deleted defaults to False
    assert freight_data.is_deleted is False

    # Assert that created_at and updated_at are set to current time
    assert freight_data.created_at is not None
    assert freight_data.updated_at is not None


def test_freight_data_relationships(db_session, test_freight_data):
    """Tests the relationships between FreightData and related models"""
    # Get a FreightData instance from the test_freight_data fixture
    freight_data = test_freight_data[0]

    # Assert that origin relationship returns a Location instance
    assert freight_data.origin is not None

    # Assert that destination relationship returns a Location instance
    assert freight_data.destination is not None

    # Assert that carrier relationship returns a Carrier instance
    assert freight_data.carrier is not None


def test_freight_data_to_dict(test_freight_data):
    """Tests the to_dict method of FreightData"""
    # Get a FreightData instance from the test_freight_data fixture
    freight_data = test_freight_data[0]

    # Call the to_dict method
    freight_data_dict = freight_data.to_dict()

    # Assert that the returned dictionary contains all expected keys
    expected_keys = ['id', 'record_date', 'origin_id', 'destination_id', 'carrier_id', 'freight_charge',
                     'currency_code', 'transport_mode', 'service_level', 'additional_charges', 'source_system',
                     'data_quality_flag', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']
    assert all(key in freight_data_dict for key in expected_keys)

    # Assert that the values match the instance attributes
    assert str(freight_data.id) == freight_data_dict['id']
    assert freight_data.origin_id == freight_data_dict['origin_id']
    assert freight_data.destination_id == freight_data_dict['destination_id']
    assert freight_data.carrier_id == freight_data_dict['carrier_id']
    assert float(freight_data.freight_charge) == freight_data_dict['freight_charge']
    assert freight_data.currency_code == freight_data_dict['currency_code']

    # Assert that transport_mode is converted to string
    assert freight_data.transport_mode.name == freight_data_dict['transport_mode']

    # Assert that dates are formatted as ISO strings
    assert freight_data.record_date.isoformat() == freight_data_dict['record_date']
    assert freight_data.created_at.isoformat() == freight_data_dict['created_at']
    assert freight_data.updated_at.isoformat() == freight_data_dict['updated_at']


def test_freight_data_search(db_session, test_freight_data):
    """Tests the search class method of FreightData"""
    # Create test data with known attributes
    record_date = datetime(2023, 1, 15)
    origin_id = test_freight_data[0].origin_id
    destination_id = test_freight_data[0].destination_id
    carrier_id = test_freight_data[0].carrier_id
    transport_mode = test_freight_data[0].transport_mode

    # Test search with start_date filter
    search_results = FreightData.search(db_session, start_date=record_date)
    assert len(search_results) == 3

    # Test search with end_date filter
    search_results = FreightData.search(db_session, end_date=record_date)
    assert len(search_results) == 3

    # Test search with origin_id filter
    search_results = FreightData.search(db_session, origin_id=origin_id)
    assert len(search_results) == 1

    # Test search with destination_id filter
    search_results = FreightData.search(db_session, destination_id=destination_id)
    assert len(search_results) == 1

    # Test search with carrier_id filter
    search_results = FreightData.search(db_session, carrier_id=carrier_id)
    assert len(search_results) == 1

    # Test search with transport_mode filter
    search_results = FreightData.search(db_session, transport_mode=transport_mode)
    assert len(search_results) == 1

    # Test search with multiple filters
    search_results = FreightData.search(db_session, start_date=record_date, origin_id=origin_id,
                                         transport_mode=transport_mode)
    assert len(search_results) == 1

    # Test search with limit and offset
    search_results = FreightData.search(db_session, limit=1, offset=1)
    assert len(search_results) == 1

    # Assert that search results match expected records
    assert search_results[0].record_date == test_freight_data[1].record_date


def test_freight_data_get_for_analysis(db_session, test_freight_data):
    """Tests the get_for_analysis class method of FreightData"""
    # Define start and end dates for analysis
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 3, 31)

    # Call get_for_analysis with date range
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date)
    assert len(analysis_results) == 3

    # Assert that returned records are within the date range
    for result in analysis_results:
        assert start_date <= result.record_date <= end_date

    # Test with origin_ids filter
    origin_ids = [test_freight_data[0].origin_id]
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date,
                                                     origin_ids=origin_ids)
    assert len(analysis_results) == 1

    # Test with destination_ids filter
    destination_ids = [test_freight_data[1].destination_id]
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date,
                                                        destination_ids=destination_ids)
    assert len(analysis_results) == 1

    # Test with carrier_ids filter
    carrier_ids = [test_freight_data[2].carrier_id]
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date,
                                                     carrier_ids=carrier_ids)
    assert len(analysis_results) == 1

    # Test with transport_modes filter
    transport_modes = [test_freight_data[0].transport_mode]
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date,
                                                     transport_modes=transport_modes)
    assert len(analysis_results) == 1

    # Test with multiple filters
    analysis_results = FreightData.get_for_analysis(db_session, start_date=start_date, end_date=end_date,
                                                     origin_ids=origin_ids, transport_modes=transport_modes)
    assert len(analysis_results) == 1

    # Assert that results are ordered by record_date
    assert analysis_results[0].record_date == test_freight_data[0].record_date


@pytest.mark.skipif(os.environ.get("SKIP_TIMESCALEDB_TESTS", "true").lower() == "true",
                    reason="TimescaleDB tests are skipped by default")
def test_freight_data_setup_timescaledb():
    """Tests the setup_timescaledb_hypertable class method"""
    # Create a mock engine
    class MockEngine:
        def execute(self, sql):
            self.executed_sql = sql

    engine = MockEngine()

    # Call setup_timescaledb_hypertable with the mock engine
    FreightData.setup_timescaledb_hypertable(engine)

    # Assert that the engine's execute method was called with the expected SQL
    assert "create_hypertable" in str(engine.executed_sql)
    assert "record_date" in str(engine.executed_sql)

    # Test with custom chunk_time_interval
    FreightData.setup_timescaledb_hypertable(engine, chunk_time_interval=30)
    assert "INTERVAL '30 days'" in str(engine.executed_sql)


def test_freight_data_soft_delete(db_session, test_freight_data):
    """Tests the soft delete functionality of FreightData"""
    # Get a FreightData instance from the test_freight_data fixture
    freight_data = test_freight_data[0]

    # Call the delete method
    freight_data.delete()
    db_session.commit()

    # Assert that is_deleted is True
    assert freight_data.is_deleted is True

    # Assert that deleted_at is set
    assert freight_data.deleted_at is not None

    # Call the restore method
    freight_data.restore()
    db_session.commit()

    # Assert that is_deleted is False
    assert freight_data.is_deleted is False

    # Assert that deleted_at is None
    assert freight_data.deleted_at is None


def test_freight_data_audit_logging(db_session):
    """Tests the audit logging functionality of FreightData"""
    # Create a new FreightData instance
    freight_data = FreightData(
        record_date=datetime.now(),
        origin_id=str(uuid4()),
        destination_id=str(uuid4()),
        carrier_id=str(uuid4()),
        freight_charge=1500.00,
        transport_mode=TransportMode.AIR
    )

    # Call log_create method
    freight_data.log_create(db_session)
    db_session.commit()

    # Assert that an audit log entry is created with CREATE action
    from src.backend.models.audit_log import AuditLog
    audit_entry = db_session.query(AuditLog).filter(AuditLog.resource_id == freight_data.id).first()
    assert audit_entry is not None
    assert audit_entry.action.name == "CREATE"

    # Update the instance
    freight_data.freight_charge = 2000.00

    # Call log_update method with changes
    freight_data.log_update(db_session, changes={"freight_charge": "2000.00"})
    db_session.commit()

    # Assert that an audit log entry is created with UPDATE action
    audit_entry = db_session.query(AuditLog).filter(AuditLog.resource_id == freight_data.id,
                                                    AuditLog.action.name == "UPDATE").first()
    assert audit_entry is not None
    assert audit_entry.details["changes"] == {"freight_charge": "2000.00"}

    # Call delete method
    freight_data.delete()
    db_session.commit()

    # Call log_delete method
    freight_data.log_delete(db_session)
    db_session.commit()

    # Assert that an audit log entry is created with DELETE action
    audit_entry = db_session.query(AuditLog).filter(AuditLog.resource_id == freight_data.id,
                                                    AuditLog.action.name == "DELETE").first()
    assert audit_entry is not None