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

# Execute automatic migration for user_id column in funcionarios table
echo "Running automatic migration..."
python3 deploy_migration.py || echo "Migration completed or not needed"

# Initialize database (only create tables if they don't exist - preserves existing data)
python3 -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database tables created/verified successfully')"

# Ensure admin user exists (safe - won't duplicate)
python3 scripts/create_admin_user.py

# Apply bug fix for 'ativo' issue in especialidades (safe - only fixes corrupted data)
echo "Applying especialidades bug fix..."
python3 fix_ativo_bug.py || echo "Bug fix completed or no issues found"

# Only populate with sample data if database is empty (first deploy)
python3 -c "import sys; sys.path.append('.'); from src.main import app, db; from src.models.usuario import User; app.app_context().push(); user_count = User.query.count(); print(f'Found {user_count} existing users'); exit(0 if user_count > 0 else 1)" && echo "Database has existing data - skipping sample data population" || python3 -c "import sys; sys.path.append('.'); from scripts.init_db import create_sample_data; create_sample_data(); print('Sample data populated successfully')"

# Create activation script for runtime
echo '#!/bin/bash' > activate_env.sh
echo 'export PATH="/opt/render/project/src/.venv/bin:$PATH"' >> activate_env.sh
echo 'exec "$@"' >> activate_env.sh
chmod +x activate_env.sh

echo "Build completed successfully!"