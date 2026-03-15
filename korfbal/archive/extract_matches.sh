#!/usr/bin/env bash

# Script to extract match schedule data from a local HTML file and save as CSV
# Usage: ./extract_matches.sh [team] [html_file]
# Example: ./extract_matches.sh "Dindoa J3" wouter.html
#          ./extract_matches.sh     # Extract all matches from wouter.html

# Get the team filter if provided
TEAM_FILTER="${1:-}"
HTML_FILE="${2:-wouter.html}"

# Check if the HTML file exists
if [[ ! -f "$HTML_FILE" ]]; then
    echo "Error: HTML file '$HTML_FILE' not found!" >&2
    echo "Usage: ./extract_matches.sh [team] [html_file]" >&2
    exit 1
fi

# Create a temporary file for processing
TMP_PROCESSED=$(mktemp)

# Process the HTML and extract the data
echo "Processing data from $HTML_FILE..."

# Output CSV header
echo "Date,Time,Home,Away,Location,Referee" > dindoa_matches.csv

# Display filter information if a team filter is provided
if [[ -n "$TEAM_FILTER" ]]; then
    echo "Filtering matches for team: $TEAM_FILTER" >&2
fi

echo "Extracting match data..." >&2

# Extract the content from the HTML file
grep -A 1000 '<div class="page-content table-responsive">' "$HTML_FILE" > "$TMP_PROCESSED"

# Process each date section
current_date=""
match_count=0

# Process the HTML file line by line
while IFS= read -r line; do
    # Extract date from h3 tags
    if [[ $line =~ \<h3\>([^<]+)\</h3\> ]]; then
        current_date="${BASH_REMATCH[1]}"
        current_date=$(echo "$current_date" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        echo "Processing date: $current_date" >&2
    fi
    
    # Look for table rows with our team
    if [[ $line =~ \<tr\> && ! $line =~ \<th && $current_date != "" ]]; then
        # Check if this row contains our team (either in home or away)
        if [[ -z "$TEAM_FILTER" || $line =~ $TEAM_FILTER ]]; then
            # Extract all td contents
            td_contents=()
            while read -r td_content; do
                # Remove td tags and clean up
                clean_content=$(echo "$td_content" | sed -E 's/<\/?td>//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                td_contents+=("$clean_content")
            done < <(echo "$line" | grep -o '<td>[^<]*</td>')
            
            # Check if we have enough fields and the first one is a time
            if [[ ${#td_contents[@]} -ge 4 && ${td_contents[0]} =~ ^[0-9]{1,2}:[0-9]{2}$ ]]; then
                time="${td_contents[0]}"
                home="${td_contents[1]}"
                away="${td_contents[2]}"
                location="${td_contents[3]}"
                referee="${td_contents[4]:-}"
                
                # Debug output
                echo "Found match: $time $home vs $away" >&2
                
                # Check if we need to filter by team
                if [[ -z "$TEAM_FILTER" || "$home" == "$TEAM_FILTER" || "$away" == "$TEAM_FILTER" ]]; then
                    # Escape quotes and commas for CSV
                    home=$(echo "$home" | sed 's/"/""/g')
                    away=$(echo "$away" | sed 's/"/""/g')
                    location=$(echo "$location" | sed 's/"/""/g')
                    referee=$(echo "$referee" | sed 's/"/""/g')
                    
                    # Write to CSV
                    echo "$current_date,$time,\"$home\",\"$away\",\"$location\",\"$referee\"" >> dindoa_matches.csv
                    echo "Added match: $time $home vs $away" >&2
                    ((match_count++))
                fi
            fi
        fi
    fi
done < "$TMP_PROCESSED"

# Clean up
rm "$TMP_PROCESSED"

echo "Done! Found $match_count matches. Data saved to dindoa_matches.csv"
