import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from fpdf import FPDF

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
        with st.expander(f"{patient_label} – {timestamp_str}"):
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

            # Kommentar anzeigen
            comment = row.get('comment', 'Kein Kommentar')
            st.markdown(f"**Kommentar:** {comment}")
            
            # Eintrag löschen
            if st.button(f"Diesen Eintrag löschen", key=f"delete_{idx}"):
                delete_entry(row.get('timestamp'))
                st.rerun()  # Seite neu laden nach Löschen

    st.markdown("---")

    # Download-Button for PDF
    if not filtered_df.empty:
        if selected_patient_id != "Alle":
            pdf = FPDF()
            pdf.add_page()

            # Title
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Berichte für Patient: {selected_patient_id}", ln=True, align="C")
            pdf.ln(5)

            # Iterate through all reports for the selected patient
            for idx, row in filtered_df.iterrows():
                # Patient Information
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 8, f"Bericht {idx + 1}", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 8, f"Geschlecht: {row.get('gender', 'Unbekannt')} | Geburtsdatum: {row.get('birth_date', 'Unbekannt')} | Alter: {row.get('age', 'Unbekannt')} Jahre")
                timestamp = pd.to_datetime(row.get('timestamp')).strftime("%Y-%m-%d %H:%M:%S") if not pd.isnull(row.get('timestamp')) else "kein Datum"
                pdf.cell(0, 8, f"Zeitpunkt: {timestamp}", ln=True)
                pdf.ln(3)

                # Zellzählung Table
                pdf.set_font("Arial", "B", 10)
                pdf.cell(60, 8, "Zelltyp", border=1)
                pdf.cell(40, 8, "Anzahl", border=1)
                pdf.cell(40, 8, "Referenz", border=1, ln=True)
                pdf.set_font("Arial", "", 10)
                counts = row.get('counts', {})
                reference_values = row.get('reference_values', {})
                if isinstance(reference_values, dict):
                    for cell, (low, high) in reference_values.items():
                        count = counts.get(cell, 0)
                        ref = f"{low}-{high}%"
                        pdf.cell(60, 8, cell, border=1)
                        pdf.cell(40, 8, str(count), border=1)
                        pdf.cell(40, 8, ref, border=1, ln=True)
                else:
                    pdf.cell(0, 8, "Keine Referenzwerte verfügbar", ln=True)

                pdf.ln(5)

                # Morphologische Beurteilung Table
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "Morphologische Beurteilung:", ln=True)
                pdf.ln(3)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(80, 8, "Parameter", border=1)
                pdf.cell(40, 8, "Schweregrad", border=1, ln=True)
                pdf.set_font("Arial", "", 10)
                morpho = row.get('morphology_results', {})
                if isinstance(morpho, dict):
                    for param, severity in morpho.items():
                        pdf.cell(80, 8, param, border=1)
                        pdf.cell(40, 8, severity, border=1, ln=True)
                else:
                    pdf.cell(0, 8, "Keine morphologischen Beurteilungen verfügbar", ln=True)

                pdf.ln(5)

                # Kommentar Section
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, "Kommentar:", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 8, row.get('comment', 'Kein Kommentar'))

                pdf.ln(10)  # Add spacing between entries

            # Generate PDF Bytes
            pdf_bytes = pdf.output(dest='S').encode('latin-1')

            # Download Button
            st.download_button(
                label=f"Berichte für {selected_patient_id} als PDF herunterladen",
                data=pdf_bytes,
                file_name=f"berichte_{selected_patient_id}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("Bitte wählen Sie eine Patienten-ID aus, um Berichte als PDF herunterzuladen.")

else:
    st.info("Es sind noch keine Ergebnisse gespeichert.")
