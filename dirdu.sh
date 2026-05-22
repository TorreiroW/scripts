#!/usr/bin/env bash
checkDir=.
excludes=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--exclude) excludes+=("$2"); shift 2 ;;
        *) checkDir=$1; shift ;;
    esac
done

dirs=($(find "${checkDir}" -maxdepth 1 -mindepth 1 -type d))

du_with_spinner() {
    local dir=$1 tmpfile
    tmpfile=$(mktemp)
    if command -v gum &>/dev/null; then
        gum spin --spinner dot --title "Checking ${dir}..." -- \
            bash -c 'du -xsm "$1" >"$2" 2>/dev/null' _ "$dir" "$tmpfile"
    else
        local frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' i=0
        du -xsm "$dir" >"$tmpfile" 2>/dev/null &
        local pid=$!
        while kill -0 "$pid" 2>/dev/null; do
            printf "\r%s Checking %s..." "${frames:$((i % ${#frames})):1}" "$dir" >&2
            sleep 0.1
            ((i++))
        done
        printf "\r%-*s\r" $((${#dir} + 15)) '' >&2
    fi
    cat "$tmpfile"
    rm -f "$tmpfile"
}

is_excluded() {
    local dir base
    base=$(basename "$1")
    for dir in "${excludes[@]}"; do
        [[ "$base" == "$dir" ]] && return 0
    done
    return 1
}

for dir in "${dirs[@]}"; do
    if ! mountpoint -q "$dir" 2>/dev/null && ! is_excluded "$dir"; then
        du_with_spinner "$dir"
    fi
done | sort -n
