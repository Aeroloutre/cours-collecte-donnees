from camoufox.sync_api import Camoufox
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import scrapCentreCommerciaux
import checker
import time
import random
import csv
import os
from datetime import datetime

def human_delay(min_ms=800, max_ms=2000):
    time.sleep(random.uniform(min_ms, max_ms) / 1000)

def generate_timestamped_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"boutiques_{timestamp}.csv"

def get_timestamped_files():
    files = [f for f in os.listdir(".") if f.startswith("boutiques_") and f.endswith(".csv")]
    return sorted(files, reverse=True)

def display_comparison(file1, file2, results):
    print(f"\n{'='*70}")
    print(f"Comparaison: {file1} -> {file2}")
    print(f"{'='*70}\n")
    
    total_added = 0
    total_removed = 0
    stores_with_changes = 0
    
    for store, changes in results["stores"].items():
        if changes["added"] or changes["removed"]:
            stores_with_changes += 1
            print(f"{store}:")
            
            if changes["removed"]:
                print(f"  Marques disparues ({len(changes['removed'])})")
                for brand in sorted(changes["removed"])[:10]:
                    print(f"    - {brand}")
                if len(changes["removed"]) > 10:
                    print(f"    ... et {len(changes['removed']) - 10} autres")
                total_removed += len(changes["removed"])
            
            if changes["added"]:
                print(f"  Marques apparues ({len(changes['added'])})")
                for brand in sorted(changes["added"])[:10]:
                    print(f"    + {brand}")
                if len(changes["added"]) > 10:
                    print(f"    ... et {len(changes['added']) - 10} autres")
                total_added += len(changes["added"])
            
            print()
    
    print(f"{'='*70}")
    print(f"Boutiques affectees: {stores_with_changes}")
    print(f"Total marques disparues: {total_removed}")
    print(f"Total marques apparues: {total_added}")
    print(f"{'='*70}\n")

def compare_latest():
    files = get_timestamped_files()
    if len(files) < 2:
        print("Pas assez de fichiers pour la comparaison")
        return
    
    file1, file2 = files[1], files[0]
    results = checker.compare_csv_files(file1, file2)
    display_comparison(file1, file2, results)

def show_history():
    checker.display_history()

def generate_report_txt():
    """Genere un rapport txt de l'historique complet des changements"""
    checker.save_changes_to_txt()

def scrape():
    output_file = generate_timestamped_filename()
    boutiques = []
    commercial_centers = scrapCentreCommerciaux.scrapCentreCommerciaux()

    with Camoufox(headless=False, locale=["fr-FR"]) as browser:
        page = browser.new_page()

        for commercial_center in commercial_centers:
            if "Galeries Lafayette" not in commercial_center:
                continue

            nom = commercial_center.replace("Galeries Lafayette", "").strip()
            if len(nom.split()) != 1:
                continue

            url = f"https://www.galerieslafayette.com/m/magasin-{nom.lower()}"
            page.goto(url, wait_until="domcontentloaded")
            human_delay(1500, 3000)

            try:
                page.click("button:has-text('Accepter')", timeout=3000)
                human_delay()
            except PlaywrightTimeoutError:
                pass

            try:
                brands_button = page.wait_for_selector(
                    "button:has-text('Nos marques')",
                    timeout=10000
                )
                brands_button.scroll_into_view_if_needed()
                human_delay(500, 1200)
                brands_button.click()
                human_delay(1000, 2000)
            except PlaywrightTimeoutError:
                print(f"[WARN] Bouton 'Nos marques' introuvable pour {nom}")
                continue

            brand_buttons = page.query_selector_all("#brands-list button")
            brands = [btn.inner_text().strip() for btn in brand_buttons if btn.inner_text().strip()]

            boutiques.append((nom, brands))
            print(f"{nom}: {len(brands)} marques trouvees")

    print(boutiques)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Boutique", "Marques"])
        for nom, brands in boutiques:
            writer.writerow([nom, "; ".join(brands)])
    
    print(f"Donnees sauvegardees dans {output_file}")


if __name__ == "__main__":
    scrape()