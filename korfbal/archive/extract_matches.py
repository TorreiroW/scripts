#!/usr/bin/env python3

import sys
import csv
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

def extract_matches(html_file, team_filter=None):
    """
    Extract match data from HTML file and filter by team if specified
    
    Args:
        html_file (str): Path to HTML file
        team_filter (str, optional): Team name to filter matches
        
    Returns:
        list: List of dictionaries containing match data
    """
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables with match data
    matches = []
    current_date = None
    
    # Find the div with class "page-content table-responsive"
    content_div = soup.find('div', class_='page-content table-responsive')
    if not content_div:
        print("Error: Could not find match data in HTML file")
        return matches
    
    # Process each h3 (date) and the table that follows it
    for element in content_div.children:
        if element.name == 'h3':
            current_date = element.text.strip()
            print(f"Processing date: {current_date}")
        
        elif element.name == 'table' and current_date:
            # Process table rows
            rows = element.find_all('tr')
            
            # Skip header row
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    time = cells[0].text.strip()
                    home = cells[1].text.strip()
                    away = cells[2].text.strip()
                    location = cells[3].text.strip()
                    referee = cells[4].text.strip() if len(cells) > 4 else ""
                    
                    # Check if this match involves the team we're looking for
                    if not team_filter or team_filter in home or team_filter in away:
                        match = {
                            'Date': current_date,
                            'Time': time,
                            'Home': home,
                            'Away': away,
                            'Location': location,
                            'Referee': referee
                        }
                        matches.append(match)
                        print(f"Found match: {time} {home} vs {away}")
    
    return matches

def save_to_csv(matches, output_file='dindoa_matches.csv'):
    """Save matches to CSV file"""
    if not matches:
        print("No matches found")
        # Create empty CSV with headers
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Time', 'Home', 'Away', 'Location', 'Referee'])
        return
    
    # Write matches to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Date', 'Time', 'Home', 'Away', 'Location', 'Referee']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)
    
    print(f"Done! Found {len(matches)} matches. Data saved to {output_file}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract match data from HTML file')
    parser.add_argument('team', nargs='?', default=None, help='Team name to filter matches')
    parser.add_argument('html_file', nargs='?', default='wouter.html', help='HTML file to parse')
    args = parser.parse_args()
    
    # Check if HTML file exists
    if not Path(args.html_file).exists():
        print(f"Error: HTML file '{args.html_file}' not found!")
        sys.exit(1)
    
    # Extract matches
    print(f"Processing data from {args.html_file}...")
    if args.team:
        print(f"Filtering matches for team: {args.team}")
    print("Extracting match data...")
    
    matches = extract_matches(args.html_file, args.team)
    save_to_csv(matches)

if __name__ == "__main__":
    main()
