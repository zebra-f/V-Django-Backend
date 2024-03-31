#!/bin/bash

set -e

echo "start"
if [ -z "$1" ]; then
	echo "not set"
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
		echo "Error: $var is not set"
		exit 1
	fi
done


echo "Waiting for postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
	sleep 0.1
done

python3 manage.py makemigrations
python3 manage.py migrate
 
python manage.py createuser --sentinel deleted

read -p "Would you like to create a superuser [y/n]: " createsuperuser
createsuperuser_lowercase=$(echo "$createsuperuser" | tr '[:upper:]' '[:lower:]')
if [[ "$createsuperuser_lowercase" == "y" ]]; then
	echo "Starting the superuser creation process:"
	python3 manage.py createsuperuser
fi


# export MEILISEARCH_HOST="meilisearch"
# export MEILISEARCH_PORT="7700"
# export MEILISEARCH_URL="http://meilisearch:7700"
# export MEILISEARCH_DISABLED="1"
# 
# export GOOGLE_OAUTH_DISABLED="1"
# # set if not GOOGLE_OAUTH_DISABLED
# export GOOGLE_OAUTH_CLIENT_SECRET=""
# export FRONTEND_CALLBACK_URL=""
# 
# export CLOUDFLARE_TURNSTILE_DISABLED="1"
# # set if not CLOUDFLARE_TURNSTILE_DISABLED
# export CLOUDFLARE_TURNSTILE_TOKEN=""


	


