"""
Tests for the reports API endpoints of the Freight Price Movement Agent.

This module contains comprehensive tests for the reports API endpoints, covering
report creation, retrieval, updating, deletion, as well as report templates,
scheduled reports, and report sharing functionality.
"""

import pytest
import json
from datetime import datetime, timedelta
import uuid

from fastapi.testclient import TestClient

from ...models.enums import ReportFormat, ReportStatus, ScheduleFrequency
from ...models import Report, ReportTemplate, ScheduledReport, ReportShare, ReportExecution


def test_create_report(client, auth_headers, test_analysis_result):
    # Create a report payload
    report_data = {
        "name": "Test Report",
        "description": "Test report for API testing",
        "analysis_result_id": test_analysis_result.id,
        "format": ReportFormat.JSON.name,
        "parameters": {
            "include_visualization": True,
            "chart_type": "line"
        }
    }
    
    # Send the request to create a report
    response = client.post("/api/reports", json=report_data, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert "id" in response_data, "Response should contain report id"
    assert response_data["name"] == report_data["name"], "Report name doesn't match"
    assert response_data["description"] == report_data["description"], "Report description doesn't match"
    assert response_data["analysis_result_id"] == test_analysis_result.id, "Analysis result ID doesn't match"
    assert response_data["format"] == report_data["format"], "Report format doesn't match"
    
    # Verify that the ID is a valid UUID
    try:
        uuid.UUID(response_data["id"])
    except ValueError:
        pytest.fail("Report ID is not a valid UUID")


def test_get_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Test Report for Retrieval",
        description="A report created for testing the GET endpoint",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Send the request to get the report
    response = client.get(f"/api/reports/{test_report.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == test_report.id, "Report ID doesn't match"
    assert response_data["name"] == test_report.name, "Report name doesn't match"
    assert response_data["description"] == test_report.description, "Report description doesn't match"
    assert response_data["analysis_result_id"] == test_analysis_result.id, "Analysis result ID doesn't match"
    assert response_data["format"] == ReportFormat.JSON.name, "Report format doesn't match"


def test_list_reports(client, auth_headers, db_session, test_analysis_result):
    # Create multiple test reports in the database
    for i in range(5):
        test_report = Report(
            name=f"Test Report {i}",
            description=f"Test report {i} for list endpoint testing",
            analysis_result_id=test_analysis_result.id,
            format=ReportFormat.JSON if i % 2 == 0 else ReportFormat.CSV,
            created_by=auth_headers.get("user_id")
        )
        db_session.add(test_report)
    
    db_session.commit()
    
    # Send the request to list reports with pagination
    response = client.get("/api/reports?page=1&page_size=3", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the pagination and data
    response_data = response.json()
    assert "items" in response_data, "Response should contain items array"
    assert "total" in response_data, "Response should contain total count"
    assert "page" in response_data, "Response should contain page number"
    assert "page_size" in response_data, "Response should contain page size"
    
    assert response_data["page"] == 1, "Page number should be 1"
    assert response_data["page_size"] == 3, "Page size should be 3"
    assert len(response_data["items"]) <= 3, "Should return at most 3 items"
    
    # Test filtering by format
    response = client.get(f"/api/reports?format={ReportFormat.JSON.name}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for report in response_data["items"]:
        assert report["format"] == ReportFormat.JSON.name, "Filter by format not working correctly"


def test_update_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Original Report Name",
        description="Original description",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        parameters={"original": "parameter"}
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create the update payload
    update_data = {
        "name": "Updated Report Name",
        "description": "Updated description",
        "parameters": {"updated": "parameter"}
    }
    
    # Send the request to update the report
    response = client.put(f"/api/reports/{test_report.id}", json=update_data, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == test_report.id, "Report ID doesn't match"
    assert response_data["name"] == update_data["name"], "Updated name doesn't match"
    assert response_data["description"] == update_data["description"], "Updated description doesn't match"
    assert response_data["parameters"] == update_data["parameters"], "Updated parameters don't match"
    assert response_data["analysis_result_id"] == test_analysis_result.id, "Analysis result ID changed"


def test_delete_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report to Delete",
        description="This report will be deleted",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Send the request to delete the report
    response = client.delete(f"/api/reports/{test_report.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify the report no longer exists
    get_response = client.get(f"/api/reports/{test_report.id}", headers=auth_headers)
    assert get_response.status_code == 404, "Report should no longer exist"


def test_run_report(client, auth_headers, db_session, test_analysis_result, test_freight_data):
    # Create a test report in the database
    test_report = Report(
        name="Report to Run",
        description="This report will be executed",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        parameters={"include_visualization": True}
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Send the request to run the report
    response = client.post(f"/api/reports/{test_report.id}/run", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert "execution_id" in response_data, "Response should contain execution ID"
    assert "status" in response_data, "Response should contain status"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["status"] in [ReportStatus.COMPLETED.name, ReportStatus.PENDING.name, ReportStatus.PROCESSING.name], "Invalid status"
    
    if response_data["status"] == ReportStatus.COMPLETED.name:
        assert "output_location" in response_data, "Completed execution should have output location"


def test_duplicate_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Original Report",
        description="Report to be duplicated",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        parameters={"test": "parameter"}
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create the duplication request
    duplicate_data = {
        "name": "Duplicated Report"
    }
    
    # Send the request to duplicate the report
    response = client.post(f"/api/reports/{test_report.id}/duplicate", 
                         json=duplicate_data, 
                         headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["name"] == duplicate_data["name"], "Duplicated report name doesn't match"
    assert response_data["description"] == test_report.description, "Description not copied correctly"
    assert response_data["analysis_result_id"] == test_analysis_result.id, "Analysis result ID not copied"
    assert response_data["format"] == ReportFormat.JSON.name, "Format not copied correctly"
    assert response_data["parameters"] == test_report.parameters, "Parameters not copied correctly"
    assert response_data["id"] != test_report.id, "Duplicated report should have a new ID"


def test_create_report_template(client, auth_headers):
    # Create a template payload
    template_data = {
        "name": "Test Template",
        "description": "Test template for report creation",
        "default_parameters": {
            "include_visualization": True,
            "chart_type": "bar"
        },
        "default_filters": {
            "transport_mode": ["OCEAN", "AIR"],
            "date_range": "LAST_30_DAYS"
        },
        "default_format": ReportFormat.JSON.name,
        "is_public": True
    }
    
    # Send the request to create a template
    response = client.post("/api/reports/templates", json=template_data, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert "id" in response_data, "Response should contain template id"
    assert response_data["name"] == template_data["name"], "Template name doesn't match"
    assert response_data["description"] == template_data["description"], "Template description doesn't match"
    assert response_data["default_parameters"] == template_data["default_parameters"], "Template parameters don't match"
    assert response_data["default_filters"] == template_data["default_filters"], "Template filters don't match"
    assert response_data["default_format"] == template_data["default_format"], "Template format doesn't match"
    assert response_data["is_public"] == template_data["is_public"], "Template publicity setting doesn't match"
    
    # Verify that the ID is a valid UUID
    try:
        uuid.UUID(response_data["id"])
    except ValueError:
        pytest.fail("Template ID is not a valid UUID")


def test_get_report_template(client, auth_headers, db_session):
    # Create a test template in the database
    test_template = ReportTemplate(
        name="Test Template for Retrieval",
        description="A template created for testing the GET endpoint",
        default_format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        default_parameters={"test": "parameter"},
        is_public=True
    )
    db_session.add(test_template)
    db_session.commit()
    db_session.refresh(test_template)
    
    # Send the request to get the template
    response = client.get(f"/api/reports/templates/{test_template.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == test_template.id, "Template ID doesn't match"
    assert response_data["name"] == test_template.name, "Template name doesn't match"
    assert response_data["description"] == test_template.description, "Template description doesn't match"
    assert response_data["default_format"] == ReportFormat.JSON.name, "Template format doesn't match"
    assert response_data["default_parameters"] == test_template.default_parameters, "Template parameters don't match"
    assert response_data["is_public"] == test_template.is_public, "Template publicity setting doesn't match"


def test_list_report_templates(client, auth_headers, db_session):
    # Create multiple test templates in the database
    for i in range(5):
        test_template = ReportTemplate(
            name=f"Test Template {i}",
            description=f"Test template {i} for list endpoint testing",
            default_format=ReportFormat.JSON if i % 2 == 0 else ReportFormat.CSV,
            created_by=auth_headers.get("user_id"),
            is_public=(i % 2 == 0)  # Alternating public/private
        )
        db_session.add(test_template)
    
    db_session.commit()
    
    # Send the request to list templates with pagination
    response = client.get("/api/reports/templates?page=1&page_size=3", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the pagination and data
    response_data = response.json()
    assert "items" in response_data, "Response should contain items array"
    assert "total" in response_data, "Response should contain total count"
    assert "page" in response_data, "Response should contain page number"
    assert "page_size" in response_data, "Response should contain page size"
    
    assert response_data["page"] == 1, "Page number should be 1"
    assert response_data["page_size"] == 3, "Page size should be 3"
    assert len(response_data["items"]) <= 3, "Should return at most 3 items"
    
    # Test filtering by public templates
    response = client.get("/api/reports/templates?include_public=true", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    
    public_templates = [t for t in response_data["items"] if t["is_public"]]
    assert len(public_templates) > 0, "Should return public templates"


def test_update_report_template(client, auth_headers, db_session):
    # Create a test template in the database
    test_template = ReportTemplate(
        name="Original Template Name",
        description="Original template description",
        default_format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        default_parameters={"original": "parameter"},
        is_public=False
    )
    db_session.add(test_template)
    db_session.commit()
    db_session.refresh(test_template)
    
    # Create the update payload
    update_data = {
        "name": "Updated Template Name",
        "description": "Updated template description",
        "default_parameters": {"updated": "parameter"},
        "is_public": True
    }
    
    # Send the request to update the template
    response = client.put(
        f"/api/reports/templates/{test_template.id}", 
        json=update_data, 
        headers=auth_headers
    )
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == test_template.id, "Template ID doesn't match"
    assert response_data["name"] == update_data["name"], "Updated name doesn't match"
    assert response_data["description"] == update_data["description"], "Updated description doesn't match"
    assert response_data["default_parameters"] == update_data["default_parameters"], "Updated parameters don't match"
    assert response_data["is_public"] == update_data["is_public"], "Updated publicity setting doesn't match"
    assert response_data["default_format"] == ReportFormat.JSON.name, "Format should not have changed"


def test_delete_report_template(client, auth_headers, db_session):
    # Create a test template in the database
    test_template = ReportTemplate(
        name="Template to Delete",
        description="This template will be deleted",
        default_format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        is_public=True
    )
    db_session.add(test_template)
    db_session.commit()
    db_session.refresh(test_template)
    
    # Send the request to delete the template
    response = client.delete(f"/api/reports/templates/{test_template.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify the template no longer exists
    get_response = client.get(f"/api/reports/templates/{test_template.id}", headers=auth_headers)
    assert get_response.status_code == 404, "Template should no longer exist"


def test_create_report_from_template(client, auth_headers, db_session):
    # Create a test template in the database
    test_template = ReportTemplate(
        name="Template for Report Creation",
        description="Template used to create a new report",
        default_format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id"),
        default_parameters={"key": "value", "chart_type": "line"},
        default_filters={"date_range": "LAST_30_DAYS"},
        is_public=True
    )
    db_session.add(test_template)
    db_session.commit()
    db_session.refresh(test_template)
    
    # Create data for the new report
    report_data = {
        "name": "Report from Template",
        "parameter_overrides": {
            "chart_type": "bar"  # Override just one parameter
        }
    }
    
    # Send the request to create a report from the template
    response = client.post(
        f"/api/reports/templates/{test_template.id}/create-report", 
        json=report_data, 
        headers=auth_headers
    )
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["name"] == report_data["name"], "Report name doesn't match"
    assert response_data["format"] == ReportFormat.JSON.name, "Format not copied from template"
    
    # Check that parameters were merged correctly
    assert response_data["parameters"]["key"] == "value", "Template parameter not preserved"
    assert response_data["parameters"]["chart_type"] == "bar", "Parameter override not applied"
    
    # Check that filters were copied
    assert response_data["filters"] == test_template.default_filters, "Filters not copied from template"


def test_create_scheduled_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Scheduling",
        description="This report will be scheduled",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create the scheduled report payload
    schedule_data = {
        "report_id": test_report.id,
        "frequency": ScheduleFrequency.WEEKLY.name,
        "day_of_week": 1,  # Monday
        "hour": 8,
        "minute": 30,
        "active": True,
        "recipients": ["user@example.com"]
    }
    
    # Send the request to create a scheduled report
    response = client.post("/api/reports/scheduled", json=schedule_data, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert "id" in response_data, "Response should contain scheduled report id"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["frequency"] == ScheduleFrequency.WEEKLY.name, "Frequency doesn't match"
    assert response_data["day_of_week"] == 1, "Day of week doesn't match"
    assert response_data["hour"] == 8, "Hour doesn't match"
    assert response_data["minute"] == 30, "Minute doesn't match"
    assert response_data["active"] is True, "Active status doesn't match"
    assert response_data["recipients"] == schedule_data["recipients"], "Recipients don't match"
    assert "next_run_at" in response_data, "Next run time should be calculated"
    
    # Verify that the ID is a valid UUID
    try:
        uuid.UUID(response_data["id"])
    except ValueError:
        pytest.fail("Scheduled report ID is not a valid UUID")


def test_get_scheduled_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Schedule Retrieval",
        description="Report used to test scheduled report retrieval",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test scheduled report
    scheduled_report = ScheduledReport(
        report_id=test_report.id,
        frequency=ScheduleFrequency.DAILY,
        hour=9,
        minute=0,
        active=True,
        created_by=auth_headers.get("user_id"),
        recipients=["test@example.com"]
    )
    db_session.add(scheduled_report)
    db_session.commit()
    db_session.refresh(scheduled_report)
    
    # Send the request to get the scheduled report
    response = client.get(f"/api/reports/scheduled/{scheduled_report.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == scheduled_report.id, "Scheduled report ID doesn't match"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["frequency"] == ScheduleFrequency.DAILY.name, "Frequency doesn't match"
    assert response_data["hour"] == 9, "Hour doesn't match"
    assert response_data["minute"] == 0, "Minute doesn't match"
    assert response_data["active"] is True, "Active status doesn't match"
    assert "next_run_at" in response_data, "Next run time should be calculated"


def test_list_scheduled_reports(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Schedule Listing",
        description="Report used to test scheduled report listing",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create multiple test scheduled reports
    for i in range(5):
        scheduled_report = ScheduledReport(
            report_id=test_report.id,
            frequency=ScheduleFrequency.DAILY if i % 2 == 0 else ScheduleFrequency.WEEKLY,
            hour=9,
            minute=0,
            active=(i % 3 != 0),  # Mix of active/inactive
            created_by=auth_headers.get("user_id"),
            recipients=[f"test{i}@example.com"]
        )
        db_session.add(scheduled_report)
    
    db_session.commit()
    
    # Send the request to list scheduled reports with pagination
    response = client.get("/api/reports/scheduled?page=1&page_size=3", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the pagination and data
    response_data = response.json()
    assert "items" in response_data, "Response should contain items array"
    assert "total" in response_data, "Response should contain total count"
    assert "page" in response_data, "Response should contain page number"
    assert "page_size" in response_data, "Response should contain page size"
    
    assert response_data["page"] == 1, "Page number should be 1"
    assert response_data["page_size"] == 3, "Page size should be 3"
    assert len(response_data["items"]) <= 3, "Should return at most 3 items"
    
    # Test filtering by active status
    response = client.get("/api/reports/scheduled?active=true", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for schedule in response_data["items"]:
        assert schedule["active"] is True, "Filter by active status not working correctly"
    
    # Test filtering by frequency
    response = client.get(f"/api/reports/scheduled?frequency={ScheduleFrequency.DAILY.name}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for schedule in response_data["items"]:
        assert schedule["frequency"] == ScheduleFrequency.DAILY.name, "Filter by frequency not working correctly"


def test_update_scheduled_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Schedule Update",
        description="Report used to test scheduled report updates",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test scheduled report
    scheduled_report = ScheduledReport(
        report_id=test_report.id,
        frequency=ScheduleFrequency.DAILY,
        hour=9,
        minute=0,
        active=True,
        created_by=auth_headers.get("user_id"),
        recipients=["original@example.com"]
    )
    db_session.add(scheduled_report)
    db_session.commit()
    db_session.refresh(scheduled_report)
    
    # Create update payload
    update_data = {
        "frequency": ScheduleFrequency.WEEKLY.name,
        "day_of_week": 3,  # Wednesday
        "hour": 14,
        "minute": 30,
        "active": False,
        "recipients": ["updated@example.com"]
    }
    
    # Send the request to update the scheduled report
    response = client.put(
        f"/api/reports/scheduled/{scheduled_report.id}", 
        json=update_data, 
        headers=auth_headers
    )
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == scheduled_report.id, "Scheduled report ID doesn't match"
    assert response_data["frequency"] == update_data["frequency"], "Updated frequency doesn't match"
    assert response_data["day_of_week"] == update_data["day_of_week"], "Updated day_of_week doesn't match"
    assert response_data["hour"] == update_data["hour"], "Updated hour doesn't match"
    assert response_data["minute"] == update_data["minute"], "Updated minute doesn't match"
    assert response_data["active"] == update_data["active"], "Updated active status doesn't match"
    assert response_data["recipients"] == update_data["recipients"], "Updated recipients don't match"
    assert "next_run_at" in response_data, "Next run time should be recalculated"


def test_delete_scheduled_report(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Schedule Deletion",
        description="Report used to test scheduled report deletion",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test scheduled report
    scheduled_report = ScheduledReport(
        report_id=test_report.id,
        frequency=ScheduleFrequency.DAILY,
        hour=9,
        minute=0,
        active=True,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(scheduled_report)
    db_session.commit()
    db_session.refresh(scheduled_report)
    
    # Send the request to delete the scheduled report
    response = client.delete(f"/api/reports/scheduled/{scheduled_report.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify the scheduled report no longer exists
    get_response = client.get(f"/api/reports/scheduled/{scheduled_report.id}", headers=auth_headers)
    assert get_response.status_code == 404, "Scheduled report should no longer exist"


def test_create_report_share(client, auth_headers, db_session, test_analysis_result, test_user):
    # Create a test report in the database
    test_report = Report(
        name="Report for Sharing",
        description="Report used to test report sharing",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create share payload
    share_data = {
        "report_id": test_report.id,
        "shared_with_id": test_user.id,
        "can_view": True,
        "can_edit": True,
        "can_delete": False,
        "can_share": False,
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    # Send the request to create a report share
    response = client.post("/api/reports/shares", json=share_data, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert "id" in response_data, "Response should contain share ID"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["shared_with_id"] == test_user.id, "Shared with ID doesn't match"
    assert response_data["owner_id"] == auth_headers.get("user_id"), "Owner ID should be the current user"
    assert response_data["can_view"] is True, "View permission doesn't match"
    assert response_data["can_edit"] is True, "Edit permission doesn't match"
    assert response_data["can_delete"] is False, "Delete permission doesn't match"
    assert response_data["can_share"] is False, "Share permission doesn't match"
    assert "expires_at" in response_data, "Expiration date should be set"


def test_get_report_share(client, auth_headers, db_session, test_analysis_result, test_user):
    # Create a test report in the database
    test_report = Report(
        name="Report for Share Retrieval",
        description="Report used to test share retrieval",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test report share
    report_share = ReportShare(
        report_id=test_report.id,
        owner_id=auth_headers.get("user_id"),
        shared_with_id=test_user.id,
        can_view=True,
        can_edit=True,
        can_delete=False,
        can_share=False,
        expires_at=datetime.now() + timedelta(days=30)
    )
    db_session.add(report_share)
    db_session.commit()
    db_session.refresh(report_share)
    
    # Send the request to get the report share
    response = client.get(f"/api/reports/shares/{report_share.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == report_share.id, "Share ID doesn't match"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["owner_id"] == auth_headers.get("user_id"), "Owner ID doesn't match"
    assert response_data["shared_with_id"] == test_user.id, "Shared with ID doesn't match"
    assert response_data["can_view"] is True, "View permission doesn't match"
    assert response_data["can_edit"] is True, "Edit permission doesn't match"
    assert response_data["can_delete"] is False, "Delete permission doesn't match"
    assert response_data["can_share"] is False, "Share permission doesn't match"
    assert "expires_at" in response_data, "Expiration date should be present"


def test_list_report_shares(client, auth_headers, db_session, test_analysis_result, test_user):
    # Create a test report in the database
    test_report = Report(
        name="Report for Share Listing",
        description="Report used to test share listing",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create multiple test report shares
    for i in range(5):
        report_share = ReportShare(
            report_id=test_report.id,
            owner_id=auth_headers.get("user_id"),
            shared_with_id=test_user.id,
            can_view=True,
            can_edit=(i % 2 == 0),  # Mix of permissions
            can_delete=False,
            can_share=False,
            expires_at=datetime.now() + timedelta(days=30)
        )
        db_session.add(report_share)
    
    db_session.commit()
    
    # Send the request to list report shares with pagination
    response = client.get("/api/reports/shares?page=1&page_size=3", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the pagination and data
    response_data = response.json()
    assert "items" in response_data, "Response should contain items array"
    assert "total" in response_data, "Response should contain total count"
    assert "page" in response_data, "Response should contain page number"
    assert "page_size" in response_data, "Response should contain page size"
    
    assert response_data["page"] == 1, "Page number should be 1"
    assert response_data["page_size"] == 3, "Page size should be 3"
    assert len(response_data["items"]) <= 3, "Should return at most 3 items"
    
    # Test filtering by report_id
    response = client.get(f"/api/reports/shares?report_id={test_report.id}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for share in response_data["items"]:
        assert share["report_id"] == test_report.id, "Filter by report_id not working correctly"
    
    # Test filtering by owner_id
    response = client.get(f"/api/reports/shares?owner_id={auth_headers.get('user_id')}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for share in response_data["items"]:
        assert share["owner_id"] == auth_headers.get("user_id"), "Filter by owner_id not working correctly"
    
    # Test filtering by shared_with_id
    response = client.get(f"/api/reports/shares?shared_with_id={test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for share in response_data["items"]:
        assert share["shared_with_id"] == test_user.id, "Filter by shared_with_id not working correctly"


def test_update_report_share(client, auth_headers, db_session, test_analysis_result, test_user):
    # Create a test report in the database
    test_report = Report(
        name="Report for Share Update",
        description="Report used to test share updates",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test report share
    report_share = ReportShare(
        report_id=test_report.id,
        owner_id=auth_headers.get("user_id"),
        shared_with_id=test_user.id,
        can_view=True,
        can_edit=False,
        can_delete=False,
        can_share=False,
        expires_at=datetime.now() + timedelta(days=30)
    )
    db_session.add(report_share)
    db_session.commit()
    db_session.refresh(report_share)
    
    # Create update payload
    update_data = {
        "can_edit": True,
        "can_share": True,
        "expires_at": (datetime.now() + timedelta(days=60)).isoformat()
    }
    
    # Send the request to update the report share
    response = client.put(
        f"/api/reports/shares/{report_share.id}", 
        json=update_data, 
        headers=auth_headers
    )
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == report_share.id, "Share ID doesn't match"
    assert response_data["can_view"] is True, "View permission should still be True"
    assert response_data["can_edit"] is True, "Edit permission should be updated"
    assert response_data["can_delete"] is False, "Delete permission should still be False"
    assert response_data["can_share"] is True, "Share permission should be updated"
    assert "expires_at" in response_data, "Expiration date should be present"


def test_delete_report_share(client, auth_headers, db_session, test_analysis_result, test_user):
    # Create a test report in the database
    test_report = Report(
        name="Report for Share Deletion",
        description="Report used to test share deletion",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test report share
    report_share = ReportShare(
        report_id=test_report.id,
        owner_id=auth_headers.get("user_id"),
        shared_with_id=test_user.id,
        can_view=True,
        can_edit=True,
        can_delete=False,
        can_share=False,
        expires_at=datetime.now() + timedelta(days=30)
    )
    db_session.add(report_share)
    db_session.commit()
    db_session.refresh(report_share)
    
    # Send the request to delete the report share
    response = client.delete(f"/api/reports/shares/{report_share.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data.get("success") is True, "Response should indicate successful deletion"
    
    # Verify the report share no longer exists
    get_response = client.get(f"/api/reports/shares/{report_share.id}", headers=auth_headers)
    assert get_response.status_code == 404, "Report share should no longer exist"


def test_get_report_execution(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Execution Retrieval",
        description="Report used to test execution retrieval",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test report execution
    report_execution = ReportExecution(
        report_id=test_report.id,
        status=ReportStatus.COMPLETED,
        created_by=auth_headers.get("user_id"),
        output_location="s3://test-bucket/reports/execution123.json",
        execution_time=5.23  # seconds
    )
    db_session.add(report_execution)
    db_session.commit()
    db_session.refresh(report_execution)
    
    # Send the request to get the report execution
    response = client.get(f"/api/reports/executions/{report_execution.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the response data
    response_data = response.json()
    assert response_data["id"] == report_execution.id, "Execution ID doesn't match"
    assert response_data["report_id"] == test_report.id, "Report ID doesn't match"
    assert response_data["status"] == ReportStatus.COMPLETED.name, "Status doesn't match"
    assert response_data["created_by"] == auth_headers.get("user_id"), "Created by doesn't match"
    assert response_data["output_location"] == report_execution.output_location, "Output location doesn't match"
    assert response_data["execution_time"] == report_execution.execution_time, "Execution time doesn't match"


def test_list_report_executions(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Execution Listing",
        description="Report used to test execution listing",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create multiple test report executions
    statuses = [ReportStatus.COMPLETED, ReportStatus.FAILED, ReportStatus.PENDING, 
                ReportStatus.PROCESSING, ReportStatus.COMPLETED]
    
    for i, status in enumerate(statuses):
        report_execution = ReportExecution(
            report_id=test_report.id,
            status=status,
            created_by=auth_headers.get("user_id"),
            output_location=f"s3://test-bucket/reports/execution{i}.json" if status == ReportStatus.COMPLETED else None,
            execution_time=3.45 if status == ReportStatus.COMPLETED else None,
            error_message="Test error" if status == ReportStatus.FAILED else None
        )
        db_session.add(report_execution)
    
    db_session.commit()
    
    # Send the request to list report executions with pagination
    response = client.get("/api/reports/executions?page=1&page_size=3", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the pagination and data
    response_data = response.json()
    assert "items" in response_data, "Response should contain items array"
    assert "total" in response_data, "Response should contain total count"
    assert "page" in response_data, "Response should contain page number"
    assert "page_size" in response_data, "Response should contain page size"
    
    assert response_data["page"] == 1, "Page number should be 1"
    assert response_data["page_size"] == 3, "Page size should be 3"
    assert len(response_data["items"]) <= 3, "Should return at most 3 items"
    
    # Test filtering by report_id
    response = client.get(f"/api/reports/executions?report_id={test_report.id}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for execution in response_data["items"]:
        assert execution["report_id"] == test_report.id, "Filter by report_id not working correctly"
    
    # Test filtering by status
    response = client.get(f"/api/reports/executions?status={ReportStatus.COMPLETED.name}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for execution in response_data["items"]:
        assert execution["status"] == ReportStatus.COMPLETED.name, "Filter by status not working correctly"
    
    # Test filtering by created_by
    response = client.get(f"/api/reports/executions?created_by={auth_headers.get('user_id')}", headers=auth_headers)
    assert response.status_code == 200
    response_data = response.json()
    for execution in response_data["items"]:
        assert execution["created_by"] == auth_headers.get("user_id"), "Filter by created_by not working correctly"


def test_download_report_execution(client, auth_headers, db_session, test_analysis_result):
    # Create a test report in the database
    test_report = Report(
        name="Report for Execution Download",
        description="Report used to test execution download",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=auth_headers.get("user_id")
    )
    db_session.add(test_report)
    db_session.commit()
    db_session.refresh(test_report)
    
    # Create a test report execution (mock with a predetermined result)
    output_content = {"test": "data", "results": [1, 2, 3]}
    
    # In a real test, you might need to mock S3 or file operations
    # For now, we'll assume the API endpoint can handle this scenario
    report_execution = ReportExecution(
        report_id=test_report.id,
        status=ReportStatus.COMPLETED,
        created_by=auth_headers.get("user_id"),
        output_location="test_location",  # Would normally be a file path or S3 URI
        execution_time=2.34,
        result_data=json.dumps(output_content)  # Store the result directly for testing
    )
    db_session.add(report_execution)
    db_session.commit()
    db_session.refresh(report_execution)
    
    # Send the request to download the report execution
    response = client.get(f"/api/reports/executions/{report_execution.id}/download", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Check the content type
    assert response.headers.get("Content-Type") == "application/json"
    
    # Check the content
    response_data = response.json()
    assert response_data == output_content, "Downloaded content doesn't match expected output"


def test_error_handling_nonexistent_report(client, auth_headers):
    # Generate a random UUID that doesn't exist
    non_existent_id = str(uuid.uuid4())
    
    # Send a request to get a non-existent report
    response = client.get(f"/api/reports/{non_existent_id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
    
    # Check the error response structure
    response_data = response.json()
    assert "detail" in response_data, "Error response should contain detail"
    assert "message" in response_data, "Error response should contain message"
    assert "report" in response_data.get("message", "").lower(), "Error message should mention report"


def test_error_handling_permission_denied(client, auth_headers, db_session, test_analysis_result, 
                                        test_admin_user, admin_auth_headers):
    # Create a test report owned by the admin user
    admin_report = Report(
        name="Admin's Report",
        description="Report owned by admin that regular user shouldn't access",
        analysis_result_id=test_analysis_result.id,
        format=ReportFormat.JSON,
        created_by=test_admin_user.id
    )
    db_session.add(admin_report)
    db_session.commit()
    db_session.refresh(admin_report)
    
    # Regular user tries to access admin's report
    response = client.get(f"/api/reports/{admin_report.id}", headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
    
    # Check the error response structure
    response_data = response.json()
    assert "detail" in response_data, "Error response should contain detail"
    assert "permission" in response_data.get("detail", "").lower(), "Error should mention permission"
    
    # Try other operations that should be denied
    update_response = client.put(
        f"/api/reports/{admin_report.id}", 
        json={"name": "Hacked Report"}, 
        headers=auth_headers
    )
    assert update_response.status_code == 403, "Update should be forbidden"
    
    delete_response = client.delete(f"/api/reports/{admin_report.id}", headers=auth_headers)
    assert delete_response.status_code == 403, "Delete should be forbidden"
    
    run_response = client.post(f"/api/reports/{admin_report.id}/run", headers=auth_headers)
    assert run_response.status_code == 403, "Running the report should be forbidden"


def test_error_handling_validation_errors(client, auth_headers):
    # Create an invalid report payload missing required fields
    invalid_report = {
        "name": "Invalid Report"
        # Missing required fields like analysis_result_id
    }
    
    # Send the request to create an invalid report
    response = client.post("/api/reports", json=invalid_report, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
    
    # Check the validation error structure
    response_data = response.json()
    assert "detail" in response_data, "Validation error should contain detail"
    assert isinstance(response_data["detail"], list), "Validation errors should be a list"
    
    # Create a report with invalid format
    invalid_format_report = {
        "name": "Invalid Format Report",
        "analysis_result_id": str(uuid.uuid4()),
        "format": "INVALID_FORMAT"  # Invalid enum value
    }
    
    # Send the request
    response = client.post("/api/reports", json=invalid_format_report, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
    
    # Check for validation error about the format
    response_data = response.json()
    assert any("format" in str(detail).lower() for detail in response_data.get("detail", [])), \
        "Validation error should mention format field"
    
    # Try creating a scheduled report with invalid frequency
    invalid_schedule = {
        "report_id": str(uuid.uuid4()),
        "frequency": "INVALID_FREQUENCY",
        "hour": 9,
        "minute": 0
    }
    
    # Send the request
    response = client.post("/api/reports/scheduled", json=invalid_schedule, headers=auth_headers)
    
    # Assert the response
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
    
    # Check for validation error about the frequency
    response_data = response.json()
    assert any("frequency" in str(detail).lower() for detail in response_data.get("detail", [])), \
        "Validation error should mention frequency field"