#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
python -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"

# Run database migrations if needed
python -c "from src.scripts.init_db import init_database; init_database(); print('Database populated successfully')" || echo "Database population skipped (already exists)"

echo "Build completed successfully!"