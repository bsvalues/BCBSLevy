"""
PRIMARY APPLICATION ENTRY POINT: Flask application initialization and configuration.

This module initializes the Flask application, configures extensions,
sets up database connections, and registers all blueprints. This is the
main entry point for the LevyMaster application and the authoritative
source for all application components.

All blueprints and routes should be registered here to maintain a
consistent application structure. This file supersedes the older app2.py
approach in favor of a more standardized architecture.
"""

import os
import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name: The configuration to use (development, testing, production)
        
    Returns:
        The configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Configure the application
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Override config from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # Configure database connection pooling
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Initialize extensions with the app
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Set up mock authentication for all users (no login required)
    # This gives all users automatic admin access without login
    from flask_login import AnonymousUserMixin
    
    class AutoAuthUser(AnonymousUserMixin):
        """User class that automatically grants admin privileges to everyone."""
        @property
        def is_authenticated(self):
            return True
            
        @property
        def is_active(self):
            return True
            
        @property
        def is_admin(self):
            return True
            
        @property
        def id(self):
            return 1
            
        @property
        def username(self):
            return "BentonStaff"
            
        @property
        def first_name(self):
            return "Benton County"
            
        @property
        def last_name(self):
            return "Staff"
    
    # Initialize login manager with auto auth
    login_manager.init_app(app)
    login_manager.anonymous_user = AutoAuthUser
    
    # Override login_required decorator to do nothing - this bypasses all @login_required decorators
    def no_login_required(func):
        return func
        
    # Replace the actual login_required with our no-op version
    import flask_login
    flask_login.login_required = no_login_required
    
    @login_manager.user_loader
    def load_user(user_id):
        # Always return our auto-authenticated user
        return AutoAuthUser()
    
    # Register CLI commands
    try:
        from cli import register_commands
        register_commands(app)
    except ImportError:
        app.logger.warning("CLI commands not registered, cli.py not found")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register template context processors
    @app.context_processor
    def inject_current_year():
        """Add current_year to all templates."""
        return {'current_year': datetime.now().year}
    
    # Configure logging
    configure_logging(app)
    
    return app


def register_error_handlers(app):
    """
    Register custom error handlers for the application.
    
    Args:
        app: The Flask application instance
    """
    @app.errorhandler(404)
    def page_not_found(error):
        if request.path.startswith('/api/'):
            return jsonify(error="Not found"), 404
        return render_template('simple_404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        if request.path.startswith('/api/'):
            return jsonify(error="Internal server error"), 500
        return render_template('simple_404.html', 
                              error_code=500, 
                              error_title="Internal Server Error",
                              error_message="The server encountered an error processing your request."), 500


def register_template_filters(app):
    """
    Register custom template filters for Jinja templates.
    
    Args:
        app: The Flask application instance
    """
    @app.template_filter('format_currency')
    def format_currency(value):
        """Format a value as currency with $ sign and commas."""
        if value is None:
            return "$0.00"
        return "${:,.2f}".format(value)
    
    @app.template_filter('format_percent')
    def format_percent(value):
        """Format a value as a percentage."""
        if value is None:
            return "0.00%"
        return "{:.2f}%".format(value * 100)
    
    @app.template_filter('format_date')
    def format_date(value):
        """Format a date value."""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return value
        return value.strftime("%m/%d/%Y")

    @app.template_filter('format_number')
    def format_number(value):
        """Format a number with commas as thousands separators."""
        if value is None:
            return "0"
        return "{:,}".format(int(value))
        
    @app.template_filter('add_tooltips')
    def add_tooltips(value):
        """Add tooltip highlighting to text."""
        return f'<span class="tooltip-text" data-toggle="tooltip" title="{value}">{value}</span>'
        
    @app.template_filter('datetime')
    def format_datetime(value):
        """Format a datetime value."""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    return value
        return value.strftime("%m/%d/%Y %H:%M")


def configure_logging(app):
    """
    Configure logging for the application.
    
    Args:
        app: The Flask application instance
    """
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    
    # Configure basic logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    app.logger.setLevel(log_level)
    app.logger.info('LevyMaster application startup')


# Create the Flask application instance
app = create_app()

# Root route is now handled by home_bp


# Register blueprints
from routes_data_management import data_management_bp
from routes_forecasting import forecasting_bp
from routes_levy_exports import levy_exports_bp
from routes_public import public_bp
from routes_admin import admin_bp
from routes_glossary import glossary_bp
from routes_auth import auth_bp, init_auth_routes
from routes_dashboard import dashboard_bp, register_dashboard_routes
from routes_levy_calculator import levy_calculator_bp, register_levy_calculator_routes
from routes_historical_analysis import historical_analysis_bp, init_historical_analysis_routes
from routes_mcp import mcp_bp, init_mcp_routes
from routes_advanced_mcp import advanced_mcp_bp
from routes_examples import examples_bp
from routes_budget_impact import budget_impact_bp
from routes_reports_new import init_report_routes
from routes_home import home_bp, init_home_routes
from routes_levy_audit import levy_audit_bp, register_levy_audit_routes
from routes_user_audit import user_audit_bp, register_user_audit_routes
from routes_tax_strategy import tax_strategy_bp, register_tax_strategy_routes
from routes_search import init_search_routes
from routes_db_fix import db_fix_bp
from routes_property_assessment import property_assessment_bp
from routes_mcp_ui import register_mcp_ui_routes

app.register_blueprint(data_management_bp)
app.register_blueprint(property_assessment_bp)
app.register_blueprint(forecasting_bp)
app.register_blueprint(levy_exports_bp)
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(glossary_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(db_fix_bp)
# Note: levy_calculator_bp is registered via register_levy_calculator_routes
# Note: historical_analysis_bp is registered via init_historical_analysis_routes
# Note: mcp_bp is registered via init_mcp_routes
app.register_blueprint(advanced_mcp_bp)
app.register_blueprint(examples_bp)
app.register_blueprint(budget_impact_bp)

# Register direct MCP Army dashboard route
from mcp_army_route import register_direct_routes
register_direct_routes(app)
app.logger.info("Direct MCP Army dashboard route registered")
# Note: levy_audit_bp is registered via register_levy_audit_routes
# Note: user_audit_bp is registered via register_user_audit_routes

# Initialize authentication routes
init_auth_routes(app)

# Initialize levy calculator routes
register_levy_calculator_routes(app)

# Initialize historical analysis routes
init_historical_analysis_routes(app)

# Initialize MCP routes
init_mcp_routes(app)

# Initialize report routes
init_report_routes(app)

# Initialize levy audit routes
register_levy_audit_routes(app)

# Initialize user audit routes
register_user_audit_routes(app)

# Initialize tax strategy routes
register_tax_strategy_routes(app)

# Initialize search routes
init_search_routes(app)
app.logger.info("Search routes initialized")

# Initialize home routes
init_home_routes(app)
app.logger.info("Home routes initialized")

# Initialize data quality routes
try:
    from routes_data_quality import init_app as init_data_quality_routes
    init_data_quality_routes(app)
    app.logger.info("Data quality routes initialized")
except ImportError as e:
    app.logger.warning(f"Could not import data quality routes: {str(e)}")
except Exception as e:
    app.logger.error(f"Error initializing data quality routes: {str(e)}")

# Register MCP UI routes
try:
    register_mcp_ui_routes(app)
    app.logger.info("MCP UI routes registered")
except Exception as e:
    app.logger.error(f"Error registering MCP UI routes: {str(e)}")

# Import models after db is defined to avoid circular imports
with app.app_context():
    # Import dependencies for MCP and AI functionalities
    from utils.mcp_integration import init_mcp_api_routes, init_mcp
    from utils.advanced_ai_agent import init_advanced_agent
    from utils.mcp_army_init import init_mcp_army
    from utils.anthropic_utils import check_api_key_status
    
    # Check Anthropic API key status before attempting to initialize AI components
    api_status = check_api_key_status()
    if api_status['status'] != 'valid':
        app.logger.warning(f"Anthropic API key issue: {api_status['message']}")
        app.logger.warning("AI-powered features will be limited or unavailable")
    
    # Initialize MCP framework with improved error handling
    try:
        init_mcp()
        app.logger.info("MCP framework initialized")
    except ImportError as e:
        app.logger.error(f"Error importing MCP dependencies: {str(e)}")
        app.logger.error("MCP framework initialization failed - module import error")
    except Exception as e:
        app.logger.error(f"Error initializing MCP framework: {str(e)}")
        app.logger.error("MCP framework initialization failed - basic features will still be available")
    
    # Register MCP API routes even if initialization failed (endpoints will handle errors)
    try:
        init_mcp_api_routes(app)
    except Exception as e:
        app.logger.error(f"Error registering MCP API routes: {str(e)}")
    
    
    # Initialize MCP Army system with dedicated error handling
    try:
        if api_status['status'] == 'valid':
            # Import here to avoid circular imports
            from routes_mcp_army import register_mcp_army_routes
            
            # Initialize MCP Army system
            mcp_army_initialized = init_mcp_army(app)
            
            # Register MCP Army routes
            routes_registered = register_mcp_army_routes(app)
            
            if mcp_army_initialized and routes_registered:
                app.logger.info("MCP Army system initialized and routes registered successfully")
            elif mcp_army_initialized:
                app.logger.warning("MCP Army system initialized but routes registration failed")
            else:
                app.logger.warning("MCP Army system initialization failed")
        else:
            app.logger.warning("Skipping MCP Army initialization due to API key issues")
    except ImportError as e:
        app.logger.error(f"Error importing MCP Army dependencies: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error initializing MCP Army system: {str(e)}")
        app.logger.error("MCP Army features will be unavailable")
        
    # Initialize Advanced AI Agent with dedicated error handling
    try:
        if api_status['status'] == 'valid':
            init_advanced_agent()
            app.logger.info("Advanced Analysis Agent initialized and registered")
        else:
            app.logger.warning("Skipping Advanced Analysis Agent initialization due to API key issues")
    except ImportError as e:
        app.logger.error(f"Error importing Advanced AI Agent dependencies: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error initializing Advanced Analysis Agent: {str(e)}")
        app.logger.error("Advanced AI features will be unavailable")
    
    # Create tables if they don't exist
    try:
        from models import User, TaxDistrict, TaxCode, Property, ImportLog, ExportLog
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")