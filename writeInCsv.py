import csv

def writeInCsv(magasins, centre_commercial):
    with open("Magasins.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for magasin in magasins:
            writer.writerow([magasin, centre_commercial])