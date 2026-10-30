#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Esta línea crea el superusuario sin preguntar nada (usando variables de entorno)
python manage.py createsuperuser --no-input