#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
else
    >&2 echo "Error: The DATABASE variable is not set to `postgres`"
    exit 1
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

# django migrations
echo 'Sleeping for 12 seconds.'
sleep 20

exec "$@"
