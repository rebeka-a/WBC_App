import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Home", layout="wide")

# Zugriffsschutz: Nur eingeloggte Nutzer dürfen hierhin!
LoginManager().go_to_login('Start.py')

# Titel und Begrüßung
st.title("🏠 Home - Übersicht")

# Login-Status abfragen
data_manager = DataManager()
login_manager = LoginManager(data_manager)

if login_manager.is_logged_in():
    user = login_manager.get_current_user()
    st.success(f"Willkommen zurück, {user}! 🎉")
    
    # Benutzer-Daten laden
    data_manager.load_user_data(
        session_state_key='data_df',
        file_name='data.csv',
        initial_value=pd.DataFrame(columns=["timestamp", "counts", "gender", "birth_date"]),
        parse_dates=['timestamp']
    )
    
    # Statusanzeige
    st.markdown("### 📊 Aktueller Status:")
    if "data_df" in st.session_state and not st.session_state["data_df"].empty:
        num_entries = len(st.session_state["data_df"])
        st.info(f"Sie haben bereits **{num_entries}** Zellzählungen gespeichert.")
    else:
        st.info("Noch keine gespeicherten Zellzählungen vorhanden.")
    
    # Navigation Buttons
    st.markdown("---")
    st.markdown("### 🚀 Aktionen")
    
    if st.button("➡️ Neue Zellzählung starten", use_container_width=True):
        st.switch_page("pages/1_Weisses Blutbild.py")
        
    if st.button("📄 Ergebnisse herunterladen", use_container_width=True):
        if not st.session_state["data_df"].empty:
            csv = st.session_state["data_df"].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download als CSV",
                data=csv,
                file_name="zellzaehlungen.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("Keine Daten zum Herunterladen verfügbar.")

    # Logout
    st.markdown("---")
    if st.button("🚪 Abmelden", use_container_width=True):
        login_manager.logout()

else:
    st.error("Bitte zuerst anmelden über Startseite.")
