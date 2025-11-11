
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
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/objekte']")))
    except TimeoutException:
        driver.quit()
        raise RuntimeError("Login nicht bestätigt – bitte Login-Selektoren prüfen.")

    import requests as rq
    s = rq.Session()
    for c in driver.get_cookies():
        s.cookies.set(c["name"], c["value"], domain=c.get("domain"), path=c.get("path", "/"))
    try:
        token = driver.execute_script("return document.querySelector('meta[name="csrf-token"]').content")
        if token:
            s.headers.update({"x-csrf-token": token})
    except Exception:
        pass
    s.headers.update({
        "content-type": "application/json;charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "origin": "https://geomap.immo",
        "referer": "https://geomap.immo/"
    })
    driver.quit()
    return s

def flatten_row(obj: dict) -> dict:
    return {
        "id": obj.get("id") or obj.get("objektId"),
        "titel": obj.get("titel") or obj.get("title"),
        "preis": obj.get("preis") or obj.get("price"),
        "preisProQm": obj.get("preisProQm") or obj.get("pricePerSqm"),
        "wohnflaeche": obj.get("wohnflaeche") or obj.get("livingSpace"),
        "grundstueck": obj.get("grundstuecksflaeche") or obj.get("propertySpace"),
        "zimmer": obj.get("zimmer") or obj.get("rooms"),
        "baujahr": obj.get("baujahr") or obj.get("constructionYear"),
        "energie": obj.get("energieKennwert") or obj.get("energy"),
        "adresse": obj.get("adresse") or obj.get("address"),
        "anbieter": obj.get("anbieter") or obj.get("vendor"),
        "url": obj.get("portalUrl") or obj.get("url"),
    }

@app.post("/search")
def search():
    body = request.get_json(force=True) or {}
    filter_ = body.get("filter", {})
    parameter = body.get("parameter", {"limit": 100, "offset": 0, "sortOrder": "ASC"})
    limit = int(parameter.get("limit", 100))
    offset = int(parameter.get("offset", 0))
    sortOrder = parameter.get("sortOrder", "ASC")
    max_pages = int(body.get("maxPages", 50))

    sess = login_and_get_session()

    rows = []
    pages = 0
    t0 = time.time()

    while pages < max_pages:
        payload = {"filter": filter_, "parameter": {"limit": limit, "offset": offset, "sortOrder": sortOrder}}
        r = sess.post(SEARCH_URL, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        items = data.get("result") or data.get("offers") or data.get("liste") or data.get("items") or []
        if not items:
            break
        for it in items:
            rows.append(flatten_row(it))
        if len(items) < limit:
            break
        offset += limit
        pages += 1

    import os
    os.makedirs("data", exist_ok=True)
    csv_path = "data/geomap_api_results.csv"
    if rows:
        cols = list(rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(rows)

    return jsonify({"status": "ok", "count": len(rows), "duration_sec": round(time.time()-t0,2),
                    "preview": rows[:10], "csv_path": csv_path})

@app.get("/")
def index():
    return "✅ GeoMap API-Scraper online. POST /search mit deinem DevTools-Payload."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
