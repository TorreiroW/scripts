#!/usr/bin/env python3

import os
import glob
import csv
import shutil
import tempfile
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime
import argparse
from zoneinfo import ZoneInfo

# -------------------------
# Argument parser
# -------------------------
parser = argparse.ArgumentParser(description="Van schema HTML naar ICS voor een team.")
parser.add_argument("team", help="Teamnaam om te filteren")
args = parser.parse_args()
team_naam = args.team.lower()
tz = ZoneInfo("Europe/Amsterdam")

# -------------------------
# Maak tijdelijke directory
# -------------------------
tmp_dir = tempfile.mkdtemp()
print(f"Tijdelijke directory aangemaakt: {tmp_dir}")

try:
    # -------------------------
    # Stap 0: Download HTML van website
    # -------------------------
    url = "https://dindoa.nl/ws/competitie-programma/"
    print(f"Downloading HTML from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    print("HTML successfully downloaded")

    # -------------------------
    # Stap 1: Haal de inhoud van de div en split per <h3>
    # -------------------------
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", class_="page-content table-responsive")
    if not div:
        print("Div niet gevonden in index.html")
        exit(1)

    div_content = div.decode_contents()
    div_soup = BeautifulSoup(div_content, "html.parser")
    h3_tags = div_soup.find_all("h3")

    # Maak blok*.html bestanden
    blok_files = []
    for idx, h3 in enumerate(h3_tags, start=1):
        block_content = [str(h3)]
        for sibling in h3.next_siblings:
            if sibling.name == "table":
                block_content.append(str(sibling))
                break
            elif isinstance(sibling, str):
                block_content.append(sibling)
            else:
                block_content.append(str(sibling))
        blok_filename = os.path.join(tmp_dir, f"blok{idx}.html")
        with open(blok_filename, "w", encoding="utf-8") as f_out:
            f_out.write("".join(block_content))
        blok_files.append(blok_filename)

    print(f"{len(blok_files)} blok*.html bestanden aangemaakt in tijdelijke directory")

    # -------------------------
    # Stap 2: Parse blok*.html naar blok-YYYY-MM-DD.csv
    # -------------------------
    current_year = "2026" #datetime.now().year
    maanden = {
        "januari": "01", "februari": "02", "maart": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "augustus": "08",
        "september": "09", "oktober": "10", "november": "11", "december": "12"
    }

    csv_files = []
    for blok_file in blok_files:
        with open(blok_file, "r", encoding="utf-8") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")

        # Datum uit <h3>
        h3 = soup.find("h3")
        if h3:
            datum_text = h3.get_text(strip=True)
            try:
                dag, maand_naam = datum_text.split()
                maand_num = maanden.get(maand_naam.lower(), "00")
                datum_formatted = f"{current_year}-{maand_num}-{int(dag):02d}"
            except ValueError:
                datum_formatted = "onbekend"
        else:
            datum_formatted = "onbekend"

        # Tabel naar CSV
        table = soup.find("table")
        if not table:
            continue
        rows = table.find_all("tr")
        csv_file = os.path.join(tmp_dir, f"blok-{datum_formatted}.csv")
        csv_files.append(csv_file)
        with open(csv_file, "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.writer(f_csv)
            for row in rows:
                cells = row.find_all(["th", "td"])
                cell_text = [cell.get_text(strip=True) for cell in cells]
                writer.writerow(cell_text)

    print(f"{len(csv_files)} CSV bestanden aangemaakt in tijdelijke directory")

    # -------------------------
    # Stap 3: Maak ICS voor opgegeven team
    # -------------------------
    cal = Calendar()
    for csv_file in csv_files:
        try:
            datum_str = os.path.basename(csv_file).replace("blok-", "").replace(".csv", "")
            datum_obj = datetime.strptime(datum_str, "%Y-%m-%d")
        except ValueError:
            continue

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                tijd, team, tegenstander, _, locatie, *rest = row
                if team_naam not in team.lower() and team_naam not in tegenstander.lower():
                    continue
                try:
                    tijd_obj = datetime.strptime(tijd, "%H:%M")
                    start_datetime = datetime(
                        year=datum_obj.year,
                        month=datum_obj.month,
                        day=datum_obj.day,
                        hour=tijd_obj.hour,
                        minute=tijd_obj.minute,
                        tzinfo=tz
                    )
                except ValueError:
                    continue
                event = Event()
                event.name = f"{team},{tegenstander}"
                event.begin = start_datetime
                event.location = locatie
                event.duration = {"hours": 1}
                cal.events.add(event)

    ics_filename = f"{team_naam.replace(' ','_')}.ics"
    with open(ics_filename, "w", encoding="utf-8") as f:
        f.writelines(cal)

    print(f"ICS bestand aangemaakt: {ics_filename}")

finally:
    # Verwijder tijdelijke directory
    shutil.rmtree(tmp_dir)
    print(f"Tijdelijke directory {tmp_dir} verwijderd")

