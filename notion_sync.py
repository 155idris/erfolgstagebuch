# ─────────────────────────────────────────────────────────────────────────────
# notion_sync.py — Notion-Synchronisation für das Erfolgstagebuch
#
# Architektur: Offline-First
#   1. Eintrag wird immer lokal in JSON gespeichert
#   2. Sofort Notion-Sync versuchen
#   3. Bei Fehler/Offline → bleibt als synced=False
#   4. Beim nächsten App-Start → ausstehende Einträge automatisch nachholen
#
# PCEP-Konzepte: Funktionen, Dictionaries, Listen, try/except, os.getenv,
#                String-Methoden, Schleifen, Conditionals, Modul-Import
# ─────────────────────────────────────────────────────────────────────────────

import os
from datetime import datetime

# Konfiguration aus Umgebungsvariablen (lokal: .env, Cloud: Streamlit Secrets)
NOTION_TOKEN       = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "c0d42dd7f4b845108ead404c6c7bb848")

# Mapping: lange App-Kategorien → kurze Notion-Optionsnamen
KATEGORIEN_MAP = {
    "⚡ Hauptmuster erkannt (im Moment)":               "Hauptmuster erkannt",
    "🪞 Hauptmuster erkannt (beim Reflektieren)":       "Hauptmuster erkannt",
    "🌱 Neues Verhalten gewählt — Muster nicht gefolgt": "Neues Verhalten",
    "👁️ Gefühl wahrgenommen":                           "Gefühl wahrgenommen",
    "🏷️ Gefühl benannt":                                "Gefühl benannt",
    "🤝 Gefühl angenommen":                             "Gefühl angenommen",
    "🔄 Gefühl verarbeitet / transformiert":            "Gefühl transformiert",
}


def notion_verfuegbar():
    """Prüft ob Notion-Token gesetzt und Client importierbar ist.
    PCEP: Conditionals, try/except, bool-Rückgabewert
    """
    if not NOTION_TOKEN:
        return False
    try:
        from notion_client import Client  # noqa: F401
        return True
    except ImportError:
        return False


def _verbinde():
    """Gibt einen Notion-Client zurück oder None.
    PCEP: try/except, Conditionals, Rückgabewert None
    """
    if not NOTION_TOKEN:
        return None
    try:
        from notion_client import Client
        return Client(auth=NOTION_TOKEN)
    except Exception:
        return None


def _datum_zu_iso(datum_str):
    """Konvertiert deutsches Datumsformat → ISO-Format für Notion.
    PCEP: String-Methoden, datetime.strptime/strftime, try/except
    Beispiel: '02.06.2026' → '2026-06-02'
    """
    try:
        return datetime.strptime(datum_str, "%d.%m.%Y").strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")


def sync_eintrag(eintrag):
    """Sendet einen einzelnen Eintrag an die Notion-Datenbank.
    PCEP: Dictionaries, Listen, Schleifen, try/except, String-Slicing
    Rückgabe: True wenn erfolgreich, False bei Fehler oder offline
    """
    notion = _verbinde()
    if not notion:
        return False

    try:
        # PCEP: Schleife + Set für deduplizierte Kategorien-Auswahl
        notion_kategorien = []
        bereits_gemappt = set()
        for kat in eintrag.get("kategorien", []):
            gemappt = KATEGORIEN_MAP.get(kat)
            if gemappt and gemappt not in bereits_gemappt:
                notion_kategorien.append({"name": gemappt})
                bereits_gemappt.add(gemappt)

        # PCEP: String-Join — Liste von Signalen → kommaseparierter Text
        signale = eintrag.get("erkannte_signale", [])
        signale_text = ", ".join(signale) if signale else ""

        # PCEP: Dictionary für Notion-Properties
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Text": {
                    "title": [{"text": {"content": eintrag["text"][:2000]}}]
                },
                "Datum": {
                    "date": {"start": _datum_zu_iso(eintrag["datum"])}
                },
                "Modus": {
                    "select": {"name": eintrag.get("modus", "rueckblick")}
                },
                "Kategorien": {
                    "multi_select": notion_kategorien
                },
                "Ist Hauptmuster": {
                    "checkbox": eintrag.get("ist_hauptmuster", False)
                },
                "Intensität": {
                    "number": eintrag.get("intensitaet") or None
                },
                "Erkannte Signale": {
                    "rich_text": [{"text": {"content": signale_text[:2000]}}]
                },
                "Spiegel": {
                    "rich_text": [{"text": {"content": eintrag.get("spiegel", "")[:2000]}}]
                },
                "Schritt": {
                    "rich_text": [{"text": {"content": eintrag.get("schritt", "")[:2000]}}]
                },
            }
        )
        return True

    except Exception:
        return False


def sync_ausstehende(eintraege):
    """Synchronisiert alle Einträge die noch nicht in Notion sind.
    PCEP: Schleifen, Conditionals, Zähler-Variable, Liste modifizieren
    Rückgabe: (aktualisierte_eintraege, anzahl_erfolgreich_gesynct)
    """
    if not notion_verfuegbar():
        return eintraege, 0

    gesynct = 0  # PCEP: Zähler-Variable
    for i, e in enumerate(eintraege):
        # PCEP: dict.get() mit Default — ältere Einträge ohne synced-Feld
        if not e.get("synced", False):
            if sync_eintrag(e):
                eintraege[i]["synced"] = True
                gesynct += 1

    return eintraege, gesynct
