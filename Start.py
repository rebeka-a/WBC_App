import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager


# Titel der App
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

st.sidebar.image("images/logo-bloodcell-counter.png.jpg", use_container_width=True)

# Initialize the data manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="WBC_Data")  # switch drive

# Login-Logik
login_manager = LoginManager(data_manager)
login_manager.login_register()

data_manager.load_user_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value=pd.DataFrame(),
    parse_dates=['timestamp']
)

# Titel der App
st.title("Blood Cell Counter 🧮")

# --- Ausführliche Einführung ---
st.markdown("""
Willkommen zur **Blood Cell Counter App**.

Diese Anwendung wurde speziell entwickelt, Studierende und Laborfachpersonal im Bereich der Hämatologie bei der umfassenden Analyse von Blutproben effizient und zuverlässig zu unterstützen. Der Fokus liegt auf der Erfassung und Auswertung der weißen und roten Blutzellen sowie auf der strukturierten Dokumentation morphologischer Zellveränderungen. Durch den integrierten Vergleich der Ergebnisse mit Referenzbereichen können Diagnoseprozesse wesentlich beschleunigt und qualitativ verbessert werden.

**Funktionsübersicht:**

🩸 Strukturierte und benutzerfreundliche Erfassung sowie manuelle Zählung weisser und roter Blutzellen  
🩸 Systematische Dokumentation und Bewertung von morphologischen Veränderungen in Blutausstrichen  
🩸 Alters- und geschlechtsspezifische Referenzbereiche zur präzisen Beurteilung der erfassten Zellpopulationen  
🩸 Sichere Speicherung, Archivierung und Verwaltung individueller Patientendaten zur kontinuierlichen Verlaufskontrolle  
🩸 Übersichtliche Darstellung aller erfassten Befunde sowie die Möglichkeit des Exports zur weiteren Analyse oder Archivierung  

**Wichtige Hinweise:**  
            
🩸 Um die vollständige Funktionalität der Blood Cell Counter App nutzen zu können, ist eine Anmeldung erforderlich. Neue Nutzer haben die Möglichkeit, ein Benutzerkonto direkt innerhalb der Anwendung zu erstellen.  
🩸 Alle eingegebenen Informationen werden ausschliesslich lokal oder innerhalb eines sicheren, geschützten Servers verarbeitet und gespeichert.  

---
            
""")

# --- Anmeldung oder Logout Bereich ---
if st.session_state.get("authentication_status"):
    user = st.session_state.get("username", "Unbekannter Benutzer")

    with st.container():
        st.success(f"Angemeldet als: **{user}**")

    # --- Button to switch to "Weisses Blutbild" page ---
    if st.button("Weisses Blutbild"):
        st.switch_page("pages/1_Weisses Blutbild.py")

    # --- Logout button ---
    if st.button("Logout", key="logout_button", use_container_width=True):
        login_manager.authenticator.logout()
        st.experimental_rerun()

# Load the data from the persistent storage into the session state



# Navigation über separate Seiten