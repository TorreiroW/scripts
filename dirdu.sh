#!/usr/bin/env bash
checkDir=${1:-.}
dirs=($(find "${checkDir}" -maxdepth 1 -mindepth 1 -type d))
for dir in "${dirs[@]}"; do
    if ! mountpoint -q "${dir}"; then
        du -xsm "${dir}" 2>/dev/null
    fi
done | sort -n
