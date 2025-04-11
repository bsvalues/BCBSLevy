"""
Authentication routes for the Levy Calculation System.

This module provides routes for user authentication, including:
- User registration
- User login and logout
- Password management
- Profile management
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from models import User
from utils.auth_utils import (
    authenticate_user,
    create_user,
    update_user_password,
    update_user_profile,
    create_admin_user_if_none_exists
)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logger
logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page - we're already auto-authenticated
    logger.info("Login page accessed - redirecting to home (auto-authentication enabled)")
    flash('Welcome to Benton County Levy Calculator!', 'success')
    return redirect(url_for('index'))


@auth_bp.route('/logout')
def logout():
    """
    User logout route.
    
    Simply redirects to home page since we're keeping users auto-authenticated.
    """
    logger.info("Logout accessed - redirecting to home (auto-authentication enabled)")
    flash('You are now back at the home page', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page - we're already auto-authenticated
    logger.info("Registration page accessed - redirecting to home (auto-authentication enabled)")
    flash('Welcome to Benton County Levy Calculator!', 'success')
    return redirect(url_for('index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    User profile management route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page with appropriate message
    logger.info("Profile page accessed - redirecting to home (auto-authentication enabled)")
    flash('Benton County Staff Profile - No changes needed', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """
    Change password route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page with appropriate message
    logger.info("Change password page accessed - redirecting to home (auto-authentication enabled)")
    flash('No password change needed for Benton County shared access.', 'info')
    return redirect(url_for('index'))


# Note: We'll handle this in the init_auth_routes function instead
def setup_default_user():
    """
    Create default admin user if no users exist.
    """
    try:
        create_admin_user_if_none_exists()
    except Exception as e:
        logger.error(f"Error creating default admin user: {str(e)}")


def init_auth_routes(app):
    """
    Initialize authentication routes.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auth_bp)
    
    # Call setup directly - this will be executed when the app starts
    with app.app_context():
        setup_default_user()
    
    logger.info("Initialized authentication routes")