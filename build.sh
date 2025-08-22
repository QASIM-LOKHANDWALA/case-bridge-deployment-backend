set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

if [[ $CREATE_SUPERUSER ]]; then
    python manage.py createsuperuser \
      --noinput \
      --email "$DJANGO_SUPERUSER_EMAIL" \
      --role admin
fi
