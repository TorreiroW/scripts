#!/usr/bin/env bash
checkDir=${1:-.}
dirs=($(find "${checkDir}" -maxdepth 1 -mindepth 1 -type d))

result=$(gum spin --spinner dot --title "Calculating disk usage in ${checkDir}..." -- \
    bash -c '
        for dir in "$@"; do
            if ! mountpoint -q "$dir" 2>/dev/null; then
                du -xsm "$dir" 2>/dev/null
            fi
        done
    ' _ "${dirs[@]}")

echo "$result" | sort -n
