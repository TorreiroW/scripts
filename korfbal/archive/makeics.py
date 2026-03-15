#!/usr/bin/env python3
import glob
import csv
from ics import Calendar, Event
from datetime import datetime
import argparse

# Argument parser
parser = argparse.ArgumentParser(description="Maak een ICS voor een specifiek team.")
parser.add_argument("team", help="Teamnaam om te filteren")
args = parser.parse_args()
team_naam = args.team.lower()  # lowercase voor case-insensitive match

# Maak een nieuwe kalender
cal = Calendar()

# Vind alle blok*.csv bestanden
csv_files = sorted(glob.glob("blok*.csv"))

for csv_file in csv_files:
    # Haal datum uit de bestandsnaam: blok-YYYY-MM-DD.csv
    try:
        datum_str = csv_file.replace("blok-", "").replace(".csv", "")
        datum_obj = datetime.strptime(datum_str, "%Y-%m-%d")
    except ValueError:
        print(f"Kan datum niet lezen uit {csv_file}")
        continue

    # Open CSV
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # Verwacht kolommen: Tijd, Team, Tegenstander, Locatie, Scheidsrechter
            tijd, team, tegenstander, locatie, *rest = row

            # Filter op opgegeven teamnaam in Team of Tegenstander
            if team_naam not in team.lower() and team_naam not in tegenstander.lower():
                continue

            # Maak event
            try:
                tijd_obj = datetime.strptime(tijd, "%H:%M")
                start_datetime = datetime(
                    year=datum_obj.year,
                    month=datum_obj.month,
                    day=datum_obj.day,
                    hour=tijd_obj.hour,
                    minute=tijd_obj.minute
                )
            except ValueError:
                print(f"Ongeldige tijd '{tijd}' in {csv_file}")
                continue

            event = Event()
            event.name = f"{team},{tegenstander}"
            event.begin = start_datetime
            event.location = locatie
            event.duration = {"hours": 1}  # standaard 1 uur

            cal.events.add(event)

# Schrijf ICS bestand
ics_filename = f"{team_naam.replace(' ','_')}.ics"
with open(ics_filename, "w", encoding="utf-8") as f:
    f.writelines(cal)

print(f"ICS bestand aangemaakt: {ics_filename}")

