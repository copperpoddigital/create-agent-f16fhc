import pytest
import json
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from ...models.enums import (
    GranularityType, 
    OutputFormat, 
    AnalysisStatus,
    TrendDirection
)


def test_create_time_period(client: TestClient, auth_headers: dict):
    """Tests the creation of a new time period via the API"""
    # Prepare test data
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30)
    
    payload = {
        "name": "Test Time Period",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "granularity": GranularityType.WEEKLY.name
    }
    
    # Make API request
    response = client.post(
        "/api/analysis/time-periods",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the created time period
    assert "id" in data, "Response should contain time period ID"
    assert uuid.UUID(data["id"]), "ID should be a valid UUID"
    assert data["name"] == payload["name"], "Time period name doesn't match"
    assert data["start_date"] == payload["start_date"], "Start date doesn't match"
    assert data["end_date"] == payload["end_date"], "End date doesn't match"
    assert data["granularity"] == payload["granularity"], "Granularity doesn't match"


def test_get_time_period(client: TestClient, auth_headers: dict, db_session):
    """Tests retrieving a time period by ID via the API"""
    # Create a test time period in the database
    time_period = create_test_time_period(db_session)
    
    # Make API request
    response = client.get(
        f"/api/analysis/time-periods/{time_period.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the retrieved time period
    assert data["id"] == str(time_period.id), "Time period ID doesn't match"
    assert data["name"] == time_period.name, "Time period name doesn't match"
    assert data["start_date"] == time_period.start_date.isoformat(), "Start date doesn't match"
    assert data["end_date"] == time_period.end_date.isoformat(), "End date doesn't match"
    assert data["granularity"] == time_period.granularity.name, "Granularity doesn't match"


def test_list_time_periods(client: TestClient, auth_headers: dict, db_session):
    """Tests listing time periods with pagination via the API"""
    # Create multiple test time periods in the database
    time_periods = [
        create_test_time_period(db_session, name=f"Test Period {i}")
        for i in range(5)
    ]
    
    # Make API request with pagination
    response = client.get(
        "/api/analysis/time-periods?page=1&page_size=3",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate pagination and data
    assert "items" in data, "Response should contain items array"
    assert "total" in data, "Response should contain total count"
    assert "page" in data, "Response should contain page number"
    assert "page_size" in data, "Response should contain page size"
    
    assert data["page"] == 1, "Page number should be 1"
    assert data["page_size"] == 3, "Page size should be 3"
    assert len(data["items"]) <= 3, "Items should not exceed page size"
    assert data["total"] >= 5, "Total count should include all created time periods"
    
    # Test filtering
    # Make API request with filtering
    response = client.get(
        f"/api/analysis/time-periods?name={time_periods[0].name}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate filtering
    assert data["total"] >= 1, "Filtered results should include at least one item"
    assert any(item["name"] == time_periods[0].name for item in data["items"]), "Filtered results should include the requested item"


def test_update_time_period(client: TestClient, auth_headers: dict, db_session):
    """Tests updating an existing time period via the API"""
    # Create a test time period in the database
    time_period = create_test_time_period(db_session)
    
    # Prepare update data
    updated_name = "Updated Time Period"
    updated_start_date = (time_period.start_date + timedelta(days=1)).isoformat()
    updated_end_date = (time_period.end_date + timedelta(days=1)).isoformat()
    updated_granularity = GranularityType.MONTHLY.name
    
    payload = {
        "name": updated_name,
        "start_date": updated_start_date,
        "end_date": updated_end_date,
        "granularity": updated_granularity
    }
    
    # Make API request
    response = client.put(
        f"/api/analysis/time-periods/{time_period.id}",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the updated time period
    assert data["id"] == str(time_period.id), "Time period ID should not change"
    assert data["name"] == updated_name, "Time period name doesn't match update"
    assert data["start_date"] == updated_start_date, "Start date doesn't match update"
    assert data["end_date"] == updated_end_date, "End date doesn't match update"
    assert data["granularity"] == updated_granularity, "Granularity doesn't match update"


def test_delete_time_period(client: TestClient, auth_headers: dict, db_session):
    """Tests deleting a time period via the API"""
    # Create a test time period in the database
    time_period = create_test_time_period(db_session)
    
    # Make API request
    response = client.delete(
        f"/api/analysis/time-periods/{time_period.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the deletion response
    assert data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify time period no longer exists
    get_response = client.get(
        f"/api/analysis/time-periods/{time_period.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404, "Time period should no longer exist"


def test_create_analysis_request(client: TestClient, auth_headers: dict, db_session):
    """Tests creating a new analysis request via the API"""
    # Create a test time period in the database
    time_period = create_test_time_period(db_session)
    
    # Prepare analysis request data
    payload = {
        "time_period_id": str(time_period.id),
        "parameters": {
            "data_source_ids": ["00000000-0000-0000-0000-000000000001"],
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "calculate_absolute_change": True,
            "calculate_percentage_change": True,
            "identify_trend": True
        },
        "output_format": OutputFormat.JSON.name
    }
    
    # Make API request
    response = client.post(
        "/api/analysis/requests",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the created analysis request
    assert "id" in data, "Response should contain analysis ID"
    assert uuid.UUID(data["id"]), "ID should be a valid UUID"
    assert data["time_period_id"] == payload["time_period_id"], "Time period ID doesn't match"
    assert data["parameters"] == payload["parameters"], "Parameters don't match"
    assert data["status"] == AnalysisStatus.PENDING.name, "Analysis status should be PENDING"


def test_get_analysis_request(client: TestClient, auth_headers: dict, db_session):
    """Tests retrieving an analysis request by ID via the API"""
    # Create a test time period and analysis request in the database
    time_period = create_test_time_period(db_session)
    analysis = create_test_analysis_request(db_session, time_period_id=time_period.id)
    
    # Make API request
    response = client.get(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the retrieved analysis request
    assert data["id"] == str(analysis.id), "Analysis ID doesn't match"
    assert data["time_period_id"] == str(analysis.time_period_id), "Time period ID doesn't match"
    assert data["status"] == analysis.status.name, "Analysis status doesn't match"


def test_list_analysis_requests(client: TestClient, auth_headers: dict, db_session):
    """Tests listing analysis requests with pagination via the API"""
    # Create a test time period
    time_period = create_test_time_period(db_session)
    
    # Create multiple test analysis requests in the database
    analyses = [
        create_test_analysis_request(db_session, time_period_id=time_period.id, status=status)
        for status in [AnalysisStatus.PENDING, AnalysisStatus.PROCESSING, AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]
    ]
    
    # Make API request with pagination
    response = client.get(
        "/api/analysis/requests?page=1&page_size=2",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate pagination and data
    assert "items" in data, "Response should contain items array"
    assert "total" in data, "Response should contain total count"
    assert len(data["items"]) <= 2, "Items should not exceed page size"
    assert data["total"] >= 4, "Total count should include all created analysis requests"
    
    # Test filtering by status
    response = client.get(
        f"/api/analysis/requests?status={AnalysisStatus.COMPLETED.name}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate filtering
    assert all(item["status"] == AnalysisStatus.COMPLETED.name for item in data["items"]), "Filtered results should all have COMPLETED status"


def test_delete_analysis_request(client: TestClient, auth_headers: dict, db_session):
    """Tests deleting an analysis request via the API"""
    # Create a test time period and analysis request in the database
    time_period = create_test_time_period(db_session)
    analysis = create_test_analysis_request(db_session, time_period_id=time_period.id)
    
    # Make API request
    response = client.delete(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the deletion response
    assert data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify analysis request no longer exists
    get_response = client.get(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404, "Analysis request should no longer exist"


def test_execute_analysis(client: TestClient, auth_headers: dict, db_session, test_freight_data):
    """Tests executing a price movement analysis via the API"""
    # Create a test time period in the database
    start_date = datetime.now().date() - timedelta(days=30)
    end_date = datetime.now().date()
    time_period = create_test_time_period(
        db_session, 
        start_date=start_date,
        end_date=end_date,
        granularity=GranularityType.WEEKLY
    )
    
    # Create a test analysis request
    analysis = create_test_analysis_request(
        db_session, 
        time_period_id=time_period.id,
        parameters={
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "calculate_absolute_change": True,
            "calculate_percentage_change": True,
            "identify_trend": True
        }
    )
    
    # Make API request to execute the analysis
    response = client.post(
        f"/api/analysis/requests/{analysis.id}/execute",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the analysis results
    assert "results" in data, "Response should contain analysis results"
    assert "absolute_change" in data["results"], "Results should include absolute_change"
    assert "percentage_change" in data["results"], "Results should include percentage_change"
    assert "trend_direction" in data["results"], "Results should include trend_direction"
    
    # Verify the analysis request status has been updated
    status_response = client.get(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    status_data = status_response.json()
    
    assert status_data["status"] == AnalysisStatus.COMPLETED.name, "Analysis status should be updated to COMPLETED"


def test_get_analysis_result(client: TestClient, auth_headers: dict, db_session, test_freight_data):
    """Tests retrieving analysis results via the API"""
    # Create a test time period and analysis request
    time_period = create_test_time_period(db_session)
    analysis = create_test_analysis_request(db_session, time_period_id=time_period.id)
    
    # Execute the analysis (we'd normally call the endpoint, but for testing we can directly set results)
    update_analysis_with_results(
        db_session, 
        analysis.id, 
        {
            "absolute_change": 125.50,
            "percentage_change": 2.5,
            "trend_direction": TrendDirection.INCREASING.name,
            "start_value": 5000.00,
            "end_value": 5125.50
        }
    )
    
    # Make API request for results in JSON format
    json_response = client.get(
        f"/api/analysis/requests/{analysis.id}/results?format={OutputFormat.JSON.name}",
        headers=auth_headers
    )
    
    # Verify JSON response
    assert json_response.status_code == 200, f"Expected 200 OK, got {json_response.status_code}: {json_response.text}"
    assert json_response.headers["Content-Type"] == "application/json", "Response should have JSON content type"
    
    json_data = json_response.json()
    assert "absolute_change" in json_data, "JSON results should include absolute_change"
    
    # Make API request for results in CSV format
    csv_response = client.get(
        f"/api/analysis/requests/{analysis.id}/results?format={OutputFormat.CSV.name}",
        headers=auth_headers
    )
    
    # Verify CSV response
    assert csv_response.status_code == 200, f"Expected 200 OK, got {csv_response.status_code}"
    assert csv_response.headers["Content-Type"] == "text/csv", "Response should have CSV content type"
    assert "absolute_change" in csv_response.text, "CSV results should include absolute_change"
    
    # Make API request for results in TEXT format
    text_response = client.get(
        f"/api/analysis/requests/{analysis.id}/results?format={OutputFormat.TEXT.name}",
        headers=auth_headers
    )
    
    # Verify TEXT response
    assert text_response.status_code == 200, f"Expected 200 OK, got {text_response.status_code}"
    assert text_response.headers["Content-Type"] == "text/plain", "Response should have text content type"
    assert "absolute change" in text_response.text.lower(), "Text results should include absolute change"


def test_cancel_analysis(client: TestClient, auth_headers: dict, db_session):
    """Tests cancelling an in-progress analysis via the API"""
    # Create a test time period and analysis request with PROCESSING status
    time_period = create_test_time_period(db_session)
    analysis = create_test_analysis_request(
        db_session, 
        time_period_id=time_period.id,
        status=AnalysisStatus.PROCESSING
    )
    
    # Make API request
    response = client.post(
        f"/api/analysis/requests/{analysis.id}/cancel",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the cancellation response
    assert data.get("success") is True, "Response should indicate successful cancellation"
    
    # Verify the analysis status has been updated to FAILED (since CANCELLED is not in the enum)
    status_response = client.get(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    status_data = status_response.json()
    
    assert status_data["status"] == AnalysisStatus.FAILED.name, "Analysis status should be updated to FAILED"


def test_rerun_analysis(client: TestClient, auth_headers: dict, db_session, test_freight_data):
    """Tests re-running a completed or failed analysis via the API"""
    # Create a test time period and completed analysis request
    time_period = create_test_time_period(db_session)
    analysis = create_test_analysis_request(
        db_session, 
        time_period_id=time_period.id,
        status=AnalysisStatus.COMPLETED,
        results={
            "absolute_change": 125.50,
            "percentage_change": 2.5,
            "trend_direction": TrendDirection.INCREASING.name
        }
    )
    
    # Make API request to rerun the analysis
    response = client.post(
        f"/api/analysis/requests/{analysis.id}/rerun",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the rerun response
    assert data.get("success") is True, "Response should indicate successful rerun initiation"
    
    # Verify the analysis request status has been reset
    status_response = client.get(
        f"/api/analysis/requests/{analysis.id}",
        headers=auth_headers
    )
    status_data = status_response.json()
    
    assert status_data["status"] == AnalysisStatus.PENDING.name, "Analysis status should be reset to PENDING"


def test_check_analysis_status(client: TestClient, auth_headers: dict, db_session):
    """Tests checking the status of an analysis via the API"""
    # Create test time period
    time_period = create_test_time_period(db_session)
    
    # Create analysis requests with different statuses
    analyses = {}
    for status in [AnalysisStatus.PENDING, AnalysisStatus.PROCESSING, AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]:
        analyses[status] = create_test_analysis_request(
            db_session, 
            time_period_id=time_period.id,
            status=status
        )
    
    # Test each status
    for status, analysis in analyses.items():
        response = client.get(
            f"/api/analysis/requests/{analysis.id}/status",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
        
        # Parse response data
        data = response.json()
        
        # Validate the status response
        assert data["status"] == status.name, f"Analysis status should be {status.name}"
        
        # Additional validation for COMPLETED status
        if status == AnalysisStatus.COMPLETED:
            assert "completed_at" in data, "COMPLETED status should include completed_at timestamp"
        
        # Additional validation for FAILED status
        if status == AnalysisStatus.FAILED:
            assert "error" in data, "FAILED status should include error information"


def test_create_saved_analysis(client: TestClient, auth_headers: dict, db_session):
    """Tests creating a new saved analysis via the API"""
    # Create a test time period in the database
    time_period = create_test_time_period(db_session)
    
    # Prepare saved analysis data
    payload = {
        "name": "Quarterly Ocean Freight Analysis",
        "description": "Analysis of ocean freight rates between Shanghai and Rotterdam",
        "time_period_id": str(time_period.id),
        "parameters": {
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "carrier_ids": [],
            "transport_mode": "OCEAN",
            "calculate_absolute_change": True,
            "calculate_percentage_change": True,
            "identify_trend": True
        },
        "output_format": OutputFormat.JSON.name
    }
    
    # Make API request
    response = client.post(
        "/api/analysis/saved",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the created saved analysis
    assert "id" in data, "Response should contain saved analysis ID"
    assert uuid.UUID(data["id"]), "ID should be a valid UUID"
    assert data["name"] == payload["name"], "Saved analysis name doesn't match"
    assert data["description"] == payload["description"], "Description doesn't match"
    assert data["time_period_id"] == payload["time_period_id"], "Time period ID doesn't match"
    assert data["parameters"] == payload["parameters"], "Parameters don't match"


def test_get_saved_analysis(client: TestClient, auth_headers: dict, db_session):
    """Tests retrieving a saved analysis by ID via the API"""
    # Create a test time period and saved analysis in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    
    # Make API request
    response = client.get(
        f"/api/analysis/saved/{saved_analysis.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the retrieved saved analysis
    assert data["id"] == str(saved_analysis.id), "Saved analysis ID doesn't match"
    assert data["name"] == saved_analysis.name, "Saved analysis name doesn't match"
    assert data["time_period_id"] == str(saved_analysis.time_period_id), "Time period ID doesn't match"
    assert data["parameters"] == saved_analysis.parameters, "Parameters don't match"


def test_list_saved_analyses(client: TestClient, auth_headers: dict, db_session):
    """Tests listing saved analyses with pagination via the API"""
    # Create a test time period
    time_period = create_test_time_period(db_session)
    
    # Create multiple test saved analyses in the database
    saved_analyses = [
        create_test_saved_analysis(db_session, time_period_id=time_period.id, name=f"Saved Analysis {i}")
        for i in range(5)
    ]
    
    # Make API request with pagination
    response = client.get(
        "/api/analysis/saved?page=1&page_size=3",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate pagination and data
    assert "items" in data, "Response should contain items array"
    assert "total" in data, "Response should contain total count"
    assert len(data["items"]) <= 3, "Items should not exceed page size"
    assert data["total"] >= 5, "Total count should include all created saved analyses"
    
    # Test filtering by name
    response = client.get(
        f"/api/analysis/saved?name={saved_analyses[0].name}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate filtering
    assert any(item["name"] == saved_analyses[0].name for item in data["items"]), "Filtered results should include the requested item"


def test_update_saved_analysis(client: TestClient, auth_headers: dict, db_session):
    """Tests updating an existing saved analysis via the API"""
    # Create a test time period and saved analysis in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    
    # Prepare update data
    updated_name = "Updated Saved Analysis"
    updated_description = "Updated description for testing"
    updated_parameters = {
        "origin": "Hong Kong",
        "destination": "Hamburg",
        "transport_mode": "OCEAN",
        "calculate_absolute_change": True,
        "calculate_percentage_change": True,
        "identify_trend": True
    }
    
    payload = {
        "name": updated_name,
        "description": updated_description,
        "parameters": updated_parameters
    }
    
    # Make API request
    response = client.put(
        f"/api/analysis/saved/{saved_analysis.id}",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the updated saved analysis
    assert data["id"] == str(saved_analysis.id), "Saved analysis ID should not change"
    assert data["name"] == updated_name, "Saved analysis name doesn't match update"
    assert data["description"] == updated_description, "Description doesn't match update"
    assert data["parameters"] == updated_parameters, "Parameters don't match update"


def test_delete_saved_analysis(client: TestClient, auth_headers: dict, db_session):
    """Tests deleting a saved analysis via the API"""
    # Create a test time period and saved analysis in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    
    # Make API request
    response = client.delete(
        f"/api/analysis/saved/{saved_analysis.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the deletion response
    assert data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify saved analysis no longer exists
    get_response = client.get(
        f"/api/analysis/saved/{saved_analysis.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404, "Saved analysis should no longer exist"


def test_run_saved_analysis(client: TestClient, auth_headers: dict, db_session, test_freight_data):
    """Tests running a saved analysis via the API"""
    # Create a test time period in the database
    start_date = datetime.now().date() - timedelta(days=30)
    end_date = datetime.now().date()
    time_period = create_test_time_period(
        db_session, 
        start_date=start_date,
        end_date=end_date,
        granularity=GranularityType.WEEKLY
    )
    
    # Create a test saved analysis
    saved_analysis = create_test_saved_analysis(
        db_session, 
        time_period_id=time_period.id,
        parameters={
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "transport_mode": "OCEAN",
            "calculate_absolute_change": True,
            "calculate_percentage_change": True,
            "identify_trend": True
        }
    )
    
    # Make API request to run the saved analysis
    response = client.post(
        f"/api/analysis/saved/{saved_analysis.id}/run",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the analysis results
    assert "results" in data, "Response should contain analysis results"
    assert "absolute_change" in data["results"], "Results should include absolute_change"
    assert "percentage_change" in data["results"], "Results should include percentage_change"
    assert "trend_direction" in data["results"], "Results should include trend_direction"
    
    # Verify the saved analysis last_run_at timestamp has been updated
    get_response = client.get(
        f"/api/analysis/saved/{saved_analysis.id}",
        headers=auth_headers
    )
    get_data = get_response.json()
    
    assert "last_run_at" in get_data, "Saved analysis should include last_run_at"
    assert get_data["last_run_at"] is not None, "last_run_at should be populated after running"


def test_create_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests creating a new analysis schedule via the API"""
    # Create a test time period and saved analysis in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    
    # Prepare analysis schedule data
    payload = {
        "name": "Weekly Ocean Freight Schedule",
        "saved_analysis_id": str(saved_analysis.id),
        "schedule_type": "WEEKLY",
        "schedule_value": "1",  # Run every Monday
        "is_active": True
    }
    
    # Make API request
    response = client.post(
        "/api/analysis/schedules",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the created analysis schedule
    assert "id" in data, "Response should contain schedule ID"
    assert uuid.UUID(data["id"]), "ID should be a valid UUID"
    assert data["name"] == payload["name"], "Schedule name doesn't match"
    assert data["saved_analysis_id"] == payload["saved_analysis_id"], "Saved analysis ID doesn't match"
    assert data["schedule_type"] == payload["schedule_type"], "Schedule type doesn't match"
    assert data["schedule_value"] == payload["schedule_value"], "Schedule value doesn't match"
    assert data["is_active"] == payload["is_active"], "Active status doesn't match"
    
    # Verify next_run_at has been calculated
    assert "next_run_at" in data, "Response should include next_run_at"
    assert data["next_run_at"] is not None, "next_run_at should be calculated"


def test_get_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests retrieving an analysis schedule by ID via the API"""
    # Create a test time period, saved analysis, and schedule in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    schedule = create_test_analysis_schedule(db_session, saved_analysis_id=saved_analysis.id)
    
    # Make API request
    response = client.get(
        f"/api/analysis/schedules/{schedule.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the retrieved analysis schedule
    assert data["id"] == str(schedule.id), "Schedule ID doesn't match"
    assert data["name"] == schedule.name, "Schedule name doesn't match"
    assert data["saved_analysis_id"] == str(schedule.saved_analysis_id), "Saved analysis ID doesn't match"
    assert data["schedule_type"] == schedule.schedule_type, "Schedule type doesn't match"
    assert data["is_active"] == schedule.is_active, "Active status doesn't match"


def test_list_analysis_schedules(client: TestClient, auth_headers: dict, db_session):
    """Tests listing analysis schedules with pagination via the API"""
    # Create a test time period and saved analysis
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    
    # Create multiple test analysis schedules in the database
    schedules = [
        create_test_analysis_schedule(
            db_session, 
            saved_analysis_id=saved_analysis.id, 
            name=f"Schedule {i}",
            is_active=(i % 2 == 0)  # Alternate active status
        )
        for i in range(5)
    ]
    
    # Make API request with pagination
    response = client.get(
        "/api/analysis/schedules?page=1&page_size=3",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate pagination and data
    assert "items" in data, "Response should contain items array"
    assert "total" in data, "Response should contain total count"
    assert len(data["items"]) <= 3, "Items should not exceed page size"
    assert data["total"] >= 5, "Total count should include all created schedules"
    
    # Test filtering by is_active
    response = client.get(
        "/api/analysis/schedules?is_active=true",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate filtering
    assert all(item["is_active"] for item in data["items"]), "Filtered results should all be active"


def test_update_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests updating an existing analysis schedule via the API"""
    # Create a test time period, saved analysis, and schedule in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    schedule = create_test_analysis_schedule(db_session, saved_analysis_id=saved_analysis.id)
    
    # Prepare update data
    updated_name = "Updated Schedule Name"
    updated_type = "MONTHLY"
    updated_value = "1"  # Run on 1st of each month
    
    payload = {
        "name": updated_name,
        "schedule_type": updated_type,
        "schedule_value": updated_value
    }
    
    # Make API request
    response = client.put(
        f"/api/analysis/schedules/{schedule.id}",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the updated analysis schedule
    assert data["id"] == str(schedule.id), "Schedule ID should not change"
    assert data["name"] == updated_name, "Schedule name doesn't match update"
    assert data["schedule_type"] == updated_type, "Schedule type doesn't match update"
    assert data["schedule_value"] == updated_value, "Schedule value doesn't match update"
    
    # Verify next_run_at has been recalculated
    assert data["next_run_at"] is not None, "next_run_at should be recalculated"


def test_delete_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests deleting an analysis schedule via the API"""
    # Create a test time period, saved analysis, and schedule in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    schedule = create_test_analysis_schedule(db_session, saved_analysis_id=saved_analysis.id)
    
    # Make API request
    response = client.delete(
        f"/api/analysis/schedules/{schedule.id}",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the deletion response
    assert data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify schedule no longer exists
    get_response = client.get(
        f"/api/analysis/schedules/{schedule.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404, "Analysis schedule should no longer exist"


def test_activate_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests activating an analysis schedule via the API"""
    # Create a test time period, saved analysis, and inactive schedule in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    schedule = create_test_analysis_schedule(
        db_session, 
        saved_analysis_id=saved_analysis.id,
        is_active=False
    )
    
    # Make API request
    response = client.post(
        f"/api/analysis/schedules/{schedule.id}/activate",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the activation response
    assert data["is_active"] is True, "Schedule should be activated"
    assert data["next_run_at"] is not None, "next_run_at should be calculated"


def test_deactivate_analysis_schedule(client: TestClient, auth_headers: dict, db_session):
    """Tests deactivating an analysis schedule via the API"""
    # Create a test time period, saved analysis, and active schedule in the database
    time_period = create_test_time_period(db_session)
    saved_analysis = create_test_saved_analysis(db_session, time_period_id=time_period.id)
    schedule = create_test_analysis_schedule(
        db_session, 
        saved_analysis_id=saved_analysis.id,
        is_active=True
    )
    
    # Make API request
    response = client.post(
        f"/api/analysis/schedules/{schedule.id}/deactivate",
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate the deactivation response
    assert data["is_active"] is False, "Schedule should be deactivated"


def test_error_handling_invalid_time_period(client: TestClient, auth_headers: dict):
    """Tests error handling for invalid time period data"""
    # Prepare invalid time period data (end_date before start_date)
    start_date = datetime.now().date()
    end_date = start_date - timedelta(days=30)  # End date is before start date
    
    payload = {
        "name": "Invalid Time Period",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "granularity": GranularityType.WEEKLY.name
    }
    
    # Make API request
    response = client.post(
        "/api/analysis/time-periods",
        json=payload,
        headers=auth_headers
    )
    
    # Verify response
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}: {response.text}"
    
    # Parse response data
    data = response.json()
    
    # Validate error details
    assert "detail" in data, "Response should contain error details"
    assert any("end_date" in str(error).lower() for error in data["detail"]), "Error should mention end_date"


def test_error_handling_nonexistent_resource(client: TestClient, auth_headers: dict):
    """Tests error handling for requests to non-existent resources"""
    # Generate a random UUID for a non-existent resource
    nonexistent_id = str(uuid.uuid4())
    
    # Test time period endpoint
    time_period_response = client.get(
        f"/api/analysis/time-periods/{nonexistent_id}",
        headers=auth_headers
    )
    
    assert time_period_response.status_code == 404, f"Expected 404 Not Found, got {time_period_response.status_code}"
    
    # Test analysis request endpoint
    analysis_response = client.get(
        f"/api/analysis/requests/{nonexistent_id}",
        headers=auth_headers
    )
    
    assert analysis_response.status_code == 404, f"Expected 404 Not Found, got {analysis_response.status_code}"
    
    # Test saved analysis endpoint
    saved_analysis_response = client.get(
        f"/api/analysis/saved/{nonexistent_id}",
        headers=auth_headers
    )
    
    assert saved_analysis_response.status_code == 404, f"Expected 404 Not Found, got {saved_analysis_response.status_code}"
    
    # Test analysis schedule endpoint
    schedule_response = client.get(
        f"/api/analysis/schedules/{nonexistent_id}",
        headers=auth_headers
    )
    
    assert schedule_response.status_code == 404, f"Expected 404 Not Found, got {schedule_response.status_code}"


def test_error_handling_unauthorized_access(client: TestClient):
    """Tests error handling for unauthorized access attempts"""
    # Test time period endpoint without authentication
    time_period_response = client.get("/api/analysis/time-periods")
    
    assert time_period_response.status_code == 401, f"Expected 401 Unauthorized, got {time_period_response.status_code}"
    
    # Test analysis request endpoint without authentication
    analysis_response = client.get("/api/analysis/requests")
    
    assert analysis_response.status_code == 401, f"Expected 401 Unauthorized, got {analysis_response.status_code}"
    
    # Test saved analysis endpoint without authentication
    saved_analysis_response = client.get("/api/analysis/saved")
    
    assert saved_analysis_response.status_code == 401, f"Expected 401 Unauthorized, got {saved_analysis_response.status_code}"
    
    # Test analysis schedule endpoint without authentication
    schedule_response = client.get("/api/analysis/schedules")
    
    assert schedule_response.status_code == 401, f"Expected 401 Unauthorized, got {schedule_response.status_code}"