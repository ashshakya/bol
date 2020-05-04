#!/bin/bash

# Makemigration
# echo Starting Makemigration.
# python3 manage.py makemigrations

# Migrate
echo Starting Migration.
python3 manage.py migrate

# Create superuser
# echo Creating superuser.
# python3 manage.py createsuperuser

# Collect static files
echo Collecting static files.
python3 manage.py collectstatic --no-input

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn boloo.wsgi:application \
    --bind 0.0.0.0:26000 \
    --workers 5