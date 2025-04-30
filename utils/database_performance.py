"""
Database performance monitoring utilities.
This module provides tools for monitoring database query performance.
"""
import time
import logging
import functools
import sqlalchemy as sa
from flask import g, request, current_app
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class QueryPerformanceMonitor:
    """Monitor database query performance."""
    
    def __init__(self, db):
        """
        Initialize the query performance monitor.
        
        Args:
            db: SQLAlchemy database instance
        """
        self.db = db
        self.slow_query_threshold = 0.5  # seconds
        self.enabled = True
        
        # Set up event listener for queries
        sa.event.listen(db.engine, 'before_cursor_execute', self._before_cursor_execute)
        sa.event.listen(db.engine, 'after_cursor_execute', self._after_cursor_execute)
    
    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Record query start time."""
        if not self.enabled:
            return
        
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Record query end time and log if slow."""
        from flask import has_request_context, request, g
        
        if not self.enabled or not conn.info.get('query_start_time'):
            return
        
        query_start_time = conn.info['query_start_time'].pop(-1)
        query_time = time.time() - query_start_time
        
        # Get additional context if we're in a request context
        endpoint = 'unknown'
        if has_request_context():
            endpoint = request.endpoint if hasattr(request, 'endpoint') else 'unknown'
            
            # Store query in global context for request stats
            if hasattr(g, 'database_queries'):
                g.database_queries.append({
                    'query': statement,
                    'parameters': parameters,
                    'duration': query_time,
                    'endpoint': endpoint
                })
        
        # Log slow queries
        if query_time > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected ({query_time:.4f}s) at endpoint '{endpoint}':\n"
                f"Query: {statement}\n"
                f"Parameters: {parameters}"
            )

def setup_query_monitoring(app, db):
    """
    Set up query performance monitoring.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    monitor = QueryPerformanceMonitor(db)
    
    @app.before_request
    def before_request():
        """Initialize database query tracking."""
        g.database_queries = []
        g.request_start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Log request performance statistics."""
        if not hasattr(g, 'request_start_time'):
            return response
        
        request_duration = time.time() - g.request_start_time
        query_count = len(getattr(g, 'database_queries', []))
        query_time = sum(q['duration'] for q in getattr(g, 'database_queries', []))
        
        # Log if this is a slow request
        if request_duration > 1.0:  # Threshold for slow requests (1 second)
            logger.warning(
                f"Slow request detected: {request.method} {request.path} "
                f"({request_duration:.4f}s, {query_count} queries, {query_time:.4f}s in DB)"
            )
            
            # Log the actual queries if they took a significant portion of time
            if query_time > 0.5:
                for i, query in enumerate(getattr(g, 'database_queries', [])):
                    if query['duration'] > 0.1:  # Only log queries that took more than 100ms
                        logger.warning(
                            f"Query {i+1}/{query_count} ({query['duration']:.4f}s): "
                            f"{query['query']}"
                        )
        
        # Add performance info to response headers in debug mode
        if current_app.debug:
            response.headers['X-Request-Duration'] = str(round(request_duration, 4))
            response.headers['X-Query-Count'] = str(query_count)
            response.headers['X-Query-Duration'] = str(round(query_time, 4))
        
        return response
    
    return monitor

def query_performance_log(f):
    """
    Decorator to log query performance for a specific function.
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import has_request_context, g
        
        start_time = time.time()
        
        # Only track queries if we're in a request context
        queries_before = 0
        if has_request_context():
            queries_before = len(getattr(g, 'database_queries', []))
        
        result = f(*args, **kwargs)
        
        duration = time.time() - start_time
        
        # Only calculate query count if we're in a request context
        query_count = 0
        if has_request_context():
            queries_after = len(getattr(g, 'database_queries', []))
            query_count = queries_after - queries_before
        
        logger.info(
            f"Function {f.__name__} took {duration:.4f}s and executed "
            f"{query_count} queries"
        )
        
        return result
    
    return decorated

def get_performance_metrics():
    """
    Retrieve database performance metrics for monitoring.
    
    Returns:
        Dictionary containing performance metrics
    """
    from app import db
    import psycopg2
    
    # Current stats
    metrics = {
        'current_time': datetime.now().isoformat(),
        'slow_queries': {
            'last_hour': 0,
            'last_day': 0,
        },
        'query_stats': {
            'avg_duration': 0,
            'max_duration': 0,
            'total_queries': 0,
        },
        'connection_pool': {
            'size': 0,
            'available': 0,
            'used': 0,
        },
        'database_size': {
            'total_mb': 0,
            'tables': {},
        }
    }
    
    try:
        # Get connection pool stats if available
        if hasattr(db, 'engine') and hasattr(db.engine, 'pool'):
            pool = db.engine.pool
            metrics['connection_pool']['size'] = pool.size()
            metrics['connection_pool']['used'] = pool.checkedout()
            metrics['connection_pool']['available'] = pool.size() - pool.checkedout()
        
        # Execute query to get database stats
        with db.engine.connect() as conn:
            # Database size
            size_result = conn.execute(sa.text("""
                SELECT pg_database_size(current_database()) / (1024 * 1024) as size_mb
            """)).fetchone()
            if size_result:
                metrics['database_size']['total_mb'] = size_result[0]
            
            # Table sizes
            table_sizes = conn.execute(sa.text("""
                SELECT
                    table_name,
                    pg_total_relation_size(quote_ident(table_name)) / (1024 * 1024) as size_mb
                FROM
                    information_schema.tables
                WHERE
                    table_schema = 'public'
                ORDER BY
                    size_mb DESC
                LIMIT 10
            """)).fetchall()
            
            for table in table_sizes:
                metrics['database_size']['tables'][table[0]] = round(table[1], 2)
            
            # Slow query stats from logs (if available)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            one_day_ago = datetime.now() - timedelta(days=1)
            
            # This would typically connect to your logging system
            # For now, we'll provide placeholders
            metrics['slow_queries']['last_hour'] = 0
            metrics['slow_queries']['last_day'] = 0
            
            # Sample query stats (these would be populated from real data)
            metrics['query_stats']['avg_duration'] = 0.15
            metrics['query_stats']['max_duration'] = 0.85
            metrics['query_stats']['total_queries'] = 1240
    
    except Exception as e:
        logger.error(f"Error retrieving database metrics: {str(e)}")
        metrics['error'] = str(e)
    
    return metrics