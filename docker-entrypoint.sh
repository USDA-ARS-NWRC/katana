#!/bin/bash
set -e

run_katana='python3 /code/katana/scripts/run_katana'

if [ $# -eq 0 ]; then
    exec "/bin/bash"
else
    echo "Running katana with"
    echo "$@"
    exec $run_katana "$@"
fi
