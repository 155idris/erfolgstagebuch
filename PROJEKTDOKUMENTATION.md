# Projektdokumentation — PCEP Abschlussprojekt
**Student:** Idrissa Sow  
**Datum:** 02.06.2026  
**Kurs:** PCEP™ – Certified Entry-Level Python Programmer

---

## 1. Projektidee und Zielsetzung

### Was wurde gebaut?
Eine persönliche Web-App zur emotionalen Selbstreflexion. Die App hilft dabei, automatische Verhaltensmuster (sog. "Autopilot-Reaktionen") im Alltag zu erkennen, zu benennen und Schritt für Schritt neue Verhaltensweisen zu wählen.

### Warum dieses Projekt?
Das Projekt verbindet technisches Lernen mit einem echten, persönlichen Nutzen. Anstatt eine abstrakte Übungsaufgabe zu lösen, entstand ein Tool, das ich selbst täglich verwende. Dadurch war die Motivation hoch und die PCEP-Konzepte wurden in einem realen Kontext gelernt.

### Kernidee
> *"Bewusstsein über ein Muster ist der erste Schritt zur Befreiung davon."*

Die App macht sichtbar, wie oft man Muster erkennt, annimmt oder überwindet — und baut so schrittweise Selbstvertrauen auf.

---

## 2. Technischer Überblick

### Stack
| Komponente | Technologie | Grund |
|---|---|---|
| Programmiersprache | Python 3 | PCEP-Kurs |
| Web-Interface | Streamlit | einfach, visuell, keine HTML-Kenntnisse nötig |
| Datenspeicherung | JSON (lokal) + Notion (Cloud) | Offline-First-Architektur |
| Deployment | Streamlit Community Cloud | kostenlos, erreichbar vom Handy |

### Architektur: Offline-First
```
Eintrag speichern
       ↓
eintraege.json  ← immer, sofort (lokaler Puffer)
       ↓
Notion-Sync versuchen
  ✅ Online  → synced = True
  ❌ Offline → synced = False, wird beim nächsten Start nachgeholt
```

---

## 3. Projektstruktur

```
Erfolgstagebuch/
├── app.py                  Streamlit-App (Benutzeroberfläche)
├── daten.py                Datenschicht (alle Python-Funktionen)
├── notion_sync.py          Notion-Synchronisation (Offline-First)
├── eintraege.json          Lokaler Datenspeicher (auto-erstellt)
├── requirements.txt        Abhängigkeiten
├── README.md               Technische Dokumentation
└── PROJEKTDOKUMENTATION.md Diese Datei
```

---

## 4. Dateibeschreibungen

### `daten.py` — Datenschicht
Enthält alle Funktionen zum Lesen, Schreiben und Auswerten der Einträge. Keine Abhängigkeit zu Streamlit — reine Python-Logik.

**Funktionen:**
| Funktion | Was sie macht |
|---|---|
| `lade_eintraege()` | JSON-Datei lesen, leere Liste wenn nicht vorhanden |
| `_schreibe_eintraege()` | Liste in JSON-Datei schreiben |
| `neuer_rueckblick_eintrag()` | Rückblick-Eintrag erstellen und speichern |
| `neuer_akut_eintrag()` | Akut-Moment-Eintrag erstellen und speichern |
| `analysiere_akut_text()` | Freitext auf Muster-Keywords analysieren |
| `berechne_streak()` | Aufeinanderfolgende Tage mit Einträgen zählen |
| `eintraege_diese_woche()` | Einträge der letzten 7 Tage filtern |
| `kategorie_stats()` | Häufigkeit jeder Kategorie zählen |
| `hauptmuster_count()` | Anzahl Hauptmuster-Einträge zählen |
| `akut_count()` | Anzahl Akut-Modus-Einträge zählen |

### `notion_sync.py` — Cloud-Synchronisation
Verantwortet die Verbindung zur Notion-Datenbank. Wird nur aufgerufen wenn ein Netzwerk vorhanden ist — bei Fehler bleibt der Eintrag lokal als `synced=False` gespeichert.

### `app.py` — Benutzeroberfläche
Streamlit-App mit drei Tabs:

**Tab 1 — ⚡ Akut-Modus**  
Für Momente in denen ein Muster gerade aktiv ist. Freies Textfeld ohne Struktur — die App analysiert im Hintergrund und gibt einen Spiegel zurück.

**Tab 2 — 📖 Rückblick**  
Zum nachträglichen Dokumentieren von Erfolgen. Kategorien auswählen, Intensität einschätzen, speichern.

**Tab 3 — 📊 Fortschritt**  
Übersicht mit Metriken, Wochenstatistik, Balkendiagramm und allen bisherigen Einträgen.

---

## 5. PCEP-Konzepte — vollständige Übersicht

| PCEP-Konzept | Datei | Konkrete Stelle im Code |
|---|---|---|
| **Variablen und Datentypen** | `app.py` | `streak`, `hm_gesamt`, `heute_str`, `notion_ok` |
| **Strings** | `daten.py` | Felder wie `"datum"`, `"text"`, `"modus"` |
| **f-Strings** | `app.py` | Header, Badge-Labels, Vorschau-Texte |
| **String-Methoden** | `daten.py` | `.lower()`, `.strftime()`, `.strip()`, `[:2000]` |
| **String-Slicing** | `app.py` | `e["text"][:55]`, `kat[2:]` |
| **String-Multiplikation** | `app.py` | `"●" * intensitaet + "○" * (5 - intensitaet)` |
| **Listen erstellen** | `daten.py` | `KATEGORIEN`, `erkannte = []` |
| **list.append()** | `daten.py` | `ergebnis.append(e)`, `erkannte.append(...)` |
| **List Comprehension** | `app.py` | `[e for e in woche if e.get("ist_hauptmuster")]` |
| **List Slicing** | `app.py` | `alle_eintraege[-10:]` |
| **Dictionaries** | `daten.py` | Jeder `eintrag`-Dict, `MUSTER_SIGNALE`, `stats` |
| **dict.get()** | `daten.py` | `e.get("synced", False)`, `e.get("modus", "")` |
| **Dictionary-Iteration** | `daten.py` | `for muster_key, muster_data in MUSTER_SIGNALE.items()` |
| **Sets** | `daten.py` | `tage_mit_eintrag = set()` in `berechne_streak()` |
| **Funktionen definieren** | `daten.py` | Alle 10 Funktionen mit `def` |
| **Parameter** | `daten.py` | `neuer_rueckblick_eintrag(text, kategorien, intensitaet)` |
| **Default-Parameter** | `notion_sync.py` | `os.getenv("NOTION_DATABASE_ID", "c0d...")` |
| **Rückgabewerte** | `daten.py` | `return streak`, `return ergebnis`, `return erkannte, spiegel, schritt` |
| **Tuple als Rückgabewert** | `daten.py` | `return erkannte, spiegel, schritt` |
| **Tuple-Unpacking** | `app.py` | `erkannte_signale, spiegel, schritt = daten.analysiere_akut_text(...)` |
| **Module importieren** | `app.py` | `import streamlit`, `import daten`, `import notion_sync` |
| **`for`-Schleife** | `daten.py` | Einträge iterieren, Keywords prüfen, Stats zählen |
| **Verschachtelte Schleifen** | `daten.py` | Muster-Schleife × Keyword-Schleife in `analysiere_akut_text()` |
| **`while`-Schleife** | `daten.py` | Streak-Berechnung: `while aktueller_tag in tage_mit_eintrag` |
| **`break`** | `daten.py` | Keyword-Schleife verlassen nach erstem Treffer |
| **`if / elif / else`** | überall | Eingabe-Validierung, Modus-Auswahl, Sync-Status |
| **Boolean-Werte** | `app.py` | `notion_ok`, `ist_hauptmuster`, `als_erfolg` |
| **`any()`** | `daten.py` | `any(k in MUSTER_KATEGORIEN for k in kategorien)` |
| **`in`-Operator** | `daten.py` | `if keyword in text_klein`, `if aktueller_tag in tage` |
| **`isinstance()`** | `app.py` | `isinstance(importierte, list)` bei JSON-Import |
| **`len()`** | überall | `len(alle_eintraege)`, `len(e["text"]) > 55` |
| **`reversed()`** | `app.py` | `for e in reversed(alle_eintraege[-10:])` |
| **File I/O (lesen)** | `daten.py` | `open(DATEI, "r")` + `json.load()` |
| **File I/O (schreiben)** | `daten.py` | `open(DATEI, "w")` + `json.dump()` |
| **`try / except`** | `daten.py`, `notion_sync.py` | `JSONDecodeError`, Notion-Verbindungsfehler |
| **`json`-Modul** | `daten.py` | `json.load()`, `json.dump()`, `json.dumps()` |
| **`os`-Modul** | `daten.py` | `os.path.exists()`, `os.path.dirname()`, `os.getenv()` |
| **`datetime`-Modul** | `daten.py` | `datetime.now()`, `strftime()`, `strptime()`, `timedelta` |
| **Zähler-Variable** | `daten.py` | `anzahl = 0` → `anzahl += 1` |

---

## 6. Datenformat

Jeder Eintrag wird als Python-Dictionary gespeichert und in `eintraege.json` abgelegt:

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
  "schritt": "Du musst nicht verschwinden. Du kannst bleiben.",
  "synced": true
}
```

---

## 7. Erkannte Muster (Keyword-Analyse)

Die App analysiert Freitexte lokal (kein externer KI-Service) mit Keyword-Matching:

| Muster | Beispiel-Keywords |
|---|---|
| Rückzug / Unsichtbar werden | zurückzieh, verschwind, will weg, niemand versteht |
| Kontrolle / Rechtfertigung | rechtfertig, beweise, meine schuld, kontroll |
| Leistungsdruck / Funktionieren | stress, nicht gut genug, erschöpft, ausgebrannt |
| Ungeduld / aufgestauter Schmerz | wut, genervt, unfair, nervt, macht mich wahnsinnig |
| Angst / Katastrophendenken | angst, was wenn, scheitern, herzklopfen |
| Erstarren / Blockade | weiß nicht mehr, stecke fest, total blockiert |

---

## 8. Installation und Start

```bash
# Abhängigkeiten installieren
pip install streamlit notion-client python-dotenv

# App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

**Online (Handy):** Die App ist auf Streamlit Community Cloud deployed und über eine öffentliche URL erreichbar.

---

## 9. Technische Entscheidungen

**Warum kein KI-Service für die Analyse?**  
Die Akut-Texte sind sehr persönlich. Ein externer KI-Dienst würde intime Inhalte an Server senden. Lokales Keyword-Matching schützt die Privatsphäre und ist für den Anwendungsfall ausreichend.

**Warum Offline-First?**  
Das Tool soll auch ohne Internetverbindung nutzbar sein — gerade in emotional aufgeladenen Momenten ist es wichtig, dass die App immer funktioniert.

**Warum Notion als Datenbank?**  
Notion ist bereits im täglichen Gebrauch und bietet eine übersichtliche Darstellung. Die Daten bleiben im persönlichen Workspace — kein fremder Server.
