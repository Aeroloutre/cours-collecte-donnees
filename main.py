from camoufox.sync_api import Camoufox
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import scrapCentreCommerciaux
import time
import random
import csv
from datetime import datetime

def human_delay(min_ms=800, max_ms=2000):
    time.sleep(random.uniform(min_ms, max_ms) / 1000)

def generate_timestamped_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"boutiques_{timestamp}.csv"

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
                print(f"Impossible de trouver 'Nos marques' pour {nom}")
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