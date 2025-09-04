#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify gunicorn installation
echo "Checking Gunicorn installation..."
which gunicorn || echo "Gunicorn not found in PATH"
pip show gunicorn || echo "Gunicorn not installed"

# Try to install gunicorn explicitly if not found
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn explicitly..."
    pip install gunicorn==21.2.0
fi

# Initialize database
python -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"

# Run database migrations if needed
python -c "import sys; sys.path.append('.'); from scripts.init_db import init_database; init_database(); print('Database populated successfully')" || echo "Database population skipped (already exists)"

echo "Build completed successfully!"