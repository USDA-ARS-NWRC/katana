#!/bin/bash
set -e

run_katana='python3 /usr/local/bin/run_katana'

if [ $# -eq 0 ]; then
    umask 0002
    exec "/bin/bash"

elif [ "$1" = "test" ]; then
    echo "Run Katana docker test"
    cd /code/katana
    python3 -m pip install -r requirements_dev.txt
    coverage run --source katana setup.py test

    coverage report --fail-under=90
    coveralls
    exit 0

else
    echo "Running katana with"
    echo "$@"
    umask 0002
    exec $run_katana "$@"
fi
