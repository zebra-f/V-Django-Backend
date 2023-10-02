#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
else
    echo "Error: The DATABASE variable is not set to `postgres`"
    exit 1
fi

python manage.py flush --no-input
python manage.py migrate

if [ "$MEILISEARCH_DISABLED" = "0" ]; then
    
    python manage.py createspeedsindex
    python manage.py updatespeedsindex
    
    echo "Meilisearch index was created and updated"
fi

exec "$@"