"""
Automated testing of application routes.
This module tests all routes to ensure they return proper status codes.
"""
import pytest
from flask import url_for
from main import app
import os

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_home_page(client):
    """Test that the home page returns a 200 status code."""
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard_page(client):
    """Test that the dashboard page returns a 200 status code."""
    response = client.get('/reports/dashboard')
    assert response.status_code == 200

def test_forecasting_page(client):
    """Test that the forecasting page returns a 200 status code."""
    response = client.get('/forecasting/')
    assert response.status_code == 200

def test_historical_analysis_page(client):
    """Test that the historical analysis page returns a 200 status code."""
    response = client.get('/historical-analysis/')
    assert response.status_code == 200

def test_levy_calculator_page(client):
    """Test that the levy calculator page returns a 200 status code."""
    response = client.get('/levy-calculator/')
    assert response.status_code == 200

def test_mcp_page(client):
    """Test that the MCP page returns a 200 status code."""
    response = client.get('/mcp/')
    assert response.status_code == 200

def test_reports_redirect(client):
    """Test that the reports redirect works properly."""
    response = client.get('/reports/')
    assert response.status_code == 302  # Redirect status code