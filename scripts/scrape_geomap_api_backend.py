
from flask import Flask, request, jsonify
import os, time, csv, json, requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

GEOMAP_LOGIN_URL = os.getenv("GEOMAP_LOGIN_URL", "https://geomap.immo/login")
GEOMAP_USER = os.getenv("GEOMAP_USER", "")
GEOMAP_PASS = os.getenv("GEOMAP_PASS", "")

SEARCH_URL = "https://app.geomap.immo/service/objekt/suche"

app = Flask(__name__)

def login_and_get_session():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,1000")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get(GEOMAP_LOGIN_URL)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    user_el = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    pass_el = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    user_el.clear(); user_el.send_keys(GEOMAP_USER)
    pass_el.clear(); pass_el.send_keys(GEOMAP_PASS); pass_el.send_keys(Keys.ENTER)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/objekte']")))

    import requests as rq
    s = rq.Session()
    for c in driver.get_cookies():
        s.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path", "/"))

    s.headers.update({
        "content-type": "application/json;charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "origin": "https://geomap.immo",
        "referer": "https://geomap.immo/"
    })

    driver.quit()
    return s
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
