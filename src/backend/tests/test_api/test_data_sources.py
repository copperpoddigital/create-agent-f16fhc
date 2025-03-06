import uuid
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.backend.models.enums import DataSourceType, DataSourceStatus  # Import DataSourceType and DataSourceStatus
from src.backend.tests.conftest import client, db_session, auth_headers, test_user  # Import fixtures

BASE_URL = "/api/v1/data-sources"


def test_get_data_sources(client: TestClient, auth_headers: dict):
    """Test retrieving a list of data sources"""
    # Send a GET request to the data sources endpoint with authentication headers
    response = client.get(BASE_URL, headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (items, total, page, size)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

    # Assert that items is a list
    assert isinstance(data["items"], list)


def test_create_csv_data_source(client: TestClient, auth_headers: dict):
    """Test creating a new CSV data source"""
    # Create test data for a CSV data source
    test_data = {
        "name": "Test CSV Data Source",
        "description": "A test CSV data source",
        "source_type": "CSV",
        "file_path": "/path/to/test.csv",
        "delimiter": ",",
        "encoding": "utf-8",
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
    }

    # Send a POST request to the CSV data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/csv", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data
    assert "filePath" in data
    assert "delimiter" in data
    assert "encoding" in data
    assert "fieldMapping" in data

    # Assert that the source_type is CSV
    assert data["sourceType"] == "CSV"

    # Assert that the name matches the test data
    assert data["name"] == test_data["name"]


def test_create_database_data_source(client: TestClient, auth_headers: dict):
    """Test creating a new database data source"""
    # Create test data for a database data source
    test_data = {
        "name": "Test Database Data Source",
        "description": "A test database data source",
        "source_type": "DATABASE",
        "connection_string": "postgresql://user:password@host:port/database",
        "query": "SELECT * FROM freight_data",
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
        "username": "testuser",
        "password": "testpassword",
    }

    # Send a POST request to the database data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/database", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data
    assert "connectionString" in data
    assert "query" in data
    assert "fieldMapping" in data
    assert "username" in data

    # Assert that the source_type is DATABASE
    assert data["sourceType"] == "DATABASE"

    # Assert that the name matches the test data
    assert data["name"] == test_data["name"]

    # Assert that the password field is not included in the response
    assert "password" not in data


def test_create_api_data_source(client: TestClient, auth_headers: dict):
    """Test creating a new API data source"""
    # Create test data for an API data source
    test_data = {
        "name": "Test API Data Source",
        "description": "A test API data source",
        "source_type": "API",
        "endpoint_url": "https://api.example.com/freight",
        "method": "GET",
        "headers": {"X-API-Key": "testkey"},
        "parameters": {"param1": "value1"},
        "auth_config": {"type": "api_key", "key": "apikey"},
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
    }

    # Send a POST request to the API data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/api", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data
    assert "endpointUrl" in data
    assert "method" in data
    assert "headers" in data
    assert "parameters" in data
    assert "authConfig" in data
    assert "fieldMapping" in data

    # Assert that the source_type is API
    assert data["sourceType"] == "API"

    # Assert that the name matches the test data
    assert data["name"] == test_data["name"]


def test_create_tms_data_source(client: TestClient, auth_headers: dict):
    """Test creating a new TMS data source"""
    # Create test data for a TMS data source
    test_data = {
        "name": "Test TMS Data Source",
        "description": "A test TMS data source",
        "source_type": "TMS",
        "tms_type": "SAP",
        "connection_string": "https://tms.example.com",
        "auth_config": {"type": "oauth2", "token_url": "https://auth.example.com"},
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
    }

    # Send a POST request to the TMS data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/tms", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data
    assert "tmsType" in data
    assert "connectionString" in data
    assert "authConfig" in data
    assert "fieldMapping" in data

    # Assert that the source_type is TMS
    assert data["sourceType"] == "TMS"

    # Assert that the name matches the test data
    assert data["name"] == test_data["name"]


def test_create_erp_data_source(client: TestClient, auth_headers: dict):
    """Test creating a new ERP data source"""
    # Create test data for an ERP data source
    test_data = {
        "name": "Test ERP Data Source",
        "description": "A test ERP data source",
        "source_type": "ERP",
        "erp_type": "SAP",
        "connection_string": "https://erp.example.com",
        "auth_config": {"type": "oauth2", "token_url": "https://auth.example.com"},
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
    }

    # Send a POST request to the ERP data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/erp", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data
    assert "erpType" in data
    assert "connectionString" in data
    assert "authConfig" in data
    assert "fieldMapping" in data

    # Assert that the source_type is ERP
    assert data["sourceType"] == "ERP"

    # Assert that the name matches the test data
    assert data["name"] == test_data["name"]


def test_get_data_source(client: TestClient, auth_headers: dict):
    """Test retrieving a specific data source by ID"""
    # Create a test data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Send a GET request to the data source endpoint with the data source ID and authentication headers
    response = client.get(f"{BASE_URL}/{data_source_id}", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (id, name, source_type, etc.)
    assert "id" in data
    assert "name" in data
    assert "sourceType" in data
    assert "description" in data
    assert "status" in data

    # Assert that the ID matches the created data source ID
    assert data["id"] == data_source_id


def test_update_data_source(client: TestClient, auth_headers: dict):
    """Test updating a data source"""
    # Create a test data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Create update data with a new name and description
    update_data = {"name": "Updated Data Source Name", "description": "Updated data source description"}

    # Send a PUT request to the data source endpoint with the data source ID, update data, and authentication headers
    response = client.put(f"{BASE_URL}/{data_source_id}", json=update_data, headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the updated name and description
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_update_csv_data_source(client: TestClient, auth_headers: dict):
    """Test updating a CSV data source"""
    # Create a test CSV data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Create update data with a new file path and delimiter
    update_data = {"file_path": "/path/to/new_file.csv", "delimiter": ";"}

    # Send a PUT request to the CSV data source endpoint with the data source ID, update data, and authentication headers
    response = client.put(f"{BASE_URL}/csv/{data_source_id}", json=update_data, headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the updated file path and delimiter
    assert data["filePath"] == update_data["file_path"]
    assert data["delimiter"] == update_data["delimiter"]


def test_delete_data_source(client: TestClient, auth_headers: dict):
    """Test deleting a data source"""
    # Create a test data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Send a DELETE request to the data source endpoint with the data source ID and authentication headers
    response = client.delete(f"{BASE_URL}/{data_source_id}", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains a success message
    assert "message" in data
    assert data["message"] == "Data source deleted successfully"

    # Send a GET request to verify the data source is no longer accessible
    response = client.get(f"{BASE_URL}/{data_source_id}", headers=auth_headers)

    # Assert that the GET response status code is 404 (Not Found)
    assert response.status_code == 404


def test_test_connection(client: TestClient, auth_headers: dict):
    """Test the connection testing functionality for a data source"""
    # Create a test data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Create test connection request data with the data source ID
    test_data = {"data_source_id": data_source_id}

    # Send a POST request to the test connection endpoint with the request data and authentication headers
    response = client.post(f"{BASE_URL}/test-connection", json=test_data, headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (success, message, details)
    assert "success" in data
    assert "message" in data
    assert "details" in data


def test_activate_data_source(client: TestClient, auth_headers: dict):
    """Test activating a data source"""
    # Create a test data source with inactive status
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Send a POST request to the activate endpoint with the data source ID and authentication headers
    response = client.post(f"{BASE_URL}/{data_source_id}/activate", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response status field is ACTIVE
    assert data["status"] == "ACTIVE"


def test_deactivate_data_source(client: TestClient, auth_headers: dict):
    """Test deactivating a data source"""
    # Create a test data source with active status
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Send a POST request to the deactivate endpoint with the data source ID and authentication headers
    response = client.post(f"{BASE_URL}/{data_source_id}/deactivate", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response status field is INACTIVE
    assert data["status"] == "INACTIVE"


def test_get_data_source_logs(client: TestClient, auth_headers: dict):
    """Test retrieving logs for a data source"""
    # Create a test data source
    csv_data_source = create_test_csv_data_source(client, auth_headers)
    data_source_id = csv_data_source["id"]

    # Perform some operations on the data source to generate logs
    # (e.g., test connection, activate, deactivate)

    # Send a GET request to the logs endpoint with the data source ID and authentication headers
    response = client.get(f"{BASE_URL}/{data_source_id}/logs", headers=auth_headers)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Parse the response JSON
    data = response.json()

    # Assert that the response contains the expected fields (items, total, page, size)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

    # Assert that items is a list of log entries
    assert isinstance(data["items"], list)


def test_unauthorized_access(client: TestClient):
    """Test that unauthorized access is properly rejected"""
    # Send a GET request to the data sources endpoint without authentication headers
    response = client.get(BASE_URL)

    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401


def create_test_csv_data_source(client: TestClient, auth_headers: dict) -> dict:
    """Helper function to create a test CSV data source"""
    # Create test data for a CSV data source
    test_data = {
        "name": "Test CSV Data Source",
        "description": "A test CSV data source",
        "source_type": "CSV",
        "file_path": "/path/to/test.csv",
        "delimiter": ",",
        "encoding": "utf-8",
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
    }

    # Send a POST request to the CSV data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/csv", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse and return the response JSON
    return response.json()


def create_test_database_data_source(client: TestClient, auth_headers: dict) -> dict:
    """Helper function to create a test database data source"""
    # Create test data for a database data source
    test_data = {
        "name": "Test Database Data Source",
        "description": "A test database data source",
        "source_type": "DATABASE",
        "connection_string": "postgresql://user:password@host:port/database",
        "query": "SELECT * FROM freight_data",
        "field_mapping": {"freight_charge": "price", "currency": "currency_code", "origin": "origin", "destination": "destination", "date/time": "quote_date"},
        "username": "testuser",
        "password": "testpassword",
    }

    # Send a POST request to the database data source endpoint with the test data and authentication headers
    response = client.post(f"{BASE_URL}/database", json=test_data, headers=auth_headers)

    # Assert that the response status code is 201 (Created)
    assert response.status_code == 201

    # Parse and return the response JSON
    return response.json()