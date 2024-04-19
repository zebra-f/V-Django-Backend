#!/bin/bash

# This script performs a specific task related to a PostgreSQL container.
# It takes two arguments:
#   1. Postgres container name: The name of the PostgreSQL container to perform the task on.
#   2. encrypt (optional): If provided, enables encryption during the task execution.
#
# Usage:
# sudo ./dump-database.sh <postgres_container_name> [encrypt]

LOG_DIR="/var/log/database"
mkdir -p $LOG_DIR
LOG_FILE="${LOG_DIR}/pgdump.log"

if [ -f ./.env ]; then
	source ./.env
fi

if [ -z "${1}" ] || [[ "${1}" = "encrypt" ]]; then
	echo "$(date), container name was not provided." | tee -a ${LOG_FILE}
	exit 1
fi
CONTAINER_NAME="${1}"

timeout 12s docker exec ${CONTAINER_NAME} pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME}
exit_code=$?
if [ $exit_code -eq 124 ]; then
	echo "$(date), pg_isready timed out." >> ${LOG_FILE}
	exit $exit_code
fi
if [ $exit_code -ne 0 ]; then
	echo "$(date), pg_isready, database is unhealthy." >> ${LOG_FILE}
	exit $exit_code
fi

timeout 20m docker exec ${CONTAINER_NAME} pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB_NAME} --format=tar -f /tmp/dumps/database.tar
exit_code=$?
if [ $exit_code -eq 124 ]; then
	echo "$(date), pg_dump timed out." >> ${LOG_FILE}
	exit $exit_code
fi
if [ $exit_code -eq 0 ]; then 
	echo "$(date), pg_dump succeed." | tee -a ${LOG_FILE}
else 
	echo "$(date), pg_dump failed." >> ${LOG_FILE}
	exit $exit_code
fi

# Exit if no arguments are provided
if [ -z "$2" ]; then
	exit 0
fi 

if [[ "$2" != "encrypt" ]]; then
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
	echo "$(date), encryption succeed." | tee -a ${LOG_FILE}
else 
	echo "$(date), encryption failed." >> ${LOG_FILE}
	exit $exit_code
fi

