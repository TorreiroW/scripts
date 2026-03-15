#!/usr/bin/env python3
import glob
import csv
from bs4 import BeautifulSoup
from datetime import datetime

# Huidig jaar
current_year = datetime.now().year

# Maandnaam naar nummer mapping (Nederlands)
maanden = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12"
}

# Vind alle blok*.html bestanden
blok_files = sorted(glob.glob("blok*.html"))

for blok_file in blok_files:
    with open(blok_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Haal de datum uit de eerste <h3> tag
    h3 = soup.find("h3")
    if h3:
        datum_text = h3.get_text(strip=True)  # bv "12 september"
        try:
            dag, maand_naam = datum_text.split()
            maand_num = maanden.get(maand_naam.lower(), "00")
            datum_formatted = f"{current_year}-{maand_num}-{int(dag):02d}"
        except ValueError:
            datum_formatted = "onbekend"
    else:
        datum_formatted = "onbekend"

    # Vind de eerste <table>
    table = soup.find("table")
    if not table:
        print(f"Geen tabel gevonden in {blok_file}")
        continue

    # Haal alle rijen uit de tabel
    rows = table.find_all("tr")

    # Schrijf CSV-bestand met datum in de naam
    csv_file = f"blok-{datum_formatted}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_text = [cell.get_text(strip=True) for cell in cells]
            writer.writerow(cell_text)

    print(f"Tabel uit {blok_file} weggeschreven naar {csv_file}")

