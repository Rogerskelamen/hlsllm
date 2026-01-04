#!/usr/bin/env bash
set -u

RESULT=result.txt
OUT=out
BUILD=build

for d in "$@"; do
    name=$(basename "$d")
    out_file="$OUT/$name.cpp"

    rm -rf "$BUILD"

    echo "==> Generate for $d"

    python3 src/main.py --algo_path "$d"

    if [ ! -f "$out_file" ]; then
        echo "$name [FAILED]" | tee -a "$RESULT"
    else
        echo "$name [PASS]" | tee -a "$RESULT"
    fi
done
