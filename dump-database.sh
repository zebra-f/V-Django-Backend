#!/bin/bash

LOG_DIR="/var/log/database"
mkdir -p $LOG_DIR
LOG_FILE="${LOG_DIR}/pgdump.log"

if [ -f ./.env ]; then
	source ./.env
fi

# Warning: hardcoded postgres container name
timeout 10s docker exec postgres-v-1-dev pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME}
exit_code=$?
if [ $exit_code -eq 124 ]; then
	echo "$(date), pg_isready timed out." >> ${LOG_FILE}
	exit $exit_code
fi
if [ $exit_code -ne 0 ]; then
	echo "$(date), pg_isready, database is unhealthy." >> ${LOG_FILE}
	exit $exit_code
fi

# Warning: hardcoded postgres container name
timeout 20m docker exec postgres-v-1-dev pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME} --format=tar -f /tmp/dumps/database.tar
exit_code=$?
if [ $exit_code -eq 124 ]; then
	echo "$(date), pg_dump timed out." >> ${LOG_FILE}
	exit $exit_code
fi
if [ $exit_code -eq 0 ]; then 
	echo "$(date), pg_dump succeed." >> ${LOG_FILE}
else 
	echo "$(date), pg_dump failed." >> ${LOG_FILE}
	exit $exit_code
fi

# Exit if no arguments are provided
if [ -z "$1" ]; then
	exit 0
fi 

if [[ "$1" != "encrypt" ]]; then
	echo "Incorrect argument. Did you mean './dump-database.sh encrypt'?"
	exit 1
fi

if [[ ! -d ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps ]]; then
	echo "$(date), dir ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps doesn't exists." >> ${LOG_FILE}
	exit 1
fi

if [[ ! -f ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar ]]; then
	echo "$(date), file ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar doesn't exists." >> ${LOG_FILE}
	exit 1
fi

if [[ -z $GPG_DATABASE_DUMP_PASSPHRASE ]]; then
	echo "$(date), encryption passphrase is not set." >> ${LOG_FILE}
	exit 1
fi

echo $GPG_DATABASE_DUMP_PASSPHRASE | gpg --batch --yes -c --passphrase-fd 0 \
	-o ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar.gpg \
	${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar
exit_code=$?
if [ $exit_code -eq 0 ]; then 
	echo "$(date), encryption succeed." >> ${LOG_FILE}
else 
	echo "$(date), encryption failed." >> ${LOG_FILE}
	exit $exit_code
fi

