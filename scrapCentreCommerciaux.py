from camoufox.sync_api import Camoufox
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
from datetime import datetime

def scrapCentreCommerciaux():
    with Camoufox(headless=False, locale=["fr-FR"]) as browser:
        page = browser.new_page()

        page.goto(
            "https://www.google.com/maps/search/galeries+lafayette/@46.7623999,-0.8233315,6.27z"
            "/data=!4m2!2m1!6e6?authuser=0&hl=fr&entry=ttu",
            wait_until="domcontentloaded"
        )

        # Accepter les cookies Google
        try:
            page.click('button:has-text("Tout accepter")', timeout=5000)
        except PlaywrightTimeoutError:
            pass

        # Attendre le feed de résultats
        page.wait_for_selector('div[role="feed"]', timeout=10000)
        scrollable_div = page.query_selector('div[role="feed"]')

        last_count = 0
        while True:
            articles = page.query_selector_all('div[role="article"]')
            new_count = len(articles)

            scrollable_div.evaluate("el => el.scrollBy(0, 1000)")
            time.sleep(1.5)

            articles_after = page.query_selector_all('div[role="article"]')
            new_count_after = len(articles_after)

            if new_count_after == last_count:
                break
            last_count = new_count_after

        articles = page.query_selector_all('div[role="article"]')
        commercial_centers = []
        for article in articles:
            nom = article.get_attribute("aria-label")
            if nom:
                commercial_centers.append(nom)

        filtered = [c for c in commercial_centers if "Galeries Lafayette" in c]
        print(filtered)
        return filtered