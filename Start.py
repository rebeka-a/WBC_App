import streamlit as st
import pandas as pd
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from PIL import Image
import base64
from io import BytesIO

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Startseite", layout="wide")

# Hilfsfunktion: Bild in base64 umwandeln
def logo_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Logo laden und als HTML anzeigen (responsiv)
logo = Image.open("images/logo.png")
encoded_logo = logo_to_base64(logo)

st.markdown(
    f"""
    <style>
        @media (max-width: 768px) {{
            .logo-img {{
                width: 50px !important;
                height: auto !important;
                margin: auto;
                display: block;
            }}
        }}

        @media (min-width: 769px) {{
            .logo-img {{
                width: 160px !important;
                height: auto !important;
                margin-left: 0px;
            }}
        }}
    </style>

    <img class="logo-img" src="data:image/png;base64,{encoded_logo}" alt="Logo" />
    """,
    unsafe_allow_html=True
)

# --- DataManager und LoginManager initialisieren ---
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="WBC_Data")
login_manager = LoginManager(data_manager)

# --- Einführung ---
st.markdown("""Willkommen zur **Blood Cell Counter App**.

Diese Anwendung wurde speziell entwickelt, Studierende und Laborfachpersonal im Bereich der Hämatologie bei der umfassenden Analyse von Blutproben effizient und zuverlässig zu unterstützen. Der Fokus liegt auf der Erfassung und Auswertung der weißen und roten Blutzellen sowie auf der strukturierten Dokumentation morphologischer Zellveränderungen. Durch den integrierten Vergleich der Ergebnisse mit Referenzbereichen können Diagnoseprozesse wesentlich beschleunigt und qualitativ verbessert werden.

**Funktionsübersicht:**
            
🩸 Strukturierte und benutzerfreundliche Erfassung sowie manuelle Zählung weißer und roter Blutzellen  
🩸 Systematische Dokumentation und Bewertung von morphologischen Veränderungen in Blutausstrichen  
🩸 Alters- und geschlechtsspezifische Referenzbereiche zur präzisen Beurteilung der erfassten Zellpopulationen  
🩸 Sichere Speicherung, Archivierung und Verwaltung individueller Patientendaten zur kontinuierlichen Verlaufskontrolle  
🩸 Übersichtliche Darstellung aller erfassten Befunde sowie die Möglichkeit des Exports zur weiteren Analyse oder Archivierung  

**Wichtige Hinweise:**  
            
🩸 Um die vollständige Funktionalität der Blood Cell Counter App nutzen zu können, ist eine Anmeldung erforderlich.  
🩸 Alle eingegebenen Informationen werden lokal oder innerhalb eines sicheren Servers verarbeitet und gespeichert.  

---
""")

# --- Anmeldung / Benutzerbereich ---
if st.session_state.get("authentication_status"):
    user = st.session_state.get("username", "Unbekannter Benutzer")

    with st.container():
        st.success(f"Angemeldet als: **{user}**")

    # --- Buttons für Weisses & Rotes Blutbild nebeneinander ---
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Zum Weissen Blutbild", use_container_width=True):
            st.switch_page("pages/1_Weisses Blutbild.py")

    with col2:
        if st.button("Zum Roten Blutbild", use_container_width=True):
            st.switch_page("pages/2_Rotes Blutbild.py")

    st.markdown("")  # Abstand

    # --- Logout Button (Standard mit Streamlit Authenticator) ---
    login_manager.authenticator.logout("Logout", "main")

    # --- Daten laden nach Login ---
    try:
        if "data_df" not in st.session_state:
            with st.spinner("Lade Benutzerdaten..."):
                data_manager.load_user_data(
                    session_state_key='data_df',
                    file_name='data.csv',
                    initial_value=pd.DataFrame(columns=["timestamp", "counts", "gender", "birth_date"]),
                    parse_dates=['timestamp']
                )
    except Exception as e:
        st.error(f"Fehler beim Laden der Nutzerdaten: {e}")

# --- Nicht eingeloggt ---
else:
    with st.container():
        st.info("Bitte melden Sie sich an oder registrieren Sie sich, um auf die Funktionen der Blood Cell Counter App zugreifen zu können.")
        login_manager.login_register()
