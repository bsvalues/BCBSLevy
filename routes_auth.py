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
from sqlalchemy import desc

from app import db
from models import User, UserRole
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
    return redirect(url_for('home.index'))


@auth_bp.route('/logout')
def logout():
    """
    User logout route.
    
    Simply redirects to home page since we're keeping users auto-authenticated.
    """
    logger.info("Logout accessed - redirecting to home (auto-authentication enabled)")
    flash('You are now back at the home page', 'info')
    return redirect(url_for('home.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page - we're already auto-authenticated
    logger.info("Registration page accessed - redirecting to home (auto-authentication enabled)")
    flash('Welcome to Benton County Levy Calculator!', 'success')
    return redirect(url_for('home.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    User profile management route.
    
    Shows the user profile page with role information and permissions.
    """
    # Use our new template that shows roles
    logger.info(f"Profile page accessed by {current_user.username}")
    return render_template('auth/profile_with_roles.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """
    Change password route.
    
    Always redirects to home page since all users are auto-authenticated.
    """
    # Just redirect to home page with appropriate message
    logger.info("Change password page accessed - redirecting to home (auto-authentication enabled)")
    flash('No password change needed for Benton County shared access.', 'info')
    return redirect(url_for('home.index'))


@auth_bp.route('/manage-roles')
@login_required
def manage_roles():
    """
    Manage user roles.
    
    This route is accessible by admin users only and allows them to 
    assign or remove roles from users.
    """
    if not current_user.is_admin:
        flash('You do not have permission to manage roles.', 'danger')
        return redirect(url_for('home.index'))
    
    users = User.query.order_by(User.username).all()
    
    return render_template('auth/manage_roles.html', users=users)


@auth_bp.route('/add-role/<int:user_id>/<string:role>')
@login_required
def add_role(user_id, role):
    """
    Add a role to a user.
    
    This route is accessible by admin users only and allows them to
    assign a role to a user.
    
    Args:
        user_id: ID of the user to update
        role: Role to add (clerk, deputy, assessor)
    """
    if not current_user.is_admin:
        flash('You do not have permission to manage roles.', 'danger')
        return redirect(url_for('home.index'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if role is valid
        if role not in ['clerk', 'deputy', 'assessor']:
            flash(f'Invalid role: {role}', 'danger')
            return redirect(url_for('auth.manage_roles'))
        
        # Check if user already has this role
        if user.has_role(role):
            flash(f'User already has the {role} role.', 'warning')
            return redirect(url_for('auth.manage_roles'))
        
        # Add the role
        user_role = UserRole(user_id=user.id, role=role)
        db.session.add(user_role)
        db.session.commit()
        
        flash(f'Role {role} added to {user.username} successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding role: {str(e)}")
        flash(f'Error adding role: {str(e)}', 'danger')
    
    return redirect(url_for('auth.manage_roles'))


@auth_bp.route('/remove-role/<int:user_id>/<string:role>')
@login_required
def remove_role(user_id, role):
    """
    Remove a role from a user.
    
    This route is accessible by admin users only and allows them to
    remove a role from a user.
    
    Args:
        user_id: ID of the user to update
        role: Role to remove (clerk, deputy, assessor)
    """
    if not current_user.is_admin:
        flash('You do not have permission to manage roles.', 'danger')
        return redirect(url_for('home.index'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if role is valid
        if role not in ['clerk', 'deputy', 'assessor']:
            flash(f'Invalid role: {role}', 'danger')
            return redirect(url_for('auth.manage_roles'))
        
        # Find the role to remove
        user_role = UserRole.query.filter_by(
            user_id=user.id, 
            role=role
        ).first()
        
        if not user_role:
            flash(f'User does not have the {role} role.', 'warning')
            return redirect(url_for('auth.manage_roles'))
        
        # Remove the role
        db.session.delete(user_role)
        db.session.commit()
        
        flash(f'Role {role} removed from {user.username} successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing role: {str(e)}")
        flash(f'Error removing role: {str(e)}', 'danger')
    
    return redirect(url_for('auth.manage_roles'))


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