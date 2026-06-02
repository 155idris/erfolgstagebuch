# ─────────────────────────────────────────────────────────────────────────────
# app.py — Erfolgstagebuch (Streamlit-App)
# PCEP-Abschlussprojekt — Idrissa Sow
#
# PCEP-Konzepte in dieser Datei:
#   - Variablen und Datentypen (str, int, bool, list)
#   - String-Formatierung (f-Strings)
#   - Conditionals (if/elif/else)
#   - Listen und Dictionaries (Ausgabe, Iteration)
#   - Funktionsaufrufe (aus daten.py)
#   - Schleifen (for — Einträge anzeigen)
#   - Modul-Import (import streamlit, import daten)
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from datetime import datetime
import html
import json
import os

# Streamlit Secrets → Umgebungsvariablen (lokal via secrets.toml, Cloud via Web-UI)
# PCEP: try/except, os.environ, dict-ähnlicher Zugriff auf st.secrets
try:
    for key in ["NOTION_TOKEN", "NOTION_DATABASE_ID"]:
        if key in st.secrets and not os.getenv(key):
            os.environ[key] = st.secrets[key]
except Exception:
    pass  # Kein secrets.toml vorhanden → .env oder Umgebungsvariablen gelten

import daten
import notion_sync

# ─── Seitenkonfiguration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="eB — Innenspiegel",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Design (Custom CSS) ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0b0a08; }
    .block-container { padding: 2rem 3rem; max-width: 1200px; }

    /* Metriken */
    [data-testid="metric-container"] {
        background: #13110b;
        border: 1px solid #261f0e;
        border-radius: 8px;
        padding: 1rem 1.2rem;
    }
    [data-testid="metric-container"] label {
        color: #8a8070 !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] { color: #f5f0e8 !important; font-size: 2.4rem !important; font-weight: 700 !important; }

    /* Buttons */
    .stButton > button {
        background: #f59e0b; color: #0b0a08;
        border: none; border-radius: 24px;
        font-weight: 700; padding: 0.6rem 2rem;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #d97706; color: #0b0a08; }

    /* Eingabefelder */
    .stTextArea textarea, .stTextInput input {
        background: #0e0c08 !important;
        border: 1px solid #261f0e !important;
        color: #f5f0e8 !important;
        border-radius: 6px;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 1px #f59e0b !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #0b0a08;
        border-bottom: 1px solid #261f0e;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] { color: #6b5a40; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { color: #f59e0b !important; border-bottom: 2px solid #f59e0b; }

    /* Expander */
    .streamlit-expanderHeader { color: #8a8070 !important; background: #13110b; border-radius: 6px; }
    .streamlit-expanderContent { background: #0e0c08; border-radius: 0 0 6px 6px; }

    /* Trennlinien und allgemeiner Text */
    hr { border-color: #261f0e; }
    p, .stMarkdown p { color: #c8bfa8; }
    h1, h2, h3, h4 { color: #f5f0e8; }

    /* Slider */
    .stSlider [data-baseweb="slider"] [role="slider"] { background: #f59e0b; }

    /* Mobile: größere Touch-Targets, Button immer sichtbar */
    @media (max-width: 768px) {
        .block-container { padding: 1rem 1rem; }
        .stTextArea textarea { font-size: 16px !important; min-height: 120px; }
        .stTextInput input { font-size: 16px !important; }
        .stButton > button { width: 100%; font-size: 1rem; padding: 0.8rem; }
        .stMultiSelect { font-size: 15px; }
    }
</style>
""", unsafe_allow_html=True)


# ─── Hilfsfunktion: HTML-Kachel ───────────────────────────────────────────────
def kachel(titel, wert, farbe="#f59e0b", rahmen="#f59e0b", hintergrund="#1a1200"):
    """Gibt eine farbige Info-Kachel als HTML-String zurück.
    PCEP: Funktionen, f-Strings, String-Rückgabewert
    """
    return f"""
    <div style="background:{hintergrund};border:1px solid {rahmen};border-radius:8px;
                padding:0.8rem 1.2rem;margin-bottom:0.5rem;">
        <p style="color:{farbe};margin:0;font-size:0.72rem;text-transform:uppercase;
                  letter-spacing:0.08em;">{titel}</p>
        <p style="color:#f5f0e8;font-size:2rem;font-weight:700;margin:0;">{wert}</p>
    </div>
    """


# ─── Header ───────────────────────────────────────────────────────────────────
# PCEP: f-String für dynamisches Datum
heute_str = datetime.now().strftime("%d.%m.%Y")

# Ausstehende Einträge beim Start synchronisieren
if "sync_done" not in st.session_state:
    alle = daten.lade_eintraege()
    aktualisiert, gesynct = notion_sync.sync_ausstehende(alle)
    if gesynct > 0:
        daten._schreibe_eintraege(aktualisiert)
    st.session_state.sync_done = True

# Notion-Status für Anzeige
notion_ok = notion_sync.notion_verfuegbar()
notion_badge = (
    '<span style="color:#4ab86c;font-size:0.75rem;">● Notion verbunden</span>'
    if notion_ok else
    '<span style="color:#6b5a40;font-size:0.75rem;">○ Nur lokal</span>'
)

st.markdown(
    '<h1 style="color:#f59e0b;font-family:Georgia,serif;font-weight:300;margin-bottom:0;">'
    'eB &nbsp;<span style="color:#6b5a40;font-size:1rem;font-weight:400;">Innenspiegel</span></h1>',
    unsafe_allow_html=True
)
st.markdown(
    f'<p style="color:#4a4030;font-size:0.85rem;margin-top:0;">'
    f'emotionales Betriebssystem · {heute_str} &nbsp;·&nbsp; {notion_badge}</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
# PCEP: Mehrere Variablen in einer Zuweisung (Tuple-Unpacking)
# Session State initialisieren — Text bleibt erhalten beim Tab-Wechsel
if "akut_counter" not in st.session_state:
    st.session_state.akut_counter = 0
if "akut_bearbeiten" not in st.session_state:
    st.session_state.akut_bearbeiten = ""
if "akut_letzter_text" not in st.session_state:
    st.session_state.akut_letzter_text = ""
if "akut_letztes_ergebnis" not in st.session_state:
    st.session_state.akut_letztes_ergebnis = None
if "rueckblick_letztes_ergebnis" not in st.session_state:
    st.session_state.rueckblick_letztes_ergebnis = None

tab1, tab2, tab3 = st.tabs([
    "⚡  Ich merke gerade etwas",
    "📖  Erfolg dokumentieren",
    "📊  Mein Fortschritt"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AKUT-MODUS
# Freies Schreiben → App analysiert im Hintergrund → Spiegel zurück
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Was ist gerade?")
    st.markdown(
        '<p style="color:#6b5a40;font-size:0.9rem;">'
        'Einfach rausschreiben was ist. Kein Format, keine Struktur.</p>',
        unsafe_allow_html=True
    )

    # PCEP: Schlüssel enthält Counter → neues Widget = Feld geleert nach Speichern
    akut_text = st.text_area(
        label="Freies Schreiben",
        placeholder="Was passiert gerade? Was fühlst du? Was läuft ab?\n\n"
                    "Einfach schreiben — die App hört zu.",
        height=180,
        label_visibility="collapsed",
        key=f"akut_freitext_{st.session_state.akut_counter}",
        value=st.session_state.akut_bearbeiten
    )

    st.markdown("")

    if st.button("Speichern & spiegeln", key="akut_save"):
        # PCEP: Wahrheitswert eines Strings (leer = False)
        if akut_text:
            # PCEP: Tuple-Unpacking — 3 Rückgabewerte der Analysefunktion
            erkannte_signale, spiegel, schritt = daten.analysiere_akut_text(akut_text)
            daten.neuer_akut_eintrag(akut_text, erkannte_signale, spiegel, schritt)
            erfolg = daten.erkenne_erfolgs_stufe(akut_text)

            # Ergebnis in session_state speichern, Feld leeren, neu rendern
            st.session_state.akut_letzter_text = akut_text
            st.session_state.akut_letztes_ergebnis = {
                "erkannte": erkannte_signale,
                "spiegel": spiegel,
                "schritt": schritt,
                "erfolg": erfolg,
            }
            st.session_state.akut_bearbeiten = ""
            st.session_state.akut_counter += 1  # PCEP: Zähler erhöhen → neues Widget
            st.rerun()
        else:
            st.warning("Schreib etwas — auch wenn es nur ein Satz ist.")

    # ── Letztes Ergebnis anzeigen (bleibt nach Speichern sichtbar) ───────────
    if st.session_state.akut_letztes_ergebnis:
        ergebnis     = st.session_state.akut_letztes_ergebnis
        letzter_text = st.session_state.akut_letzter_text
        erkannte_signale = ergebnis["erkannte"]
        spiegel          = ergebnis["spiegel"]
        schritt          = ergebnis["schritt"]
        erfolg           = ergebnis["erfolg"]

        st.markdown("---")

        # ── Erfolgs-Moment ────────────────────────────────────────────────────
        st.markdown(
            f'<div style="background:#1a1200;border:1px solid #f59e0b;'
            f'border-radius:10px;padding:1rem 1.4rem;margin-bottom:1rem;">'
            f'<p style="color:#f59e0b;font-size:1.05rem;margin:0;">'
            f'{erfolg["emoji"]} {erfolg["nachricht"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Spiegel ───────────────────────────────────────────────────────────
        st.markdown(
            '<p style="color:#8a8070;font-size:0.72rem;text-transform:uppercase;'
            'letter-spacing:0.1em;">Was ich höre</p>',
            unsafe_allow_html=True
        )

        # PCEP: html.escape() — Usertext absichern vor HTML-Einbettung
        vorschau_text = html.escape(letzter_text[:120]) + ("..." if len(letzter_text) > 120 else "")
        st.markdown(
            f'<p style="color:#c8bfa8;font-style:italic;font-size:0.95rem;">'
            f'„{vorschau_text}"</p>',
            unsafe_allow_html=True
        )

        # PCEP: Conditional — Muster-Box nur wenn erkannt
        if erkannte_signale:
            # PCEP: String-Join — Liste zu kommasepariertem String
            signale_str = html.escape(", ".join(erkannte_signale))
            st.markdown(
                f'<div style="background:#1a1200;border:1px solid #f59e0b;'
                f'border-radius:8px;padding:1rem 1.2rem;margin:1rem 0;">'
                f'<p style="color:#f59e0b;margin:0 0 0.3rem;font-size:0.72rem;'
                f'text-transform:uppercase;letter-spacing:0.1em;">Das könnte klingen nach</p>'
                f'<p style="color:#f5f0e8;font-size:1rem;margin:0;">{signale_str}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div style="background:#0e0c08;border-left:3px solid #f59e0b;'
            f'padding:0.8rem 1rem;margin:0.5rem 0;">'
            f'<p style="color:#c8bfa8;margin:0;">{spiegel}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div style="background:#140f00;border-left:3px solid #d97706;'
            f'padding:0.8rem 1rem;margin:0.5rem 0;">'
            f'<p style="color:#8a8070;margin:0 0 0.2rem;font-size:0.72rem;'
            f'text-transform:uppercase;letter-spacing:0.1em;">Eine Möglichkeit jetzt</p>'
            f'<p style="color:#c8bfa8;margin:0;">{schritt}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("")

        # ── Bearbeiten-Button ─────────────────────────────────────────────────
        if st.button("✏️ Text bearbeiten", key="akut_bearbeiten_btn"):
            st.session_state.akut_bearbeiten = letzter_text
            st.session_state.akut_letztes_ergebnis = None
            st.session_state.akut_counter += 1
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RÜCKBLICK
# Abendlicher oder nachträglicher Erfolgs-Eintrag
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Was ist heute gelungen?")

    # PCEP: Variablen für Eingabewerte
    text = st.text_area(
        label="Erfolg beschreiben",
        placeholder="Beschreibe den Moment — was du wahrgenommen, erkannt oder anders gewählt hast...",
        height=130,
        label_visibility="collapsed"
    )

    st.markdown(
        '<p style="color:#8a8070;font-size:0.75rem;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-top:0.5rem;">Kategorien (Mehrfachauswahl möglich)</p>',
        unsafe_allow_html=True
    )

    # PCEP: Rückgabe ist eine Liste der gewählten Strings
    kategorien = st.multiselect(
        label="Kategorien",
        options=daten.KATEGORIEN,
        label_visibility="collapsed"
    )

    # PCEP: any() + Membership-Test (in) — prüft ob mindestens eine Muster-Kategorie gewählt
    if any(k in daten.MUSTER_KATEGORIEN for k in kategorien):
        st.markdown(
            '<div style="background:#1a1200;border:1px solid #f59e0b;border-radius:6px;'
            'padding:0.6rem 1rem;margin:0.5rem 0;">'
            '<p style="color:#f59e0b;margin:0;font-size:0.85rem;">⚡ Hauptmuster-Moment erkannt.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    # PCEP: Integer-Variable aus Slider (Wertebereich 1–5)
    intensitaet = st.slider(
        "Intensität dieses Moments",
        min_value=1, max_value=5, value=3,
        help="Wie bedeutsam war dieser Moment für dich?"
    )

    st.markdown("")

    if st.button("Erfolg speichern", key="rueckblick_save"):
        # PCEP: Mehrfach-Conditional zur Eingabe-Validierung
        if not text:
            st.warning("Bitte beschreibe den Erfolg.")
            st.session_state.rueckblick_letztes_ergebnis = None
        elif not kategorien:
            st.warning("Bitte wähle mindestens eine Kategorie.")
            st.session_state.rueckblick_letztes_ergebnis = None
        else:
            daten.neuer_rueckblick_eintrag(text, kategorien, intensitaet)
            erfolg = daten.erkenne_erfolgs_stufe(text, kategorien)
            st.session_state.rueckblick_letztes_ergebnis = erfolg

    # ── Erfolgs-Moment nach Speichern ─────────────────────────────────────────
    if st.session_state.rueckblick_letztes_ergebnis:
        erfolg = st.session_state.rueckblick_letztes_ergebnis
        st.markdown(
            f'<div style="background:#1a1200;border:1px solid #f59e0b;'
            f'border-radius:10px;padding:1rem 1.4rem;margin-top:1rem;">'
            f'<p style="color:#f59e0b;font-size:1.05rem;margin:0;">'
            f'{erfolg["emoji"]} {erfolg["nachricht"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD / FORTSCHRITT
# Übersicht aller Einträge, Statistiken, Verlauf
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    # PCEP: Funktionsaufrufe — Ergebnisse in Variablen speichern
    alle_eintraege = daten.lade_eintraege()
    woche          = daten.eintraege_diese_woche(alle_eintraege)
    streak         = daten.berechne_streak(alle_eintraege)
    hm_gesamt      = daten.hauptmuster_count(alle_eintraege)
    akut_gesamt    = daten.akut_count(alle_eintraege)

    # ── Metriken ─────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(kachel("⚡ Hauptmuster erkannt", hm_gesamt), unsafe_allow_html=True)
    with col2:
        # Fix 3: "Streak" → "Tage mit Kontakt" — kein Habit-Tracker-Vibe
        st.markdown(kachel("🕯️ Tage mit Kontakt", f"{streak} Tage", rahmen="#261f0e", hintergrund="#13110b"), unsafe_allow_html=True)
    with col3:
        st.markdown(kachel("📖 Gesamt-Einträge", len(alle_eintraege), rahmen="#261f0e", hintergrund="#13110b"), unsafe_allow_html=True)
    with col4:
        # Fix 3: "Akut-Momente" → "Präsenz-Momente" — weniger Alarm-Charakter
        st.markdown(kachel("👁️ Präsenz-Momente", akut_gesamt, rahmen="#261f0e", hintergrund="#13110b"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Muster-Momente diese Woche ────────────────────────────────────────────
    if woche:
        st.markdown("#### Muster-Momente diese Woche")

        # PCEP: List Comprehension — gefilterte Teillisten erstellen
        muster_woche   = [e for e in woche if e.get("ist_hauptmuster")]
        neues_verhalten = [e for e in woche if "🌱 Neues Verhalten gewählt — Muster nicht gefolgt" in e.get("kategorien", [])]
        akut_woche     = [e for e in woche if e.get("modus") == "akut"]

        wk1, wk2, wk3 = st.columns(3)
        with wk1:
            st.markdown(kachel("⚡ Hauptmuster erkannt", len(muster_woche)), unsafe_allow_html=True)
        with wk2:
            st.markdown(kachel("🌱 Neues Verhalten gewählt", len(neues_verhalten),
                               farbe="#f59e0b", rahmen="#f59e0b", hintergrund="#1a1200"), unsafe_allow_html=True)
        with wk3:
            st.markdown(kachel("👁️ Präsenz-Momente", len(akut_woche)), unsafe_allow_html=True)

        st.markdown("")

    # ── Kategorien-Chart ──────────────────────────────────────────────────────
    stats = daten.kategorie_stats(alle_eintraege)

    if stats:
        st.markdown("#### Kategorien gesamt")

        # PCEP: Dictionary-Iteration, String-Slicing für kurze Labels
        chart_daten = {}
        for kat, anzahl in stats.items():
            # Emoji + langen Text kürzen für lesbare Chart-Achse
            kurz = kat[2:].strip() if len(kat) > 2 else kat
            kurz = kurz[:28] + "…" if len(kurz) > 28 else kurz
            chart_daten[kurz] = anzahl

        st.bar_chart(chart_daten)

    st.markdown("---")

    # ── Letzte Einträge ───────────────────────────────────────────────────────
    st.markdown("#### Letzte Einträge")

    if not alle_eintraege:
        st.markdown(
            '<p style="color:#4a4030;">Noch keine Einträge. Starte mit deinem ersten Moment.</p>',
            unsafe_allow_html=True
        )
    else:
        # PCEP: reversed() + Slicing — neueste 10 Einträge, neueste zuerst
        for e in reversed(alle_eintraege[-10:]):

            # PCEP: Conditional für Modus-Badge
            if e.get("modus") == "akut":
                badge = "⚡ Akut-Moment"
            else:
                badge = "📖 Rückblick"

            # PCEP: f-String + String-Slicing für Vorschau-Text
            vorschau = e["text"][:55] + "..." if len(e["text"]) > 55 else e["text"]
            titel = f"{e['datum']}  {e.get('uhrzeit', '')} · {badge} · {vorschau}"

            with st.expander(titel):
                spalte_text, spalte_meta = st.columns([3, 1])

                with spalte_text:
                    # Fix 5: st.write statt markdown mit f-string — kein ungeplantes Markdown
                    st.write(f"**{e['text']}**")

                    # Fix 1: neue Akut-Felder anzeigen (erkannte_signale, spiegel, schritt)
                    if e.get("modus") == "akut":
                        signale = e.get("erkannte_signale", [])
                        if signale:
                            # PCEP: String-Join — Liste zu lesbarem Text
                            st.markdown(f"⚡ **Könnte klingen nach:** {', '.join(signale)}")
                        spiegel_text = e.get("spiegel", "")
                        if spiegel_text:
                            st.markdown(f"🪞 **Spiegel:** {spiegel_text}")
                        schritt_text = e.get("schritt", "")
                        if schritt_text:
                            st.markdown(f"✦ **Möglicher Schritt:** {schritt_text}")

                with spalte_meta:
                    # PCEP: for-Schleife über eine Liste von Strings
                    for kat in e.get("kategorien", []):
                        ist_gold = kat in daten.MUSTER_KATEGORIEN
                        farbe = "#f59e0b" if ist_gold else "#8a8070"
                        st.markdown(
                            f'<span style="color:{farbe};font-size:0.78rem;">{kat}</span><br>',
                            unsafe_allow_html=True
                        )

                    # PCEP: Conditional + String-Multiplikation für Intensitäts-Punkte
                    intensitaet = e.get("intensitaet", 0)
                    if intensitaet > 0:
                        punkte = "●" * intensitaet + "○" * (5 - intensitaet)
                        st.markdown(
                            f'<span style="color:#f59e0b;font-size:0.9rem;">{punkte}</span>',
                            unsafe_allow_html=True
                        )

    # ── Daten-Export + Import ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Daten sichern")

    col_dl, col_ul = st.columns(2)

    with col_dl:
        if alle_eintraege:
            # PCEP: json.dumps() — Liste → String für Download
            json_string = json.dumps(alle_eintraege, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Einträge herunterladen",
                data=json_string,
                file_name=f"erfolgstagebuch_{heute_str.replace('.', '-')}.json",
                mime="application/json"
            )

    with col_ul:
        upload = st.file_uploader(
            "⬆️ Einträge importieren (.json)",
            type=["json"],
            label_visibility="collapsed"
        )
        if upload is not None:
            # Fix 4: Bestätigung bevor bestehende Daten überschrieben werden
            bestaetigt = st.checkbox(
                "Ich weiß, dass bestehende Einträge dabei ersetzt werden.",
                key="import_confirm"
            )
            if bestaetigt:
                try:
                    importierte = json.load(upload)
                    if isinstance(importierte, list):
                        daten._schreibe_eintraege(importierte)
                        st.success(f"{len(importierte)} Einträge importiert.")
                        st.rerun()
                    else:
                        st.error("Ungültiges Format — erwartet eine JSON-Liste.")
                except json.JSONDecodeError:
                    st.error("Datei konnte nicht gelesen werden.")
