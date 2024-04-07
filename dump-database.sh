#!/bin/bash

LOG_DIR="/var/log/database"
mkdir -p $LOG_DIR
LOG_FILE="${LOG_DIR}/pgdump.log"

if [ -f ./.env ]; then
	source ./.env
fi

# Warning: hardcoded postgres container name
docker exec -it postgres-v-1-dev pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME}
if [ $? -ne 0 ]; then
	echo "$(date), database is unhealthy." >> ${LOG_FILE}
	exit 1
fi

# Warning: hardcoded postgres container name
docker exec -it postgres-v-1-dev pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME} --format=tar -f /tmp/dump/database.tar
if [ $? -eq 0 ]; then 
	echo "$(date), pg_dump succeed." >> ${LOG_FILE}
else 
	echo "$(date), pg_dump failed." >> ${LOG_FILE}
	exit 2
fi
