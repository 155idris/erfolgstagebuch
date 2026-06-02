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
    /* ── Streamlit-Elemente verstecken ───────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stDecoration"] { visibility: hidden; }
    [data-testid="stStatusWidget"] { visibility: hidden; }

    /* ── Basis ───────────────────────────────────────────────────────────── */
    .stApp { background-color: #0e0e0e; color: #f0ebe0; }
    .block-container { padding: 2rem 3rem; max-width: 1100px; }
    p, .stMarkdown p { color: #f0ebe0; }
    h1, h2, h3, h4 { color: #f0ebe0; font-family: Georgia, serif; font-weight: 300; }
    hr { border-color: #2a2a2a; }

    /* ── Metriken ────────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 1rem 1.2rem;
    }
    [data-testid="metric-container"] label {
        color: #666 !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] { color: #f0ebe0 !important; font-size: 2.4rem !important; font-weight: 700 !important; }

    /* ── Buttons ─────────────────────────────────────────────────────────── */
    .stButton > button {
        background: #c4a35a; color: #0e0e0e;
        border: none; border-radius: 24px;
        font-weight: 700; padding: 0.6rem 2rem;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #d4b36a; color: #0e0e0e; }

    /* ── Eingabefelder ───────────────────────────────────────────────────── */
    .stTextArea textarea, .stTextInput input {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        color: #f0ebe0 !important;
        border-radius: 6px;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #c4a35a !important;
        box-shadow: 0 0 0 1px #c4a35a !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0e0e0e;
        border-bottom: 1px solid #2a2a2a;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] { color: #555; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { color: #c4a35a !important; border-bottom: 2px solid #c4a35a; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #c4a35a !important; height: 2px; }

    /* ── Expander ────────────────────────────────────────────────────────── */
    .streamlit-expanderHeader { color: #888 !important; background: #141414; border-radius: 6px; }
    .streamlit-expanderContent { background: #1a1a1a; border-radius: 0 0 6px 6px; }

    /* ── Slider ──────────────────────────────────────────────────────────── */
    .stSlider [data-baseweb="slider"] [role="slider"] { background: #c4a35a; }

    /* ── Multiselect ─────────────────────────────────────────────────────── */
    [data-testid="stMultiSelect"] { background: #1a1a1a; }

    /* ── Mobile ──────────────────────────────────────────────────────────── */
    @media (max-width: 768px) {
        .block-container { padding: 1rem 1rem; }
        .stTextArea textarea { font-size: 16px !important; min-height: 120px; }
        .stTextInput input { font-size: 16px !important; }
        .stButton > button { width: 100%; font-size: 1rem; padding: 0.8rem; }
    }
</style>
""", unsafe_allow_html=True)


# ─── Hilfsfunktion: HTML-Kachel ───────────────────────────────────────────────
def kachel(titel, wert, farbe="#c4a35a", rahmen="#c4a35a", hintergrund="#1a1a1a"):
    """Gibt eine farbige Info-Kachel als HTML-String zurück.
    PCEP: Funktionen, f-Strings, String-Rückgabewert
    """
    return f"""
    <div style="background:{hintergrund};border:1px solid {rahmen};border-radius:8px;
                padding:0.8rem 1.2rem;margin-bottom:0.5rem;">
        <p style="color:{farbe};margin:0;font-size:0.72rem;text-transform:uppercase;
                  letter-spacing:0.08em;">{titel}</p>
        <p style="color:#f0ebe0;font-size:2rem;font-weight:700;margin:0;">{wert}</p>
    </div>
    """


# ─── Header ───────────────────────────────────────────────────────────────────
# PCEP: f-String für dynamisches Datum
heute_str = datetime.now().strftime("%d.%m.%Y")

# Beim Start: Notion als Quelle der Wahrheit laden (einmal pro Session)
if "sync_done" not in st.session_state:
    if notion_sync.notion_verfuegbar():
        notion_eintraege = notion_sync.lade_eintraege_von_notion()
        if notion_eintraege:
            daten._schreibe_eintraege(notion_eintraege)
    # Lokale Einträge die noch nicht in Notion sind, hochladen
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
    '<span style="color:#666;font-size:0.75rem;">○ Nur lokal</span>'
)

st.markdown(
    '<h1 style="color:#c4a35a;font-family:Georgia,serif;font-weight:300;margin-bottom:0;">'
    'eB &nbsp;<span style="color:#666;font-size:1rem;font-weight:400;">Innenspiegel</span></h1>',
    unsafe_allow_html=True
)
st.markdown(
    f'<p style="color:#444;font-size:0.85rem;margin-top:0;">'
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
if "reflexion_counter" not in st.session_state:
    st.session_state.reflexion_counter = 0
if "verlauf_zeige_n" not in st.session_state:
    st.session_state.verlauf_zeige_n = 10
if "verlauf_bearbeiten_idx" not in st.session_state:
    st.session_state.verlauf_bearbeiten_idx = None

tab1, tab2, tab3, tab4 = st.tabs([
    "⚡  Ich merke gerade etwas",
    "📖  Erfolg dokumentieren",
    "📊  Mein Fortschritt",
    "🗂️  Verlauf"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AKUT-MODUS
# Freies Schreiben → App analysiert im Hintergrund → Spiegel zurück
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Was ist gerade?")
    st.markdown(
        '<p style="color:#666;font-size:0.9rem;">'
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
            f'<div style="background:#1a1a1a;border:1px solid #c4a35a;'
            f'border-radius:10px;padding:1rem 1.4rem;margin-bottom:1rem;">'
            f'<p style="color:#c4a35a;font-size:1.05rem;margin:0;">'
            f'{erfolg["emoji"]} {erfolg["nachricht"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Spiegel ───────────────────────────────────────────────────────────
        st.markdown(
            '<p style="color:#888;font-size:0.72rem;text-transform:uppercase;'
            'letter-spacing:0.1em;">Was ich höre</p>',
            unsafe_allow_html=True
        )

        # PCEP: html.escape() — Usertext absichern vor HTML-Einbettung
        vorschau_text = html.escape(letzter_text[:120]) + ("..." if len(letzter_text) > 120 else "")
        st.markdown(
            f'<p style="color:#f0ebe0;font-style:italic;font-size:0.95rem;">'
            f'„{vorschau_text}"</p>',
            unsafe_allow_html=True
        )

        # PCEP: Conditional — Muster-Box nur wenn erkannt
        if erkannte_signale:
            # PCEP: String-Join — Liste zu kommasepariertem String
            signale_str = html.escape(", ".join(erkannte_signale))
            st.markdown(
                f'<div style="background:#1a1a1a;border:1px solid #c4a35a;'
                f'border-radius:8px;padding:1rem 1.2rem;margin:1rem 0;">'
                f'<p style="color:#c4a35a;margin:0 0 0.3rem;font-size:0.72rem;'
                f'text-transform:uppercase;letter-spacing:0.1em;">Das könnte klingen nach</p>'
                f'<p style="color:#f0ebe0;font-size:1rem;margin:0;">{signale_str}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div style="background:#141414;border-left:3px solid #c4a35a;'
            f'padding:0.8rem 1rem;margin:0.5rem 0;">'
            f'<p style="color:#f0ebe0;margin:0;">{spiegel}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div style="background:#141414;border-left:3px solid #d4b36a;'
            f'padding:0.8rem 1rem;margin:0.5rem 0;">'
            f'<p style="color:#888;margin:0 0 0.2rem;font-size:0.72rem;'
            f'text-transform:uppercase;letter-spacing:0.1em;">Eine Möglichkeit jetzt</p>'
            f'<p style="color:#f0ebe0;margin:0;">{schritt}</p>'
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
# TAB 2 — TAGESREFLEXION
# Drei Fragen die zum positiven Sehen einladen — alle optional
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Was war heute gut?")
    st.markdown(
        '<p style="color:#666;font-size:0.9rem;margin-bottom:1.5rem;">'
        'Alle Felder optional — schreib was dir in den Sinn kommt.</p>',
        unsafe_allow_html=True
    )

    # PCEP: Counter-Key — Felder leeren sich nach dem Speichern
    rc = st.session_state.reflexion_counter

    # ── Frage 1: Dankbarkeit ──────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#c4a35a;font-size:0.78rem;text-transform:uppercase;'
        'letter-spacing:0.1em;margin-bottom:0.3rem;">🙏 &nbsp;Wofür bin ich heute dankbar?</p>',
        unsafe_allow_html=True
    )
    dankbarkeit = st.text_area(
        label="Dankbarkeit",
        placeholder="Drei Momente — auch kleine zählen...",
        height=160,
        label_visibility="collapsed",
        key=f"ref_dankbarkeit_{rc}"
    )

    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

    # ── Frage 2: Freude erhalten ──────────────────────────────────────────────
    st.markdown(
        '<p style="color:#c4a35a;font-size:0.78rem;text-transform:uppercase;'
        'letter-spacing:0.1em;margin-bottom:0.3rem;">✨ &nbsp;Was hat mir heute Freude bereitet?</p>',
        unsafe_allow_html=True
    )
    freude_erhalten = st.text_area(
        label="Freude erhalten",
        placeholder="Ein Moment der sich gut angefühlt hat...",
        height=120,
        label_visibility="collapsed",
        key=f"ref_freude_erhalten_{rc}"
    )

    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

    # ── Frage 3: Freude gegeben ───────────────────────────────────────────────
    st.markdown(
        '<p style="color:#c4a35a;font-size:0.78rem;text-transform:uppercase;'
        'letter-spacing:0.1em;margin-bottom:0.3rem;">🤝 &nbsp;Wen habe ich heute Freude bereitet?</p>',
        unsafe_allow_html=True
    )
    freude_gegeben = st.text_area(
        label="Freude gegeben",
        placeholder="Jemand dem du heute etwas gegeben hast...",
        height=120,
        label_visibility="collapsed",
        key=f"ref_freude_gegeben_{rc}"
    )

    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

    # ── Freier Raum (optional) ────────────────────────────────────────────────
    st.markdown(
        '<p style="color:#555;font-size:0.78rem;text-transform:uppercase;'
        'letter-spacing:0.1em;margin-bottom:0.3rem;">📝 &nbsp;Gibt es noch etwas das du festhalten möchtest?</p>',
        unsafe_allow_html=True
    )
    freier_raum = st.text_area(
        label="Freier Raum",
        placeholder="Optional...",
        height=100,
        label_visibility="collapsed",
        key=f"ref_freier_raum_{rc}"
    )

    st.markdown("")

    if st.button("Speichern", key="reflexion_save"):
        # PCEP: any() — mindestens ein Feld muss ausgefüllt sein
        if not any([dankbarkeit, freude_erhalten, freude_gegeben, freier_raum]):
            st.warning("Füll mindestens eine Frage aus — auch ein Satz reicht.")
            st.session_state.rueckblick_letztes_ergebnis = None
        else:
            daten.neue_reflexion_eintrag(dankbarkeit, freude_erhalten, freude_gegeben, freier_raum)

            # PCEP: Conditionals — Erfolgs-Stufe aus ausgefüllten Feldern berechnen
            felder = sum(bool(f) for f in [dankbarkeit, freude_erhalten, freude_gegeben])
            if freude_gegeben:
                erfolg = daten.ERFOLGS_STUFEN[0]   # ✨ nach außen gehandelt
            elif felder == 3:
                erfolg = daten.ERFOLGS_STUFEN[1]   # 👁️ alles beantwortet
            elif felder == 2:
                erfolg = daten.ERFOLGS_STUFEN[3]   # 💛 zwei Fragen
            else:
                erfolg = daten.ERFOLG_BASIS         # 🌱 ein Moment reicht

            st.session_state.rueckblick_letztes_ergebnis = erfolg
            st.session_state.reflexion_counter += 1
            st.rerun()

    # ── Erfolgs-Moment nach Speichern ─────────────────────────────────────────
    if st.session_state.rueckblick_letztes_ergebnis:
        erfolg = st.session_state.rueckblick_letztes_ergebnis
        st.markdown(
            f'<div style="background:#1a1a1a;border:1px solid #c4a35a;'
            f'border-radius:10px;padding:1rem 1.4rem;margin-top:1rem;">'
            f'<p style="color:#c4a35a;font-size:1.05rem;margin:0;">'
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
        st.markdown(kachel("🕯️ Tage mit Kontakt", f"{streak} Tage", rahmen="#2a2a2a", hintergrund="#141414"), unsafe_allow_html=True)
    with col3:
        st.markdown(kachel("📖 Gesamt-Einträge", len(alle_eintraege), rahmen="#2a2a2a", hintergrund="#141414"), unsafe_allow_html=True)
    with col4:
        # Fix 3: "Akut-Momente" → "Präsenz-Momente" — weniger Alarm-Charakter
        st.markdown(kachel("👁️ Präsenz-Momente", akut_gesamt, rahmen="#2a2a2a", hintergrund="#141414"), unsafe_allow_html=True)

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
                               farbe="#c4a35a", rahmen="#c4a35a", hintergrund="#1a1a1a"), unsafe_allow_html=True)
        with wk3:
            st.markdown(kachel("👁️ Präsenz-Momente", len(akut_woche)), unsafe_allow_html=True)

        st.markdown("")

    pass  # Tab 3 zeigt nur Metriken und Wochenübersicht


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — VERLAUF
# Letzte Einträge ansehen und bearbeiten
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Verlauf")

    alle_eintraege = daten.lade_eintraege()
    gesamt = len(alle_eintraege)

    if not alle_eintraege:
        st.markdown(
            '<p style="color:#444;">Noch keine Einträge. Starte mit deinem ersten Moment.</p>',
            unsafe_allow_html=True
        )
    else:
        # PCEP: Slicing — nur die letzten N Einträge anzeigen
        n = st.session_state.verlauf_zeige_n
        eintraege_anzeigen = alle_eintraege[-n:]

        # PCEP: enumerate + reversed — neueste zuerst, mit echtem Index
        for i, e in enumerate(reversed(eintraege_anzeigen)):
            actual_idx = gesamt - 1 - i  # echter Index in alle_eintraege

            # PCEP: Conditional für Modus-Badge
            # PCEP: if/elif/else — Badge je nach Modus
            if e.get("modus") == "akut":
                badge = "⚡ Akut"
            elif e.get("modus") == "reflexion":
                badge = "🙏 Reflexion"
            else:
                badge = "📖 Rückblick"
            vorschau = e["text"][:55] + "..." if len(e["text"]) > 55 else e["text"]
            titel = f"{e['datum']}  {e.get('uhrzeit', '')} · {badge} · {vorschau}"

            with st.expander(titel):

                # ── Bearbeitungsmodus ─────────────────────────────────────────
                if st.session_state.verlauf_bearbeiten_idx == actual_idx:
                    neuer_text = st.text_area(
                        "Text bearbeiten",
                        value=e["text"],
                        height=150,
                        key=f"edit_text_{actual_idx}"
                    )
                    col_save, col_cancel = st.columns([1, 1])
                    with col_save:
                        if st.button("💾 Speichern", key=f"save_{actual_idx}"):
                            if neuer_text.strip():
                                daten.aktualisiere_eintrag_text(actual_idx, neuer_text)
                                st.session_state.verlauf_bearbeiten_idx = None
                                st.rerun()
                    with col_cancel:
                        if st.button("Abbrechen", key=f"cancel_{actual_idx}"):
                            st.session_state.verlauf_bearbeiten_idx = None
                            st.rerun()

                # ── Lesemodus ─────────────────────────────────────────────────
                else:
                    spalte_text, spalte_meta = st.columns([3, 1])

                    with spalte_text:
                        # PCEP: Conditional — je nach Modus unterschiedliche Anzeige
                        if e.get("modus") == "reflexion":
                            if e.get("dankbarkeit"):
                                st.markdown(f"🙏 **Dankbarkeit:** {e['dankbarkeit']}")
                            if e.get("freude_erhalten"):
                                st.markdown(f"✨ **Freude erhalten:** {e['freude_erhalten']}")
                            if e.get("freude_gegeben"):
                                st.markdown(f"🤝 **Freude gegeben:** {e['freude_gegeben']}")
                            if e.get("freier_raum"):
                                st.markdown(f"📝 {e['freier_raum']}")
                        else:
                            st.write(e["text"])

                        if e.get("modus") == "akut":
                            signale = e.get("erkannte_signale", [])
                            if signale:
                                st.markdown(f"⚡ **Könnte klingen nach:** {', '.join(signale)}")
                            spiegel_text = e.get("spiegel", "")
                            if spiegel_text:
                                st.markdown(f"🪞 **Spiegel:** {spiegel_text}")
                            schritt_text = e.get("schritt", "")
                            if schritt_text:
                                st.markdown(f"✦ **Möglicher Schritt:** {schritt_text}")

                        # PCEP: Bearbeiten-Button
                        if st.button("✏️ Bearbeiten", key=f"edit_btn_{actual_idx}"):
                            st.session_state.verlauf_bearbeiten_idx = actual_idx
                            st.rerun()

                    with spalte_meta:
                        for kat in e.get("kategorien", []):
                            ist_gold = kat in daten.MUSTER_KATEGORIEN
                            farbe = "#c4a35a" if ist_gold else "#888"
                            st.markdown(
                                f'<span style="color:{farbe};font-size:0.78rem;">{kat}</span><br>',
                                unsafe_allow_html=True
                            )
                        intensitaet = e.get("intensitaet", 0)
                        if intensitaet > 0:
                            punkte = "●" * intensitaet + "○" * (5 - intensitaet)
                            st.markdown(
                                f'<span style="color:#c4a35a;font-size:0.9rem;">{punkte}</span>',
                                unsafe_allow_html=True
                            )

        # ── Weitere laden ─────────────────────────────────────────────────────
        if gesamt > n:
            verbleibend = gesamt - n
            if st.button(f"Weitere 10 anzeigen · noch {verbleibend} Einträge"):
                st.session_state.verlauf_zeige_n += 10
                st.rerun()
