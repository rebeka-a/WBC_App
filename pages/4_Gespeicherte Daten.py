import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Gespeicherte Ergebnisse", layout="wide")

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Titel
st.title("Übersicht der gespeicherten Ergebnisse")

# DataManager initialisieren
data_manager = DataManager()

# Gespeicherte Daten laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

# Hilfsfunktion: Eintrag löschen
def delete_entry(timestamp):
    df = st.session_state['data_df']
    df = df[df['timestamp'] != timestamp]  # Alle behalten außer diesen
    st.session_state['data_df'] = df
    data_manager.save_data("data_df")
    st.success(f"Eintrag vom {timestamp} wurde gelöscht.")

# Hauptbereich
if 'data_df' in st.session_state and not st.session_state['data_df'].empty:

    # Patienten-IDs für Filter
    patient_ids = st.session_state['data_df']['patient_id'].dropna().unique()
    selected_patient_id = st.selectbox(
        "🔍 Ergebnisse filtern nach Patienten-ID (optional)", 
        options=["Alle"] + list(patient_ids)
    )

    if selected_patient_id != "Alle":
        filtered_df = st.session_state['data_df'][st.session_state['data_df']['patient_id'] == selected_patient_id]
    else:
        filtered_df = st.session_state['data_df']

    # Kompakte Anzeige der Einträge
    for idx, row in filtered_df.iterrows():
        # Timestamp schön formatieren
        timestamp = pd.to_datetime(row.get('timestamp'))
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if not pd.isnull(timestamp) else "kein Datum"

        # Patienten-ID holen und behandeln
        patient_id = row.get('patient_id')
        if not patient_id or pd.isna(patient_id) or str(patient_id).strip() == "":
            patient_label = "**Patienten-ID: Unbekannt**"
        else:
            patient_label = f"**Patienten-ID: {patient_id}**"

        # --- Neuer Expander-Titel ---
        with st.expander(f"🆔 {patient_label} – {timestamp_str}"):
            st.markdown(f"""
            **Patienten-ID:** {row.get('patient_id', 'Keine ID')}  
            **Geschlecht:** {row.get('gender', 'Unbekannt')}  
            **Geburtsdatum:** {row.get('birth_date', 'Unbekannt')} | **Alter:** {row.get('age', 'Unbekannt')}
            """)

            # Zellzählung kompakt darstellen
            counts = row.get('counts', {})
            if isinstance(counts, dict) and any(value > 0 for value in counts.values()):
                st.markdown("**Weisses Blutbild:**")
                for zelltyp, anzahl in counts.items():
                    if anzahl > 0:
                        st.markdown(f"- {zelltyp}: {anzahl}")
            else:
                st.info("Keine Zellzählung gespeichert.")

            # Morphologische Auffälligkeiten kompakt
            morpho = row.get('morphology_results', {})
            if isinstance(morpho, dict):
                auffaelligkeiten = {k: v for k, v in morpho.items() if v != "Keine"}
            else:
                auffaelligkeiten = {}

            if auffaelligkeiten:
                st.markdown("**Morphologische Auffälligkeiten:**")
                for merkmal, stufe in auffaelligkeiten.items():
                    st.markdown(f"- {merkmal}: {stufe}")
            else:
                st.info("Keine morphologischen Auffälligkeiten gespeichert.")

            # 🗑️ Eintrag löschen
            if st.button(f"🗑️ Diesen Eintrag löschen", key=f"delete_{idx}"):
                delete_entry(row.get('timestamp'))
                st.rerun()  # Seite neu laden nach Löschen

    st.markdown("---")

    # Download-Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Alle Ergebnisse als CSV herunterladen",
        data=csv,
        file_name='gespeicherte_ergebnisse.csv',
        mime='text/csv'
    )

else:
    st.info("Es sind noch keine Ergebnisse gespeichert.")
