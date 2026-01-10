#!/bin/bash

echo "🚀 Setting up ŠtúdujSmart.sk development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create PostgreSQL database
echo "Creating database..."
createdb studujsmart 2>/dev/null || echo "Database already exists"

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env file - please edit with your credentials"
fi

# Initialize database migrations
flask db init 2>/dev/null || echo "Migrations already initialized"
flask db migrate -m "Initial migration"
flask db upgrade

# Seed database
python seed_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "The app will be available at http://localhost:5000"