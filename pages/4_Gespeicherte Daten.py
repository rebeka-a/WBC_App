import streamlit as st
import pandas as pd
from fpdf import FPDF
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
import datetime
import ast
import re
from PIL import Image
import base64
from io import BytesIO

# Seitenkonfiguration
st.set_page_config(page_title="Gespeicherte Ergebnisse", layout="wide")

# Hilfsfunktion: Bild in base64 umwandeln
def logo_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Logo laden und als HTML anzeigen (links oben, größer)
logo = Image.open("images/logo.png")
encoded_logo = logo_to_base64(logo)

st.markdown(
    f"""
    <div style="display: flex; align-items: center; margin-top: -70px; margin-bottom: 1rem;">
        <img src="data:image/png;base64,{encoded_logo}" style="height: 100px; margin-left: -15px;" />
    </div>
    """,
    unsafe_allow_html=True)

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Titel
st.title("Übersicht der gespeicherten Ergebnisse")

# DataManager initialisieren
data_manager = DataManager()

# Daten laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

# Funktion zum sicheren Parsen
def safe_eval(value, fallback):
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return fallback
    elif isinstance(value, type(fallback)):
        return value
    else:
        return fallback

# Funktion zum Löschen
def delete_entry(timestamp):
    df = st.session_state["data_df"]
    df = df[df["timestamp"] != timestamp]
    st.session_state["data_df"] = df
    data_manager.save_data("data_df")
    st.success(f"Eintrag vom {timestamp} wurde gelöscht.")

# Anzeige
if 'data_df' in st.session_state and not st.session_state["data_df"].empty:

    patient_ids = st.session_state["data_df"]["patient_id"].dropna().unique()
    selected_patient_id = st.selectbox(
        "🔍 Ergebnisse filtern nach Patienten-ID (optional)",
        options=["Alle"] + list(patient_ids)
    )

    if selected_patient_id != "Alle":
        filtered_df = st.session_state["data_df"][st.session_state["data_df"]["patient_id"] == selected_patient_id]
    else:
        filtered_df = st.session_state["data_df"]

    for idx, row in filtered_df.iterrows():
        timestamp = pd.to_datetime(row.get("timestamp"), errors="coerce")
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if not pd.isnull(timestamp) else "kein Datum"
        patient_id = row.get("patient_id", "Unbekannt")

        with st.expander(f"**Patienten-ID: {patient_id}** – {timestamp_str}"):

            st.markdown(f"""
            **Patienten-ID:** {patient_id}  
            **Geschlecht:** {row.get('gender', 'Unbekannt')}  
            **Geburtsdatum:** {row.get('birth_date', 'Unbekannt')} | **Alter:** {row.get('age', 'Unbekannt')}
            """)

            counts = safe_eval(row.get("counts", {}), {})
            morpho = safe_eval(row.get("morphology_results", {}), {})
            comment_raw = row.get("comment", "")
            comment = str(comment_raw).strip() if not pd.isna(comment_raw) else ""

            if counts and any(v > 0 for v in counts.values()):
                st.markdown("**Weisses Blutbild:**")
                for zelltyp, anzahl in counts.items():
                    if anzahl > 0:
                        st.markdown(f"- {zelltyp}: {anzahl}")
            else:
                st.info("Keine Zellzählung gespeichert.")

            auffaelligkeiten = {k: v for k, v in morpho.items() if v != "Keine"}

            if auffaelligkeiten:
                st.markdown("**Morphologische Auffälligkeiten:**")
                for merkmal, stufe in auffaelligkeiten.items():
                    st.markdown(f"- {merkmal}: {stufe}")
            else:
                st.info("Keine morphologischen Auffälligkeiten gespeichert.")

            if comment:
                st.markdown(f"**Kommentar:** {comment}")
            else:
                st.info("Kein Kommentar vorhanden.")

            # PDF Export
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

            reference_values = {
                "Segmentkernige Neutrophile": (40, 75),
                "Stabkernige Neutrophile": (3, 6),
                "Eosinophile": (1, 6),
                "Basophile": (0, 1),
                "Monozyten": (2, 10),
                "Lymphozyten": (15, 45),
                "Plasmazellen": (0, 2),
                "Vorstufen": (0, 1)
            }

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

            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')

            safe_patient_id = re.sub(r'[^a-zA-Z0-9_-]', '_', str(patient_id))
            safe_timestamp = timestamp_str.replace(":", "-").replace(" ", "_")

            st.download_button(
                label="📄 Bericht als PDF herunterladen",
                data=pdf_bytes,
                file_name=f"Zellbericht_{safe_patient_id}_{safe_timestamp}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            if st.button(f"Diesen Eintrag löschen", key=f"delete_{idx}", use_container_width=True):
                delete_entry(row.get("timestamp"))
                st.rerun()

else:
    st.info("Es sind noch keine Ergebnisse gespeichert.")
