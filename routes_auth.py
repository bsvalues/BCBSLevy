"""
Authentication routes for the Levy Calculation System.

This module provides routes for user authentication, including:
- User registration
- User login and logout
- Password management
- Profile management
- Role-based access control
"""

import logging
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc

from app import db
from models import User, UserRole, UserActionLog
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


@auth_bp.route('/update-role', methods=['POST'])
@login_required
def update_role():
    """
    Update a user's role via AJAX.
    
    This route is accessible by admin users only and allows them to
    assign or remove roles from users via AJAX.
    
    Expected JSON payload:
    {
        "user_id": 123,
        "role": "clerk",
        "has_role": true
    }
    """
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'message': 'Permission denied. Admin access required.'
        }), 403
    
    # Parse JSON request data
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        role = data.get('role')
        has_role = data.get('has_role', False)
        
        # Validate the role
        if role not in ['clerk', 'deputy', 'assessor']:
            return jsonify({
                'success': False,
                'message': f'Invalid role: {role}'
            }), 400
        
        # Get the user
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': f'User with ID {user_id} not found'
            }), 404
        
        # Check if user is trying to modify their own roles
        if user_id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'You cannot modify your own roles'
            }), 403
        
        # Update the role
        if has_role:
            # Add role if the user doesn't have it
            if not user.has_role(role):
                user_role = UserRole(user_id=user.id, role=role)
                db.session.add(user_role)
                
                # Log the action
                log = UserActionLog(
                    user_id=current_user.id,
                    action_type='ROLE_ASSIGNMENT',
                    module='auth',
                    submodule='role_management',
                    entity_type='user',
                    entity_id=user.id,
                    action_details={
                        'role_added': role,
                        'target_user': user.username
                    }
                )
                db.session.add(log)
                
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Role {role} added to {user.username}'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'User already has the {role} role'
                })
        else:
            # Remove role if the user has it
            user_role = UserRole.query.filter_by(user_id=user.id, role=role).first()
            if user_role:
                db.session.delete(user_role)
                
                # Log the action
                log = UserActionLog(
                    user_id=current_user.id,
                    action_type='ROLE_REMOVAL',
                    module='auth',
                    submodule='role_management',
                    entity_type='user',
                    entity_id=user.id,
                    action_details={
                        'role_removed': role,
                        'target_user': user.username
                    }
                )
                db.session.add(log)
                
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Role {role} removed from {user.username}'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'User does not have the {role} role'
                })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating role: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating role: {str(e)}'
        }), 500


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