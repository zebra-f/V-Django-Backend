#!/bin/bash

set -e

sudo docker compose down
sudo docker compose up --build -d

echo
echo "All containers should be up and running."
sudo docker ps -n 5

echo 
read -p "Would you like to inspect Django logs to check if everything is set up correctly [y/n]: " djangologs
djangologs_lowercase=$(echo "$djangologs" | tr '[:upper:]' '[:lower:]')
while [ $djangologs_lowercase = "y" ]; do
	logsout=$(sudo docker logs django-v-1-dev)
	echo "$logsout"

	last_logsout_line=$(echo "$logsout" | tail -n 1)
	if [ ! "$last_logsout_line" = "Quit the server with CONTROL-C." ]; then
		echo
		read -p "Try again, it seems like the container has not finished loading [y/n]: " djangologs
		djangologs_lowercase=$(echo "$djangologs" | tr '[:upper:]' '[:lower:]')
	else
		echo
		echo "Success, feel free to explore or work on this project."
		djangologs_lowercase="n"
	fi
done
