#!/usr/bin/env bash
checkDir=${1:-.}
dirs=($(find "${checkDir}" -maxdepth 1 -mindepth 1 -type d))

du_with_spinner() {
    local dir=$1
    if command -v gum &>/dev/null; then
        gum spin --spinner dot --title "Checking ${dir}..." -- du -xsm "$dir" 2>/dev/null
    else
        local tmpfile frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' i=0
        tmpfile=$(mktemp)
        du -xsm "$dir" >"$tmpfile" 2>/dev/null &
        local pid=$!
        while kill -0 "$pid" 2>/dev/null; do
            printf "\r%s Checking %s..." "${frames:$((i % ${#frames})):1}" "$dir" >&2
            sleep 0.1
            ((i++))
        done
        printf "\r%-*s\r" $((${#dir} + 15)) '' >&2
        cat "$tmpfile"
        rm -f "$tmpfile"
    fi
}

results=()
for dir in "${dirs[@]}"; do
    if ! mountpoint -q "$dir" 2>/dev/null; then
        results+=("$(du_with_spinner "$dir")")
    fi
done

printf '%s\n' "${results[@]}" | sort -n
