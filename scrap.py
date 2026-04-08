from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("https://www.centre-commercial.fr/labege2/boutiques/")

# Je récupère le nom du centre commercial
centre_commercial = driver.find_element(By.CSS_SELECTOR, "h1.custom-h1").text

# Je récupère toutes les boutiques du centre commercial
noms = driver.find_elements(By.CSS_SELECTOR, "a.boutique-card")

boutiques = []

for nom in noms:
    boutique = nom.find_element(By.CSS_SELECTOR, "h2.custom-h2").text
    boutiques.append(boutique)

print(boutiques)