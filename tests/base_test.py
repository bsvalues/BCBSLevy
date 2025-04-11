"""
Base test class for Levy Calculation System tests.

This module provides a standardized base test class with setup helpers,
assertion utilities, and other testing tools to make writing tests more
consistent and efficient.
"""

import json
import os
import pytest
from typing import Dict, Any, List, Optional, Union, Tuple
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from app import db as flask_db


class BaseTest:
    """
    Base test class for all Levy Calculation System tests.
    
    This class provides common setup and utility methods for tests,
    helping standardize test structure and reduce duplication.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self, app: Flask, client: FlaskClient, db: SQLAlchemy):
        """
        Set up test environment.
        
        This fixture runs automatically for all test methods in classes
        that inherit from BaseTest.
        
        Args:
            app: Flask application fixture
            client: Flask test client fixture
            db: SQLAlchemy database fixture
        """
        self.app = app
        self.client = client
        self.db = db
        
        # Set up test context
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Yield control back to the test
        yield
        
        # Clean up
        self.db.session.rollback()
        self.app_context.pop()
    
    def create_tax_district(self, name: str, code: str, year: int = 2024) -> Dict[str, Any]:
        """
        Create a tax district for testing.
        
        Args:
            name: Name of the tax district
            code: District code
            year: Assessment year
            
        Returns:
            Dictionary with the created district's info
        """
        from sqlalchemy import text
        # Use raw SQL to ensure schema compatibility
        result = self.db.session.execute(
            text("""
            INSERT INTO tax_district (name, code, year, created_at, updated_at) 
            VALUES (:name, :code, :year, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
            """),
            {"name": name, "code": code, "year": year}
        )
        district_id = result.fetchone()[0]
        self.db.session.commit()
        
        return {
            "id": district_id,
            "name": name,
            "code": code,
            "year": year
        }
    
    def create_tax_code(self, code: str, levy_rate: float, total_assessed_value: float,
                        levy_amount: Optional[float] = None, year: int = 2024) -> Dict[str, Any]:
        """
        Create a tax code for testing.
        
        Args:
            code: Tax code
            levy_rate: Rate as a float (e.g., 2.5 for 2.5%)
            total_assessed_value: Total assessed value
            levy_amount: Levy amount (calculated if not provided)
            year: Assessment year
            
        Returns:
            Dictionary with the created tax code's info
        """
        if levy_amount is None:
            levy_amount = (levy_rate / 1000) * total_assessed_value
            
        from sqlalchemy import text
        result = self.db.session.execute(
            text("""
            INSERT INTO tax_code (code, levy_amount, levy_rate, total_assessed_value, year, created_at, updated_at) 
            VALUES (:code, :levy_amount, :levy_rate, :total_assessed_value, :year, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
            """),
            {
                "code": code,
                "levy_amount": levy_amount,
                "levy_rate": levy_rate,
                "total_assessed_value": total_assessed_value,
                "year": year
            }
        )
        tax_code_id = result.fetchone()[0]
        self.db.session.commit()
        
        return {
            "id": tax_code_id,
            "code": code,
            "levy_amount": levy_amount,
            "levy_rate": levy_rate,
            "total_assessed_value": total_assessed_value,
            "year": year
        }
    
    def create_property(self, parcel_number: str, address: str, assessed_value: float,
                        tax_code_id: int, year: int = 2024) -> Dict[str, Any]:
        """
        Create a property for testing.
        
        Args:
            parcel_number: Parcel number/identifier
            address: Property address
            assessed_value: Assessed value of the property
            tax_code_id: ID of the tax code this property belongs to
            year: Assessment year
            
        Returns:
            Dictionary with the created property's info
        """
        from sqlalchemy import text
        result = self.db.session.execute(
            text("""
            INSERT INTO property (parcel_number, address, assessed_value, tax_code_id, year, created_at, updated_at) 
            VALUES (:parcel_number, :address, :assessed_value, :tax_code_id, :year, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
            """),
            {
                "parcel_number": parcel_number,
                "address": address,
                "assessed_value": assessed_value,
                "tax_code_id": tax_code_id,
                "year": year
            }
        )
        property_id = result.fetchone()[0]
        self.db.session.commit()
        
        return {
            "id": property_id,
            "parcel_number": parcel_number,
            "address": address,
            "assessed_value": assessed_value,
            "tax_code_id": tax_code_id,
            "year": year
        }
    
    def assert_response_status(self, response, expected_status: int = 200, message: str = None):
        """
        Assert that a response has the expected status code.
        
        Args:
            response: Flask test client response
            expected_status: Expected HTTP status code
            message: Optional message for the assertion
        """
        assert response.status_code == expected_status, \
            message or f"Expected status {expected_status}, got {response.status_code}. Response: {response.data.decode('utf-8')}"
    
    def assert_json_response(self, response, expected_status: int = 200) -> Dict[str, Any]:
        """
        Assert that a response contains valid JSON and has the expected status.
        
        Args:
            response: Flask test client response
            expected_status: Expected HTTP status code
            
        Returns:
            Parsed JSON data from the response
        """
        self.assert_response_status(response, expected_status)
        
        content_type = response.headers.get('Content-Type', '')
        assert 'application/json' in content_type, \
            f"Expected JSON response, got Content-Type: {content_type}"
        
        try:
            return json.loads(response.data)
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {response.data.decode('utf-8')}")
    
    def assert_success_response(self, response, expected_status: int = 200) -> Dict[str, Any]:
        """
        Assert that a JSON response indicates success.
        
        Args:
            response: Flask test client response
            expected_status: Expected HTTP status code
            
        Returns:
            Parsed JSON data from the response
        """
        data = self.assert_json_response(response, expected_status)
        assert data.get('success') is True, f"Expected 'success': true in response: {data}"
        return data
    
    def assert_error_response(self, response, expected_status: int = 400, 
                              expected_code: str = None) -> Dict[str, Any]:
        """
        Assert that a JSON response indicates an error.
        
        Args:
            response: Flask test client response
            expected_status: Expected HTTP status code
            expected_code: Expected error code in the response
            
        Returns:
            Parsed JSON data from the response
        """
        data = self.assert_json_response(response, expected_status)
        assert data.get('success') is False, f"Expected 'success': false in response: {data}"
        assert 'error' in data, f"Expected 'error' field in response: {data}"
        
        if expected_code:
            assert data['error'].get('code') == expected_code, \
                f"Expected error code '{expected_code}', got '{data['error'].get('code')}'"
        
        return data
    
    def json_post(self, endpoint: str, data: Dict[str, Any], 
                  expect_status: int = 200) -> Tuple[Dict[str, Any], Any]:
        """
        Send a POST request with JSON data and assert the response status.
        
        Args:
            endpoint: API endpoint to post to
            data: JSON-serializable data to send
            expect_status: Expected HTTP status code
            
        Returns:
            Tuple of (parsed JSON response, raw response object)
        """
        response = self.client.post(
            endpoint,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assert_response_status(response, expect_status)
        json_data = json.loads(response.data)
        return json_data, response
    
    def json_get(self, endpoint: str, query_params: Dict[str, str] = None,
                 expect_status: int = 200) -> Tuple[Dict[str, Any], Any]:
        """
        Send a GET request and assert the response status.
        
        Args:
            endpoint: API endpoint to get
            query_params: Optional query parameters
            expect_status: Expected HTTP status code
            
        Returns:
            Tuple of (parsed JSON response, raw response object)
        """
        response = self.client.get(
            endpoint,
            query_string=query_params
        )
        self.assert_response_status(response, expect_status)
        json_data = json.loads(response.data)
        return json_data, response
    
    @classmethod
    def get_mock_api_response(cls, fixture_name: str) -> Dict[str, Any]:
        """
        Load a mock API response from a fixture file.
        
        Args:
            fixture_name: Name of the fixture file (without extension)
            
        Returns:
            Loaded fixture data
        """
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            f"{fixture_name}.json"
        )
        
        with open(fixture_path, 'r') as f:
            return json.load(f)
    
    def execute_raw_sql(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute raw SQL and return results as dictionaries.
        
        Args:
            sql: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        from sqlalchemy import text
        result = self.db.session.execute(text(sql), params or {})
        
        # Convert result to list of dictionaries
        column_names = result.keys()
        return [dict(zip(column_names, row)) for row in result.fetchall()]