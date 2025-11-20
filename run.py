#!/usr/bin/env python3
"""
Salon Pulse - Main Application Entry Point

This script starts the Flask web application.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import routes to register them with the app
from backend import routes

# Import the Flask app
from backend.models import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("💅 Starting Salon Pulse Application")
    print("=" * 50)
    print("📍 Access the app at: http://127.0.0.1:5000")
    print("🔧 Debug mode: ON")
    print("=" * 50 + "\n")

    app.run(debug=True, host="127.0.0.1", port=5000)
