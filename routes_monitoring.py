
from flask import Blueprint, jsonify
from utils.database_performance import get_performance_metrics
from utils.mcp_agent_manager import get_agent_metrics

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/metrics/agents')
def agent_metrics():
    return jsonify(get_agent_metrics())

@monitoring_bp.route('/metrics/database')
def database_metrics():
    return jsonify(get_performance_metrics())

@monitoring_bp.route('/metrics')
def all_metrics():
    return jsonify({
        'agents': get_agent_metrics(),
        'database': get_performance_metrics()
    })
