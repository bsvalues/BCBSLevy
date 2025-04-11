"""
Tests for the error handling framework.

This module tests the error handling utilities and exception classes
to ensure they work correctly in different contexts.
"""

import pytest
from flask import jsonify, request

from tests.base_test import BaseTest
from utils.error_handling import (
    LevySystemException, ValidationError, NotFoundError, DataAccessError,
    ApiError, AuthorizationError, exception_handler, handle_exception,
    check_required_fields, check_resource_exists
)


class TestErrorHandlingFramework(BaseTest):
    """Test suite for the error handling framework."""
    
    def test_validation_error(self):
        """Test raising and handling ValidationError."""
        # Register a test route with the exception handler
        @self.app.route('/test-validation-error')
        @exception_handler()
        def test_validation_error():
            # This should raise a ValidationError
            check_required_fields({'name': 'Test'}, ['name', 'code'], 'district')
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-validation-error')
        
        # Verify response
        data = self.assert_error_response(response, 400, 'VALIDATION_ERROR')
        assert 'code' in data['error']['details'].get('missing_fields', []), \
            "Expected 'code' to be in missing fields"
    
    def test_not_found_error(self):
        """Test raising and handling NotFoundError."""
        # Register a test route with the exception handler
        @self.app.route('/test-not-found-error/<int:id>')
        @exception_handler()
        def test_not_found_error(id):
            # This should raise a NotFoundError
            check_resource_exists(None, 'tax_district', id)
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-not-found-error/999')
        
        # Verify response
        data = self.assert_error_response(response, 404, 'NOT_FOUND')
        assert data['error']['details'].get('resource_type') == 'tax_district', \
            "Expected resource_type to be 'tax_district'"
        assert data['error']['details'].get('resource_id') == 999, \
            "Expected resource_id to be 999"
    
    def test_data_access_error(self):
        """Test raising and handling DataAccessError."""
        # Register a test route
        @self.app.route('/test-data-access-error')
        @exception_handler()
        def test_data_access_error():
            raise DataAccessError(
                message="Failed to access database",
                entity="tax_district",
                operation="read"
            )
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-data-access-error')
        
        # Verify response
        data = self.assert_error_response(response, 500, 'DATA_ACCESS_ERROR')
        assert data['error']['details'].get('entity') == 'tax_district', \
            "Expected entity to be 'tax_district'"
        assert data['error']['details'].get('operation') == 'read', \
            "Expected operation to be 'read'"
    
    def test_api_error(self):
        """Test raising and handling ApiError."""
        # Register a test route
        @self.app.route('/test-api-error')
        @exception_handler()
        def test_api_error():
            raise ApiError(
                message="Failed to call external API",
                service="anthropic",
                endpoint="/v1/messages",
                status_code=429
            )
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-api-error')
        
        # Verify response
        data = self.assert_error_response(response, 502, 'API_ERROR')
        assert data['error']['details'].get('service') == 'anthropic', \
            "Expected service to be 'anthropic'"
        assert data['error']['details'].get('endpoint') == '/v1/messages', \
            "Expected endpoint to be '/v1/messages'"
        assert data['error']['details'].get('status_code') == 429, \
            "Expected status_code to be 429"
    
    def test_authorization_error(self):
        """Test raising and handling AuthorizationError."""
        # Register a test route
        @self.app.route('/test-authorization-error')
        @exception_handler()
        def test_authorization_error():
            raise AuthorizationError(
                message="Not authorized to access this resource",
                required_role="admin"
            )
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-authorization-error')
        
        # Verify response
        data = self.assert_error_response(response, 403, 'AUTHORIZATION_ERROR')
        assert data['error']['details'].get('required_role') == 'admin', \
            "Expected required_role to be 'admin'"
    
    def test_generic_exception_handling(self):
        """Test handling of generic exceptions."""
        # Register a test route
        @self.app.route('/test-generic-error')
        @exception_handler()
        def test_generic_error():
            # This will raise a generic exception
            raise ValueError("Something went wrong")
            return jsonify({'success': True})
        
        # Call the endpoint
        response = self.client.get('/test-generic-error')
        
        # Verify response
        data = self.assert_error_response(response, 500, 'UNEXPECTED_ERROR')
        # In debug mode, the details should include the exception message
        if self.app.config.get('DEBUG'):
            assert 'details' in data['error'], "Expected details in error response"
            if 'details' in data['error']:
                assert data['error']['details'].get('exception_message') == 'Something went wrong', \
                    "Expected exception_message to be 'Something went wrong'"
    
    def test_manual_exception_handling(self):
        """Test manual exception handling."""
        # Register a test route without the decorator
        @self.app.route('/test-manual-handling')
        def test_manual_handling():
            try:
                raise ValidationError(
                    message="Invalid input",
                    field="name"
                )
            except Exception as e:
                return handle_exception(e)
        
        # Call the endpoint
        response = self.client.get('/test-manual-handling')
        
        # Verify response
        data = self.assert_error_response(response, 400, 'VALIDATION_ERROR')
        assert data['error']['details'].get('field') == 'name', \
            "Expected field to be 'name'"