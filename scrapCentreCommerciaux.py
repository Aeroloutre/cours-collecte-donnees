from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://www.google.com/maps/search/centre+commercial/@43.5987012,3.915776,15z/data=!4m2!2m1!6e6?entry=ttu&g_ep=EgoyMDI2MDQwNS4wIKXMDSoASAFQAw%3D%3D")

wait = WebDriverWait(driver, 10)

# On accepte les cookies
element = driver.find_element(By.XPATH, '//*[text()="Tout accepter"]').click()

# On scroll la page pour charger tous les résultats
scrollable_div = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
)

last_count = 0

while True:
    # récupérer les articles
    articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
    print("Nombre:", len(articles))

    # scroll
    driver.execute_script(
        "arguments[0].scrollBy(0, 1000);",
        scrollable_div
    )

    time.sleep(1.5)

    # Récuperer les artciles après le scroll
    new_articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
    new_count = len(new_articles)

    if new_count == last_count:
        break

    last_count = new_count

# Je récupère toutes les boutiques du centre commercial
articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')

for article in articles:
    nom = article.get_attribute("aria-label")

# On filtre les résultats pour ne garder que les centres commerciaux
filtre = [el for el in nom if "centre commercial" in el.lower()]

print(filtre)