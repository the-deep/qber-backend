#! /bin/bash

# /code/deploy/ -> /code/
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR=$(dirname "$BASE_DIR")

cd $ROOT_DIR

# Start celery
celery -A main worker -Q CELERY-DEFAULT-QUEUE,CELERY-EXPORT-HEAVY-QUEUE -E --concurrency=2 -l info
