#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Automatically create a superuser using environment variables,
# if one doesn't already exist. Safe to run on every deploy.
python manage.py createsuperuser --no-input || true