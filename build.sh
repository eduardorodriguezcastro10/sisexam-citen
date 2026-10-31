#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# El "|| true" hace que si el usuario ya existe, no detenga el despliegue
python manage.py createsuperuser --no-input || true