"""
WTTG2 Organizer - HTTP Routes
Blueprint for HTTP endpoints.
"""
import os
from flask import Blueprint, render_template, request

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@main_bp.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server"""
    print("Shutdown requested...")
    os._exit(0)
    return "Server shutting down...", 200
