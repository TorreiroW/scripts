#!/usr/bin/env python3
from bs4 import BeautifulSoup

# Stap 1: Haal de inhoud van de div en schrijf naar output.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Vind de eerste div met de opgegeven klasse
div = soup.find("div", class_="page-content table-responsive")

if div:
    div_content = div.decode_contents()

    # Schrijf naar output.html
    with open("output.html", "w", encoding="utf-8") as out_file:
        out_file.write(div_content)

    print("Inhoud weggeschreven naar output.html")

    # Stap 2: Open de output.html en splits per <h3> ... </table>
    div_soup = BeautifulSoup(div_content, "html.parser")
    h3_tags = div_soup.find_all("h3")

    for idx, h3 in enumerate(h3_tags, start=1):
        block_content = [str(h3)]

        # Voeg siblings toe tot de eerstvolgende <table>
        for sibling in h3.next_siblings:
            if sibling.name == "table":
                block_content.append(str(sibling))
                break
            elif isinstance(sibling, str):
                block_content.append(sibling)
            else:
                block_content.append(str(sibling))

        # Schrijf elk blok naar apart bestand
        filename = f"blok{idx}.html"
        with open(filename, "w", encoding="utf-8") as out_file:
            out_file.write("".join(block_content))

        print(f"Inhoud van H3 {idx} weggeschreven naar {filename}")

else:
    print("Div niet gevonden")

