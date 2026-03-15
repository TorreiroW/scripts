#!/usr/bin/env python3
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# Huidig jaar
current_year = datetime.now().year

# HTML inlezen
with open("index.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# CSV file openen
with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    # Header
    writer.writerow(["Date", "Tijd", "Thuis", "Uit", "Locatie"])

    # Loop over alle h3-elementen
    for h3 in soup.find_all("h3"):
        date_text = h3.get_text(strip=True)  # bv "13 september"
        date_str = f"{date_text} {current_year}"

        # Parse datum
        try:
            date_obj = datetime.strptime(date_str, "%d %B %Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = ""  # fallback bij fout

        # Loop over alle tables tot de volgende h3
        for table in h3.find_all_next("table", class_="table inverse table-hover"):
            # Stoppen als we bij een andere h3 komen
            if table.find_previous("h3") != h3:
                break

            for tr in table.find_all("tr")[1:]:  # sla header row over
                tds = tr.find_all("td")
                if len(tds) >= 4:  # Zorg dat er genoeg kolommen zijn
                    tijd = tds[0].get_text(strip=True)
                    thuis = tds[1].get_text(strip=True)
                    uit = tds[2].get_text(strip=True)
                    locatie = tds[3].get_text(strip=True)
                    writer.writerow([formatted_date, tijd, thuis, uit, locatie])

