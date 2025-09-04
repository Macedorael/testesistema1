#!/usr/bin/env bash
# exit on error
set -o errexit

# Force Python environment
echo "Setting up Python environment..."
export PATH="/opt/render/project/src/.venv/bin:$PATH"
echo "PATH: $PATH"

# Ensure we're using Python 3
echo "Checking Python installation..."
which python3 || echo "python3 not found"
/opt/render/project/src/.venv/bin/python3 --version || python3 --version || echo "python3 version check failed"

# Install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Verify gunicorn installation
echo "Checking Gunicorn installation..."
which gunicorn || echo "Gunicorn not found in PATH"
python3 -m pip show gunicorn || echo "Gunicorn not installed"

# Try to install gunicorn explicitly if not found
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Gunicorn explicitly..."
    python3 -m pip install gunicorn==21.2.0
fi

# Verify gunicorn is working and show path
echo "Final Gunicorn check:"
which gunicorn || echo "Gunicorn not found in PATH"
gunicorn --version || echo "Gunicorn version check failed"
echo "PATH: $PATH"
echo "Expected start command: gunicorn --bind 0.0.0.0:\$PORT wsgi:app"

# Initialize database
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"

# Run database migrations if needed
python3 -c "import sys; sys.path.append('.'); from scripts.init_db import init_database; init_database(); print('Database populated successfully')" || echo "Database population skipped (already exists)"

# Create activation script for runtime
echo '#!/bin/bash' > activate_env.sh
echo 'export PATH="/opt/render/project/src/.venv/bin:$PATH"' >> activate_env.sh
echo 'exec "$@"' >> activate_env.sh
chmod +x activate_env.sh

echo "Build completed successfully!"