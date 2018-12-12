#!/bin/bash
set -e

run_katana='python3 /code/katana/scripts/run_katana'

if [ $# -eq 0 ]; then
    umask 0002
    exec "/bin/bash"
else
    echo "Running katana with"
    echo "$@"
    umask 0002
    exec $run_katana "$@"
fi
