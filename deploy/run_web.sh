#! /bin/bash

# /code/deploy/ -> /code/
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR=$(dirname "$BASE_DIR")

cd $ROOT_DIR

echo '>> [Running] Django Collectstatic and Migrate'

./manage.py collectstatic --no-input
./manage.py migrate --no-input

uwsgi --ini ./deploy/uwsgi.ini # Start uwsgi server
