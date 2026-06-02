# Erfolgstagebuch
### PCEP-Abschlussprojekt — Idrissa Sow

---

## Was ist dieses Projekt?

Das **Erfolgstagebuch** ist eine persönliche Web-App zum Dokumentieren emotionaler Erfolge im Alltag.

**Kernidee:** Nicht Misserfolge verfolgen — sondern die Momente sichtbar machen, in denen man ein altes Verhaltensmuster erkannt oder bewusst anders gehandelt hat. Der Fokus liegt auf kleinen, realen Befreiungsschritten.

**Zwei Modi:**

| Modus | Zweck |
|---|---|
| ⚡ Akut-Modus | Sofort-Check-in wenn das Muster gerade aktiv ist (< 60 Sekunden) |
| 📖 Rückblick | Abendliches Dokumentieren eines Erfolgs |

---

## Technologie

- **Sprache:** Python 3
- **Framework:** Streamlit (Web-Interface)
- **Datenspeicher:** JSON-Datei (lokal)
- **Deployment:** Streamlit Community Cloud (erreichbar per Handy-Browser)

---

## PCEP-Konzepte — Übersicht

Diese Tabelle zeigt welche PCEP-Prüfungsthemen im Projekt verwendet werden und wo genau sie im Code zu finden sind.

| PCEP-Konzept | Datei | Wo im Code |
|---|---|---|
| Variablen und Datentypen | `app.py` | `streak`, `hm_gesamt`, `heute_str`, `als_erfolg` |
| Strings und f-Strings | `app.py` | Header, Badge-Labels, `vorschau = e["text"][:55] + "..."` |
| String-Methoden | `daten.py` | `datetime.strftime()`, `e["datum"]`, String-Slicing |
| Listen (erstellen, append, slicing) | `daten.py` | `KATEGORIEN`, `ergebnis.append(e)`, `alle_eintraege[-10:]` |
| List Comprehension | `app.py` | `[e for e in woche if e.get("ist_hauptmuster")]` |
| Dictionaries (erstellen, lesen, schreiben) | `daten.py` | Jeder `eintrag`-Dict, `stats`-Dict in `kategorie_stats()` |
| `dict.get()` mit Default-Wert | `daten.py` | `e.get("modus", "")`, `e.get("ist_hauptmuster", False)` |
| Funktionen definieren (`def`) | `daten.py` | Alle 8 Funktionen |
| Parameter und Rückgabewert (`return`) | `daten.py` | `berechne_streak()`, `kategorie_stats()`, `lade_eintraege()` |
| Default-Parameter | `daten.py` | `neuer_akut_eintrag(text, erkannte_signale, spiegel, schritt)` |
| Module importieren | `app.py` | `import streamlit as st`, `import daten`, `from datetime import datetime` |
| `for`-Schleife | `daten.py`, `app.py` | Einträge iterieren, Stats berechnen, Einträge anzeigen |
| `while`-Schleife | `daten.py` | Streak-Berechnung in `berechne_streak()` |
| `if / elif / else` | `app.py`, `daten.py` | Eingabe-Validierung, Modus-Auswahl, Datei-Existenz |
| Boolean-Werte | `app.py` | `als_erfolg = st.checkbox(...)`, `ist_hauptmuster` |
| `any()` | `daten.py` | `any(k in MUSTER_KATEGORIEN for k in kategorien)` |
| `in`-Operator | `daten.py` | `if aktueller_tag in tage_mit_eintrag` |
| Set | `daten.py` | `tage_mit_eintrag = set()` in `berechne_streak()` |
| File I/O (`open`, `read`, `write`) | `daten.py` | `lade_eintraege()`, `_schreibe_eintraege()` |
| `json`-Modul | `daten.py`, `app.py` | `json.load()`, `json.dump()`, `json.dumps()` |
| `datetime`-Modul | `daten.py` | Datum/Uhrzeit speichern, Streak berechnen, `timedelta` |
| String-Multiplikation | `app.py` | `"●" * intensitaet + "○" * (5 - intensitaet)` |
| Zähler-Variable | `daten.py` | `anzahl = 0` + `anzahl += 1` |
| Mehrfach-Zuweisung (Tuple-Unpacking) | `app.py` | `tab1, tab2, tab3 = st.tabs([...])` |

---

## Projektstruktur

```
Erfolgstagebuch/
├── app.py              # Streamlit-App (Benutzeroberfläche)
├── daten.py            # Datenschicht (alle Python-Funktionen)
├── eintraege.json      # Datenspeicher (wird automatisch angelegt)
├── requirements.txt    # Abhängigkeiten (nur: streamlit)
└── README.md           # Diese Dokumentation
```

---

## Installation und Start

```bash
# 1. Abhängigkeit installieren
pip install streamlit

# 2. App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

---

## Datenformat

Jeder Eintrag wird als Dictionary in `eintraege.json` gespeichert:

```json
{
  "datum": "02.06.2026",
  "uhrzeit": "14:32",
  "modus": "akut",
  "text": "Ich merke gerade wie ich mich wieder zurückziehe...",
  "kategorien": ["⚡ Hauptmuster erkannt (im Moment)"],
  "ist_hauptmuster": true,
  "intensitaet": 0,
  "erkannte_signale": ["Rückzug / Unsichtbar werden"],
  "spiegel": "Das könnte nach dem Rückzugsmuster klingen.",
  "schritt": "Du musst nicht verschwinden. Du kannst bleiben."
}
```

---

## Kategorien

| Kategorie | Bedeutung |
|---|---|
| ⚡ Hauptmuster erkannt (im Moment) | Muster wurde während des Geschehens wahrgenommen |
| 🪞 Hauptmuster erkannt (beim Reflektieren) | Muster wurde nachträglich erkannt |
| 🌱 Neues Verhalten gewählt | Muster war aktiv — und wurde bewusst nicht befolgt |
| 👁️ Gefühl wahrgenommen | Emotion wurde bemerkt, nicht verdrängt |
| 🏷️ Gefühl benannt | Emotion konnte in Worte gefasst werden |
| 🤝 Gefühl angenommen | Emotion wurde zugelassen statt bekämpft |
| 🔄 Gefühl verarbeitet / transformiert | Emotion wurde durchgearbeitet und veränderte sich |

---

## Cloud-Deployment (Handy-Zugriff)

1. Projekt auf GitHub pushen
2. [share.streamlit.io](https://share.streamlit.io) → "New app" → GitHub-Repo auswählen
3. App-URL auf dem Handy öffnen

> **Hinweis zur Datenpersistenz:** Streamlit Cloud speichert keine Dateien dauerhaft.
> Die Einträge können über den "Daten sichern"-Button als JSON heruntergeladen
> und bei Bedarf neu hochgeladen werden.
