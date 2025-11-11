
import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="GeoMap Inserate – Cloud", layout="wide")
st.title("GeoMap Inserate – API Suche + Viewer")

st.sidebar.header("Datenquelle")
api_url = st.sidebar.text_input("Render API Endpoint (/search)", "https://<DEIN-RENDER>.onrender.com/search")
csv_path = st.sidebar.text_input("CSV Pfad (relativ im Repo)", "data/geomap_api_results.csv")

default_payload = {
  "filter": {
    "angebotArt": ["KAUF"],
    "currency": "EUR",
    "regionId": "DE.BOCHOLT.ORT",
    "type": "region",
    "grundstuecksflaeche": {"von": 500},
    "objektKategorien": {"Wohnen": {"Haus": {"EinZweiFamilienhaus": ["Einfamilienhaus","Doppelhaushaelfte","Zweifamilienhaus","Reihenhaus","ReiheneckEndhaus","Reihenmittelhaus"]}, "Grundstueck": {}, "StellplatzGarage": {}}},
    "objektKategorienAllowed": ["Wohnen","Gewerbe","Spezial"],
    "zimmer": {},
    "wohnflaeche": {},
    "preis": {},
    "preisProQm": {},
    "baujahr": {},
    "energieKennwert": {},
    "eigenschaften": {},
    "rendite": {},
    "sanierungsjahr": {}
  },
  "parameter": {"limit": 100, "offset": 0, "sortOrder": "ASC"}
}

with st.expander("Payload bearbeiten (optional)"):
  payload_text = st.text_area("JSON Payload", json.dumps(default_payload, ensure_ascii=False, indent=2), height=280)
  try:
    effective_payload = json.loads(payload_text)
  except Exception as e:
    st.error(f"Ungültiges JSON: {e}")
    effective_payload = default_payload

if st.sidebar.button("🔄 Suche jetzt ausführen (Render)"):
  with st.spinner("Suche läuft über Render…"):
    try:
      r = requests.post(api_url, json=effective_payload, timeout=180)
      if r.status_code == 200:
        resp = r.json()
        st.success(f"OK – {resp.get('count',0)} Treffer in {resp.get('duration_sec',0)}s")
        st.write("Vorschau der ersten 10 Zeilen:")
        st.json(resp.get("preview", []))
      else:
        st.error(f"Fehler {r.status_code}: {r.text[:400]}")
    except Exception as e:
      st.error(f"Request fehlgeschlagen: {e}")

st.markdown("---")
st.header("CSV laden & anzeigen")
try:
  df = pd.read_csv(csv_path)
  st.metric("Anzahl Inserate", len(df))
  show_cols = [c for c in ["titel","preis","preisProQm","wohnflaeche","grundstueck","zimmer","baujahr","adresse","anbieter","url"] if c in df.columns]
  st.dataframe(df[show_cols])
except Exception as e:
  st.info(f"CSV noch nicht vorhanden oder Pfad falsch: {e}")
