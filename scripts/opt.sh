#!/usr/bin/env bash
set -u

OUT=out
BUILD=build

for d in "$@"; do
    name=$(basename "$d")
    output_dir="$OUT/$name"
    mkdir -p "$output_dir"

    rm -rf "$BUILD"

    echo "==> Optimize for $d"

    python3 src/main.py --type opt --algo_path "$d"

    cp -r "$BUILD"/. "$output_dir"/
done
