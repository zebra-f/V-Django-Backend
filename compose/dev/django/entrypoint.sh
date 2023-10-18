#!/bin/sh

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# exits if any of your variables is not set
set -o nounset

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

# python manage.py flush --no-input
python manage.py migrate

# a custom management command
python manage.py createuser --sentinel deleted

if [ "$MEILISEARCH_DISABLED" = "0" ]; then
    
    python manage.py createspeedsindex
    python manage.py updatespeedsindex
    
    echo "Meilisearch index was created and updated"
fi

redis_ready() {
python << END
import sys

import redis

try:
    r = redis.Redis(
        host="${REDIS_HOST}",
        port="${REDIS_PORT}"
    )
    r.ping()
except Exception as e:
    print(e)
    sys.exit(-1)
sys.exit(0)
END
}
until redis_ready; do
  >&2 echo 'Waiting for Redis to become available...'
  sleep 0.1
done

exec "$@"