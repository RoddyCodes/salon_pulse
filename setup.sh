#!/bin/bash
# Salon Pulse - Quick Setup Script

echo "======================================"
echo "💅 Salon Pulse - Quick Setup"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Initialize database
echo "🗄️  Initializing database..."
python -m backend.models
echo "✅ Database initialized"

# Generate sample data
echo "📊 Generating practice dataset (90 days of appointments)..."
python scripts/seed_data.py

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  python run.py"
echo ""
echo "Then visit: http://127.0.0.1:5000"
echo ""
