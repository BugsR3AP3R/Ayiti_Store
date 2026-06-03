#!/usr/bin/env bash
# Render build script

set -o errexit  # Arrêter si une commande échoue

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
