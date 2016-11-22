web: python manage.py db upgrade && gunicorn -w 4 cal:app --log-file -
dev: python manage.py db upgrade && python manage.py runserver