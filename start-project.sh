#!/bin/bash

set -e

echo "Starting..."

if [ -z "$1" ]; then
	chmod +x ./compose/dev/django/entrypoint.sh
	chmod +x ./compose/dev/django/celery/entrypoint.sh
	chmod +x ./compose/dev/composeup.sh

	source ./compose/dev/composeup.sh

	exit 0
fi

if [[ "$1" != "local" ]]; then
	echo "Incorrect argument. Did you mean './start-project.sh local'?"
	exit 1
fi

required_vars=(\
	"DEBUG" "DJANGO_V_1_SECRET_KEY" "ALLOWED_HOSTS" "ADMIN_URL_SEGMENT" "CLIENT_BASE_URL" "ADMINS" "CORS_ALLOWED_ORIGINS" \
	"POSTGRES_V_1_PASSWORD" "POSTGRES_DB_NAME" "POSTGRES_HOST" "POSTGRES_PORT" "POSTGRES_USER" \
	"REDIS_URL" "REDIS_PORT" "REDIS_URL" \
	"MEILISEARCH_DISABLED" \
	"GOOGLE_OAUTH_DISABLED" \
	"CLOUDFLARE_TURNSTILE_DISABLED")

for var in "${required_vars[@]}"; do
	if [ -z "${!var}" ]; then
		echo "Error: $var is not set."
		exit 1
	fi
done

if [ $MEILISEARCH_DISABLED -eq "0" ]; then
	if [ -z "$MEILISEARCH_PORT" ] || [ -z "$MEILISEARCH_HOST" ] || [ -z "$MEILISEARCH_URL" ]; then
		echo "Make sure that MEILISEARCH_HOST, MEILISEARCH_PORT and MEILISEARCH_URL environment variables are set."
		exit 1
	fi
fi

if [ $GOOGLE_OAUTH_DISABLED -eq "0" ]; then
	if [ -z "$GOOGLE_OAUTH_CLIENT_SECRET" ] || [ -z "$FRONTEND_CALLBACK_URL" ]; then
		echo "Make sure that GOOGLE_OAUTH_CLIENT_SECRET and FRONTEND_CALLBACK_URL environment variables are set."
		exit 1
	fi
fi

if [ $CLOUDFLARE_TURNSTILE_DISABLED -eq "0" ] && [ -z $CLOUDFLARE_TURNSTILE_TOKEN ]; then
	echo "Make sure that CLOUDFLARE_TURNSTILE_TOKEN environment variable is set."
	exit 1
fi

echo "Waiting for postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
	sleep 0.1
done

python3 manage.py makemigrations
python3 manage.py migrate
 
python3 manage.py createuser --sentinel deleted

if [ $MEILISEARCH_DISABLED -eq "0" ]; then
	python manage.py createspeedsindex
	python manage.py updatespeedsindex
    
	echo "Meilisearch index was created and updated"
fi

read -p "Would you like to create a superuser [y/n]: " createsuperuser
createsuperuser_lowercase=$(echo "$createsuperuser" | tr '[:upper:]' '[:lower:]')
if [[ "$createsuperuser_lowercase" == "y" ]]; then
	echo "Starting the superuser creation process:"
	python3 manage.py createsuperuser
fi

python3 manage.py runserver
