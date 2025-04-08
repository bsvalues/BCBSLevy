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
    
    GET: Render login form
    POST: Process login request
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        remember_me = 'remember_me' in request.form
        
        if not username_or_email or not password:
            flash('Please provide both username/email and password', 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        success, result = authenticate_user(username_or_email, password)
        
        if success:
            # Log in user
            login_user(result, remember=remember_me)
            logger.info(f"User logged in: {result.username} (admin: {result.is_admin})")
            
            # Get the next page to redirect to
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            
            flash(f'Welcome back, {result.first_name or result.username}!', 'success')
            return redirect(next_page)
        else:
            flash(f'Login failed: {result}', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route.
    """
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    GET: Render registration form
    POST: Process registration request
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validate form data
        if not username or not email or not password:
            flash('Please fill in all required fields', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Create user
        success, result = create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if success:
            # Log in user
            login_user(result)
            logger.info(f"New user registered and logged in: {result.username}")
            flash('Registration successful! Welcome to the Levy Calculation System.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Registration failed: {result}', 'error')
    
    return render_template('auth/register.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile management route.
    
    GET: Render profile form
    POST: Process profile update request
    """
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Update profile
        success, result = update_user_profile(
            user_id=current_user.id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        if success:
            flash('Profile updated successfully', 'success')
        else:
            flash(f'Failed to update profile: {result}', 'error')
    
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password route.
    
    GET: Render change password form
    POST: Process password change request
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        success, message = update_user_password(
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
        
        if success:
            flash('Password changed successfully. Please log in with your new password.', 'success')
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash(f'Failed to change password: {message}', 'error')
    
    return render_template('auth/change_password.html')


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