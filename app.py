"""
Flask application initialization and configuration.

This module initializes the Flask application, configures extensions,
and sets up database connections and other necessary components.
"""

import os
import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
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
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
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
    app.logger.info('Levy Calculation System startup')


# Create the Flask application instance
app = create_app()

# Root route with welcome page
@app.route('/')
def index():
    """Render welcome page with stunning landing page design"""
    return render_template('index.html')


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
from routes_tours import tours_bp, register_routes as register_tour_routes
from routes_historical_analysis import historical_analysis_bp, init_historical_analysis_routes
from routes_mcp import mcp_bp, init_mcp_routes
from routes_advanced_mcp import advanced_mcp_bp
from routes_examples import examples_bp
from routes_budget_impact import budget_impact_bp
from routes_reports_new import init_report_routes
from routes_levy_audit import levy_audit_bp, register_levy_audit_routes
from routes_user_audit import user_audit_bp, register_user_audit_routes
from routes_tax_strategy import tax_strategy_bp, register_tax_strategy_routes

app.register_blueprint(data_management_bp)
app.register_blueprint(forecasting_bp)
app.register_blueprint(levy_exports_bp)
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(glossary_bp)
app.register_blueprint(dashboard_bp)
# Note: levy_calculator_bp is registered via register_levy_calculator_routes
app.register_blueprint(tours_bp)
# Note: historical_analysis_bp is registered via init_historical_analysis_routes
# Note: mcp_bp is registered via init_mcp_routes
app.register_blueprint(advanced_mcp_bp)
app.register_blueprint(examples_bp)
app.register_blueprint(budget_impact_bp)
# Note: levy_audit_bp is registered via register_levy_audit_routes
# Note: user_audit_bp is registered via register_user_audit_routes

# Initialize authentication routes
init_auth_routes(app)

# Initialize tour routes
register_tour_routes(app)

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

# Import models after db is defined to avoid circular imports
with app.app_context():
    # Initialize MCP API endpoints within application context
    try:
        from utils.mcp_integration import init_mcp_api_routes, init_mcp
        init_mcp()
        init_mcp_api_routes(app)
        app.logger.info("MCP framework initialized")
        
        # Initialize Advanced AI Agent
        try:
            from utils.advanced_ai_agent import init_advanced_agent
            init_advanced_agent()
            app.logger.info("Advanced Analysis Agent initialized")
        except Exception as e:
            app.logger.error(f"Error initializing Advanced Analysis Agent: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error initializing MCP framework: {str(e)}")
    # Create tables if they don't exist
    try:
        from models import User, TaxDistrict, TaxCode, Property, ImportLog, ExportLog
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")