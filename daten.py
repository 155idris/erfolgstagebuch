# ─────────────────────────────────────────────────────────────────────────────
# daten.py — Datenschicht des Erfolgstagebuchs
# Alle Funktionen zum Lesen, Schreiben und Auswerten der Einträge.
#
# PCEP-Konzepte in dieser Datei:
#   - Funktionen (def)
#   - Listen und List-Operationen
#   - Dictionaries
#   - File I/O (open, json.load, json.dump)
#   - Schleifen (for)
#   - Conditionals (if/else)
#   - Datum/Zeit-Modul (datetime)
#   - String-Methoden
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
from datetime import datetime, timedelta
import notion_sync  # PCEP: eigenes Modul importieren

# Pfad zur JSON-Datei (im gleichen Ordner wie dieses Skript)
DATEI = os.path.join(os.path.dirname(__file__), "eintraege.json")

# ─── Konstanten ───────────────────────────────────────────────────────────────

# PCEP: Liste mit String-Elementen
KATEGORIEN = [
    "⚡ Hauptmuster erkannt (im Moment)",
    "🪞 Hauptmuster erkannt (beim Reflektieren)",
    "🌱 Neues Verhalten gewählt — Muster nicht gefolgt",
    "👁️ Gefühl wahrgenommen",
    "🏷️ Gefühl benannt",
    "🤝 Gefühl angenommen",
    "🔄 Gefühl verarbeitet / transformiert",
]

# PCEP: Set für schnelle Mitgliedschaftsprüfung
MUSTER_KATEGORIEN = {
    "⚡ Hauptmuster erkannt (im Moment)",
    "🪞 Hauptmuster erkannt (beim Reflektieren)",
    "🌱 Neues Verhalten gewählt — Muster nicht gefolgt",
}

# PCEP: Dictionary of Dictionaries — Signal-Wörter → Muster-Profil
# Jedes Muster hat: keywords (Liste), name, spiegel, schritt
MUSTER_SIGNALE = {
    "rueckzug": {
        "keywords": ["zurückzieh", "verschwind", "versteck", "schweig",
                     "rückzug", "unsichtbar", "will weg", "ganz allein",
                     "niemand versteht", "lass mich", "bin nicht da", "zieh mich"],
        "name": "Rückzug / Unsichtbar werden",
        "spiegel": "Das könnte nach dem Rückzugsmuster klingen — etwas in dir will gerade verschwinden.",
        "schritt": "Du musst nicht verschwinden. Du kannst bleiben — auch wenn es sich falsch anfühlt.",
    },
    "kontrolle": {
        "keywords": ["rechtfertig", "erklär", "beweise", "kontroll",
                     "darf nicht", "falsch machen", "meine schuld", "hab einen fehler"],
        "name": "Kontrolle / Rechtfertigung",
        "spiegel": "Das könnte nach dem Kontrollmuster klingen — alles erklären, beweisen, unter Kontrolle halten.",
        "schritt": "Du musst dich nicht beweisen. Was wäre, wenn du einfach da sein dürftest?",
    },
    "druck": {
        # Fix 4: "muss", "soll" entfernt — zu breit. Nur in Kombination sinnvoll
        "keywords": ["unter druck", "so viel druck", "stress", "funktionier",
                     "nicht gut genug", "leistung", "versag", "ich schaffe das nicht",
                     "erschöpft", "ausgebrannt", "leer", "keine kraft", "überwältigt"],
        "name": "Leistungsdruck / Funktionieren",
        "spiegel": "Das könnte nach dem Leistungsmuster klingen — das Gefühl, nicht genug zu sein.",
        "schritt": "Dieser Druck ist nicht die Wahrheit. Er ist ein altes Signal — kein Fakt.",
    },
    "wut": {
        "keywords": ["wut", "genervt", "ärgert mich", "unfair", "ungerecht",
                     "warum immer", "wütend", "könnt kotzen",
                     "nervt", "macht mich wahnsinnig", "so ein mist", "bringt mich auf"],
        "name": "Ungeduld / aufgestauter Schmerz",
        "spiegel": "Das könnte nach aufgestautem Schmerz klingen — Wut ist oft ein Signal, dass etwas Tieferes gehört werden will.",
        "schritt": "Was verletzt dich gerade wirklich — nicht das Äußere, sondern das Innere?",
    },
    "angst": {
        # Fix 4: "passiert", "schlimm" entfernt — zu allgemein
        "keywords": ["angst", "sorge", "was wenn", "verlier", "scheitern",
                     "furcht", "erschreck", "geht schief",
                     "herzklopfen", "zittern", "magen", "und wenn das", "und wenn ich"],
        "name": "Angst / Katastrophendenken",
        "spiegel": "Das könnte nach dem Angstmuster klingen — worst-case-Szenarien, die das Muster malt.",
        "schritt": "Was ist gerade, in diesem Moment, wirklich wahr? Nur dieser eine Moment.",
    },
    "erstarren": {
        "keywords": ["weiß nicht mehr", "keine ahnung mehr", "festgefroren", "kann nicht mehr",
                     "stecke fest", "total blockiert", "lähmung", "paralys"],
        "name": "Erstarren / Blockade",
        "spiegel": "Das könnte nach dem Erstarrungs-Muster klingen — einfrieren als alte Schutzreaktion.",
        "schritt": "Du musst nicht sofort alles wissen. Ein kleiner Schritt reicht — welcher wäre das?",
    },
}


# ─── File I/O Funktionen ──────────────────────────────────────────────────────

def lade_eintraege():
    """Liest alle gespeicherten Einträge aus der JSON-Datei.

    PCEP-Konzepte: File I/O (open/read), json.load, Conditionals, Listen
    Rückgabe: Liste mit Dictionaries (ein Dict pro Eintrag)
    """
    # PCEP: Conditional — Datei existiert noch nicht beim ersten Start
    if not os.path.exists(DATEI):
        return []  # Leere Liste zurückgeben

    # PCEP: File I/O + Fehlerbehandlung (try/except)
    try:
        with open(DATEI, "r", encoding="utf-8") as datei:
            return json.load(datei)
    except json.JSONDecodeError:
        return []  # Kaputte Datei → leere Liste, kein Absturz


def _schreibe_eintraege(eintraege):
    """Schreibt die gesamte Eintrags-Liste in die JSON-Datei.

    PCEP-Konzepte: File I/O (open/write), json.dump
    Parameter: eintraege — Liste mit allen Eintrags-Dictionaries
    """
    # PCEP: File I/O — Datei öffnen und schreiben
    with open(DATEI, "w", encoding="utf-8") as datei:
        json.dump(eintraege, datei, ensure_ascii=False, indent=2)


# ─── Einträge erstellen ───────────────────────────────────────────────────────

def neuer_rueckblick_eintrag(text, kategorien, intensitaet):
    """Erstellt und speichert einen Rückblick-Eintrag.

    PCEP-Konzepte: Funktionen mit Parametern, Dictionaries, any(), datetime
    Parameter:
        text        — Beschreibung des Erfolgs (String)
        kategorien  — gewählte Kategorien (Liste)
        intensitaet — Bedeutsamkeit 1–5 (Integer)
    """
    # PCEP: any() + Generator-Ausdruck — prüft ob eine Muster-Kategorie gewählt wurde
    ist_hauptmuster = any(k in MUSTER_KATEGORIEN for k in kategorien)

    # PCEP: Dictionary — strukturierter Datensatz
    eintrag = {
        "datum":             datetime.now().strftime("%d.%m.%Y"),
        "uhrzeit":           datetime.now().strftime("%H:%M"),
        "modus":             "rueckblick",
        "text":              text,
        "kategorien":        kategorien,
        "ist_hauptmuster":   ist_hauptmuster,
        "intensitaet":       intensitaet,
        # Akut-Felder werden leer mitgespeichert für konsistentes Datenmodell
        "koerpergefuehl":    "",
        "muster_impuls":     "",
        "erkanntes_muster":  "",
        "freier_schritt":    "",
    }

    # PCEP: Funktion aufrufen, Liste erweitern (append), File I/O
    eintraege = lade_eintraege()
    eintrag["synced"] = False
    eintraege.append(eintrag)
    _schreibe_eintraege(eintraege)

    if notion_sync.sync_eintrag(eintrag):
        eintraege[-1]["synced"] = True
        _schreibe_eintraege(eintraege)


def analysiere_akut_text(text):
    """Analysiert einen freien Akut-Text auf Muster-Signale.

    PCEP-Konzepte: Schleifen, Dictionaries, String-Methoden (lower, in),
                   Listen (append), Conditionals, Rückgabe mehrerer Werte
    Parameter: text — freier Eingabetext (String)
    Rückgabe:  Tuple (erkannte_signale: List, spiegel: str, schritt: str)
    """
    # PCEP: String-Methode lower() — Groß-/Kleinschreibung ignorieren
    text_klein = text.lower()

    erkannte = []  # PCEP: leere Liste für gefundene Muster

    # PCEP: verschachtelte Schleifen — äußere über Muster, innere über Keywords
    for muster_key, muster_data in MUSTER_SIGNALE.items():
        for keyword in muster_data["keywords"]:
            # PCEP: in-Operator für Substring-Suche
            if keyword in text_klein:
                erkannte.append(muster_data["name"])
                break  # PCEP: Schleife abbrechen sobald ein Treffer gefunden

    # PCEP: Conditional — Rückgabewert abhängig von Ergebnis
    if erkannte:
        # Erstes erkanntes Muster für Spiegel nutzen
        erstes = erkannte[0]
        for muster_data in MUSTER_SIGNALE.values():
            if muster_data["name"] == erstes:
                spiegel = muster_data["spiegel"]
                schritt = muster_data["schritt"]
                break
    else:
        spiegel = "Du hast hingeschaut. Das zählt."
        schritt = "Manchmal ist Benennen genug. Kein Muster muss sofort gelöst werden."

    return erkannte, spiegel, schritt  # PCEP: Tuple als Rückgabewert


def neuer_akut_eintrag(text, erkannte_signale, spiegel, schritt):
    """Erstellt und speichert einen Akut-Modus-Eintrag.

    PCEP-Konzepte: Funktionen, Dictionaries, Listen, Conditionals, datetime
    Parameter:
        text             — freier Eingabetext (String)
        erkannte_signale — Liste der erkannten Muster-Namen
        spiegel          — generierter Spiegel-Text (String)
        schritt          — vorgeschlagener freier Schritt (String)  ← Fix 1
    """
    # Fix 2: Kategorie und ist_hauptmuster abhängig davon ob etwas erkannt wurde
    if erkannte_signale:
        kategorien = ["⚡ Hauptmuster erkannt (im Moment)"]
        ist_hauptmuster = True
    else:
        kategorien = ["👁️ Gefühl wahrgenommen"]  # Hinschauen zählt auch ohne Treffer
        ist_hauptmuster = False

    eintrag = {
        "datum":             datetime.now().strftime("%d.%m.%Y"),
        "uhrzeit":           datetime.now().strftime("%H:%M"),
        "modus":             "akut",
        "text":              text,
        "kategorien":        kategorien,
        "ist_hauptmuster":   ist_hauptmuster,
        "intensitaet":       0,
        "erkannte_signale":  erkannte_signale,
        "spiegel":           spiegel,
        "schritt":           schritt,  # Fix 1: jetzt gespeichert
    }

    eintraege = lade_eintraege()
    eintrag["synced"] = False
    eintraege.append(eintrag)
    _schreibe_eintraege(eintraege)

    if notion_sync.sync_eintrag(eintrag):
        eintraege[-1]["synced"] = True
        _schreibe_eintraege(eintraege)


# ─── Auswertungs-Funktionen ───────────────────────────────────────────────────

def berechne_streak(eintraege):
    """Berechnet aufeinanderfolgende Tage mit mindestens einem Eintrag.

    PCEP-Konzepte: Schleifen (while), Conditionals, datetime, Sets, timedelta
    Parameter: eintraege — Liste aller Eintrags-Dictionaries
    Rückgabe:  Anzahl Tage als Integer
    """
    # PCEP: Frühzeitiger Rückgabewert bei leerer Liste
    if not eintraege:
        return 0

    # PCEP: Set — sammelt alle Tage mit Eintrag (keine Duplikate)
    tage_mit_eintrag = set()
    for e in eintraege:
        try:
            # PCEP: String → datetime-Objekt umwandeln
            tag = datetime.strptime(e["datum"], "%d.%m.%Y").date()
            tage_mit_eintrag.add(tag)
        except ValueError:
            continue  # PCEP: Fehlerhafte Datumstrings überspringen

    heute = datetime.now().date()
    streak = 0
    aktueller_tag = heute

    # PCEP: while-Schleife — rückwärts durch Tage iterieren
    while aktueller_tag in tage_mit_eintrag:
        streak += 1
        aktueller_tag -= timedelta(days=1)  # PCEP: timedelta für Datums-Arithmetik

    return streak


def eintraege_diese_woche(eintraege):
    """Gibt nur Einträge der letzten 7 Tage zurück.

    PCEP-Konzepte: Schleifen, Conditionals, datetime, Listen (append)
    Rückgabe: gefilterte Liste
    """
    heute = datetime.now().date()
    vor_7_tagen = heute - timedelta(days=7)

    # PCEP: Neue Liste aufbauen mit Schleife + Conditional
    ergebnis = []
    for e in eintraege:
        try:
            datum = datetime.strptime(e["datum"], "%d.%m.%Y").date()
            if datum >= vor_7_tagen:
                ergebnis.append(e)
        except ValueError:
            continue

    return ergebnis


def kategorie_stats(eintraege):
    """Zählt Vorkommen jeder Kategorie über alle Einträge.

    PCEP-Konzepte: Dictionaries, verschachtelte Schleifen, Conditionals
    Rückgabe: Dictionary {Kategorie: Anzahl}
    """
    # PCEP: Leeres Dictionary, das schrittweise befüllt wird
    stats = {}

    for e in eintraege:
        # PCEP: dict.get() mit Default-Wert
        for kat in e.get("kategorien", []):
            if kat in stats:
                stats[kat] += 1   # PCEP: Dictionary-Wert erhöhen
            else:
                stats[kat] = 1    # PCEP: Neuen Schlüssel anlegen

    return stats


def hauptmuster_count(eintraege):
    """Zählt alle Einträge mit Hauptmuster-Bezug.

    PCEP-Konzepte: Schleife, Conditional, Zähler-Variable, dict.get()
    Rückgabe: Integer
    """
    anzahl = 0  # PCEP: Zähler-Variable
    for e in eintraege:
        if e.get("ist_hauptmuster", False):  # PCEP: dict.get() mit Default
            anzahl += 1
    return anzahl


def akut_count(eintraege):
    """Zählt alle Akut-Modus-Einträge.

    PCEP-Konzepte: Schleife, Conditional, Vergleichsoperator
    Rückgabe: Integer
    """
    anzahl = 0
    for e in eintraege:
        if e.get("modus") == "akut":
            anzahl += 1
    return anzahl
