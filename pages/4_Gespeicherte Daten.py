import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from fpdf import FPDF
import datetime
import re
import ast

# Seitenkonfiguration
st.set_page_config(page_title="Gespeicherte Ergebnisse", layout="wide")

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Titel
st.title("Übersicht der gespeicherten Ergebnisse")

# DataManager initialisieren
data_manager = DataManager()

# Daten laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

# Funktion zur Referenzwertberechnung
def get_reference_values(age, gender):
    if age is None:
        return {
            "Segmentkernige Neutrophile": (40, 75),
            "Stabkernige Neutrophile": (3, 6),
            "Eosinophile": (1, 6),
            "Basophile": (0, 1),
            "Monozyten": (2, 10),
            "Lymphozyten": (15, 45),
            "Plasmazellen": (0, 2),
            "Vorstufen": (0, 1)
        }
    elif age < 1:
        return {
            "Segmentkernige Neutrophile": (35, 65),
            "Stabkernige Neutrophile": (5, 15),
            "Eosinophile": (2, 8),
            "Basophile": (0, 1),
            "Monozyten": (5, 12),
            "Lymphozyten": (20, 50),
            "Plasmazellen": (0, 2),
            "Vorstufen": (0, 2)
        }
    elif age < 5:
        return {
            "Segmentkernige Neutrophile": (30, 60),
            "Stabkernige Neutrophile": (3, 8),
            "Eosinophile": (1, 6),
            "Basophile": (0, 1),
            "Monozyten": (2, 10),
            "Lymphozyten": (30, 55),
            "Plasmazellen": (0, 2),
            "Vorstufen": (0, 1)
        }
    elif age < 12:
        return {
            "Segmentkernige Neutrophile": (40, 65),
            "Stabkernige Neutrophile": (2, 6),
            "Eosinophile": (1, 5),
            "Basophile": (0, 1),
            "Monozyten": (2, 8),
            "Lymphozyten": (25, 45),
            "Plasmazellen": (0, 2),
            "Vorstufen": (0, 1)
        }
    else:
        return {
            "Segmentkernige Neutrophile": (40, 75),
            "Stabkernige Neutrophile": (3, 6),
            "Eosinophile": (1, 6),
            "Basophile": (0, 1),
            "Monozyten": (2, 10),
            "Lymphozyten": (15, 45),
            "Plasmazellen": (0, 2),
            "Vorstufen": (0, 1)
        }

# Funktion zum Löschen eines Eintrags
def delete_entry(timestamp):
    df = st.session_state['data_df']
    df = df[df['timestamp'] != timestamp]
    st.session_state['data_df'] = df
    data_manager.save_data("data_df")
    st.success(f"Eintrag vom {timestamp} wurde gelöscht.")

# Hauptbereich
if 'data_df' in st.session_state and not st.session_state['data_df'].empty:

    patient_ids = st.session_state['data_df']['patient_id'].dropna().unique()
    selected_patient_id = st.selectbox(
        "🔍 Ergebnisse filtern nach Patienten-ID (optional)", 
        options=["Alle"] + list(patient_ids)
    )

    if selected_patient_id != "Alle":
        filtered_df = st.session_state['data_df'][st.session_state['data_df']['patient_id'] == selected_patient_id]
    else:
        filtered_df = st.session_state['data_df']

    for idx, row in filtered_df.iterrows():
        timestamp = pd.to_datetime(row.get('timestamp'), errors='coerce')
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if not pd.isnull(timestamp) else "kein Datum"
        patient_id = row.get('patient_id')
        patient_label = f"**Patienten-ID: {patient_id}**" if patient_id else "**Patienten-ID: Unbekannt**"

        with st.expander(f"{patient_label} – {timestamp_str}"):
            st.markdown(f"""
            **Patienten-ID:** {row.get('patient_id', 'Keine ID')}  
            **Geschlecht:** {row.get('gender', 'Unbekannt')}  
            **Geburtsdatum:** {row.get('birth_date', 'Unbekannt')} | **Alter:** {row.get('age', 'Unbekannt')}
            """)

            # Zellzählung sicher parsen
            raw_counts = row.get('counts', {})
            if isinstance(raw_counts, str):
                try:
                    counts = ast.literal_eval(raw_counts)
                except Exception:
                    counts = {}
            else:
                counts = raw_counts

            if isinstance(counts, dict) and any(value > 0 for value in counts.values()):
                st.markdown("**Weisses Blutbild:**")
                for zelltyp, anzahl in counts.items():
                    if anzahl > 0:
                        st.markdown(f"- {zelltyp}: {anzahl}")
            else:
                st.info("Keine Zellzählung gespeichert.")

            # Morphologische Beurteilung sicher parsen
            raw_morpho = row.get('morphology_results', {})
            if isinstance(raw_morpho, str):
                try:
                    morpho = ast.literal_eval(raw_morpho)
                except Exception:
                    morpho = {}
            else:
                morpho = raw_morpho

            auffaelligkeiten = {k: v for k, v in morpho.items() if v != "Keine"} if isinstance(morpho, dict) else {}

            if auffaelligkeiten:
                st.markdown("**Morphologische Auffälligkeiten:**")
                for merkmal, stufe in auffaelligkeiten.items():
                    st.markdown(f"- {merkmal}: {stufe}")
            else:
                st.info("Keine morphologischen Auffälligkeiten gespeichert.")

            # Kommentar sicher parsen
            raw_comment = row.get('comment', '')
            comment = str(raw_comment).strip() if not pd.isna(raw_comment) else ''
            if comment:
                st.markdown(f"**Kommentar:** {comment}")
            else:
                st.info("Kein Kommentar vorhanden.")

            # PDF erzeugen
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 8, "Ergebnisse der Zellzählung", ln=True, align="C")
            pdf.ln(4)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 6, f"Patienten-ID: {row.get('patient_id', '')} | Geschlecht: {row.get('gender', '')} | Geburtsdatum: {row.get('birth_date', '')} | Alter: {row.get('age', '')} Jahre")
            pdf.cell(0, 6, f"Zeitpunkt: {timestamp_str}", ln=True)
            pdf.ln(2)

            pdf.set_font("Arial", "B", 8)
            pdf.cell(60, 6, "Zelltyp", border=1)
            pdf.cell(30, 6, "Anzahl", border=1)
            pdf.cell(30, 6, "Referenz", border=1, ln=True)
            pdf.set_font("Arial", "", 8)

            reference_values = get_reference_values(row.get("age"), row.get("gender"))
            for cell, (low, high) in reference_values.items():
                count = counts.get(cell, 0)
                ref = f"{low}-{high}%"
                pdf.cell(60, 6, cell, border=1)
                pdf.cell(30, 6, str(count), border=1)
                pdf.cell(30, 6, ref, border=1, ln=True)

            pdf.ln(3)
            pdf.set_font("Arial", "B", 8)
            pdf.cell(0, 6, "Morphologische Beurteilung:", ln=True)
            pdf.ln(2)
            pdf.cell(60, 6, "Parameter", border=1)
            pdf.cell(30, 6, "Schweregrad", border=1, ln=True)
            pdf.set_font("Arial", "", 8)
            for param, severity in morpho.items():
                pdf.cell(60, 6, param, border=1)
                pdf.cell(30, 6, severity, border=1, ln=True)

            pdf.ln(3)
            pdf.set_font("Arial", "B", 8)
            pdf.cell(0, 6, "Kommentar:", ln=True)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 6, comment)

            # PDF als Bytes exportieren
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')

            # Dateiname sicher erzeugen
            raw_id = row.get('patient_id', 'unbekannt')
            safe_patient_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(raw_id))
            safe_timestamp = timestamp_str.replace(':', '-').replace(' ', '_')
            file_name = f"Zellzählung_{safe_patient_id}_{safe_timestamp}.pdf"

            # Zwei gleich breite Buttons nebeneinander – volle Breite
            with st.container():
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    st.download_button(
                        label="📄 PDF herunterladen",
                        data=pdf_bytes,
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                with col2:
                    if st.button("🗑️ Eintrag löschen", key=f"delete_{idx}", use_container_width=True):
                        delete_entry(row.get('timestamp'))
                        st.rerun()

else:
    st.info("Es sind noch keine Ergebnisse gespeichert.")
