import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

# Initialize the data manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="WBC_Data")  # switch drive

# Login-Logik
login_manager = LoginManager(data_manager)
login_manager.login_register()

# --- Main Page Content ---
st.title("Blood Cell Counter")

st.write(
    "Willkommen in der Blood Cell Counter App! "
    "Diese Anwendung unterstützt Sie dabei, weiße und rote Blutzellen schnell und intuitiv zu zählen, "
    "morphologische Auffälligkeiten effizient zu dokumentieren, Ihre Ergebnisse direkt mit Referenzwerten zu vergleichen "
    "und patientenspezifische Befunde sicher zu speichern und zu verwalten. "
    "Ob für die klinische Diagnostik, zu Ausbildungszwecken oder in der Forschung – diese App bietet Ihnen einen einfachen, "
    "strukturierten und sicheren Workflow für hämatologische Bewertungen.\n\n"
    "Funktionen:\n"
    "- Schnelle Blutzellzählung mit direkter grafischer Rückmeldung\n"
    "- Automatischer Abgleich mit Referenzbereichen\n"
    "- Morphologische Beurteilung roter Blutzellen\n"
    "- Sicheres Login und persönliche Datenspeicherung\n"
    "- Export aller Ergebnisse als CSV-Datei\n\n"
    "Wichtig:\n"
    "- Bitte zuerst registrieren oder anmelden, um alle Funktionen nutzen zu können.\n"
    "- Alle Ihre Daten werden sicher und personenbezogen gespeichert.\n"
    "- Bei Fragen oder Feedback wenden Sie sich gerne an das Entwicklerteam."
)

# Load the data from the persistent storage into the session state
data_manager.load_user_data(
    session_state_key='data_df',
    file_name='data.csv',
    initial_value=pd.DataFrame(columns=["timestamp", "counts", "gender", "birth_date"]),
    parse_dates=['timestamp']
)

# Navigation über separate Seiten
