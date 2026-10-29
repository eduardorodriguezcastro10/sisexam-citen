#!/usr/bin/env bash
# Sale si hay un error
set -o errexit

# Instala las librerías
pip install -r requirements.txt

# Recolecta los archivos estáticos (CSS, imágenes)
python manage.py collectstatic --no-input

# Crea las tablas en la base de datos de Render
python manage.py migrate