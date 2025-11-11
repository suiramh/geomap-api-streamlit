
# GeoMap API Suche (Render) + Streamlit Cloud Viewer

## Was ist drin?
- **scripts/scrape_geomap_api_backend.py** – Flask-API für Render. Loggt sich ein, ruft die interne Geomap-Suche `/service/objekt/suche` auf, paginiert und schreibt CSV.
- **app/streamlit_app.py** – Streamlit-Frontend (Cloud). Button triggert die API und zeigt CSV.

## Schritt 1 – Repo zu GitHub hochladen
- Neues Repo erstellen (z. B. `geomap-api-streamlit`)
- Diesen Ordnerinhalt hochladen (app/, scripts/, data/, requirements.txt, .gitignore, README.md)

## Schritt 2 – Render.com (Backend) einrichten
- Render Konto → New + → Web Service → aus GitHub Repo deployen
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python scripts/scrape_geomap_api_backend.py`
- **Environment Variables:**
  - `GEOMAP_USER` – deine Login-E-Mail
  - `GEOMAP_PASS` – dein Passwort
  - optional `GEOMAP_LOGIN_URL` – Standard `https://geomap.immo/login`
- Region EU, Free Instance
- Nach dem Deploy hast du eine URL: `https://<dein-service>.onrender.com`

## Schritt 3 – Streamlit Cloud (Frontend) deployen
- share.streamlit.io → New app → Repo wählen
- **Main file:** `app/streamlit_app.py` → Deploy
- In der App-Sidebar: `Render API Endpoint` auf `https://<dein-service>.onrender.com/search` setzen

## Schritt 4 – Payload
- Im Streamlit-Expander kannst du den **exacten JSON-Payload** (aus DevTools) einfügen. Beispiel ist bereits vorbelegt.
- Klick **"Suche jetzt ausführen"** → App zeigt Preview, CSV wird bei Render unter `data/geomap_api_results.csv` gespeichert.

## Anpassen
- Feld-Mapping im Backend (`flatten_row`) an die reale Antwort anpassen (nach erstem Lauf).
- Pagination via `limit/offset` geschieht automatisch, bis keine Datensätze mehr kommen.
