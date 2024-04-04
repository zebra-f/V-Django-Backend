#!/bin/bash

set -e

if [ -d ./.venv ]; then
	echo "Project was already initialized."
	exit 1
fi

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
chmod +x ./start-project.sh

echo "Set environment variables specified in README.md and execute './start-project.sh local'"
