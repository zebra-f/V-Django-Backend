#!/bin/bash

# sudo -E ./sync-database.sh

log_dir="/var/log/database"
mkdir -p $log_dir
log_file="${log_dir}/s3sync.log"

if [ -f ./.env ]; then
	source ./.env
fi

which aws
if [[ $? -ne 0 ]]; then
	echo "$(date), aws cli is not installed." >> ${log_file}
fi

if [[ ! -f ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar.gpg ]]; then
	echo "$(date), file ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar.gpg doesn't exists." >> ${log_file}
	exit 1
fi

if [[ -z $S3_BUCKET_PATH ]]; then
	echo "$(date), bucket path is not set." >> ${log_file}
	exit 1
fi

if ! aws s3 ls s3://${S3_BUCKET_PATH} >/dev/null 2>&1; then
	echo "$(date), s3 bucket path ${S3_BUCKET_PATH} doesn't exists" >> ${log_file}
	exit 1
fi

output=$(aws s3 cp ${BIND_MOUNT_DATA_PATH}/postgres_data/dumps/database.tar.gpg s3://${S3_BUCKET_PATH} 2>&1)
if [ $? -eq 0 ]; then 
	echo "$(date), cp database.tar.gpg to s3 bucket succeed." | tee -a ${log_file}
else 
	echo "$(date), cp database.tar.gpg to s3 bucket failed. Output: ${output}" >> ${log_file}
	exit 1
fi
