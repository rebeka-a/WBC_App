import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import io
from fpdf import FPDF
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Datenübersicht", layout="wide")

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Titel
st.title("Datenübersicht")

# DataManager initialisieren
data_manager = DataManager()

# Daten beim Start laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

# Patientendaten
patient_id = st.session_state.get("patient_id", "")
gender = st.session_state.get("gender", "Nicht angegeben")
birth_date_str = st.session_state.get("birth_date", "")

if birth_date_str:
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%d.%m.%Y").date()
    except ValueError:
        birth_date = None
else:
    birth_date = None

if birth_date:
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
else:
    age = None

# Zellzählung vorbereiten
wbc_types = [
    "Segmentkernige Neutrophile",
    "Stabkernige Neutrophile",
    "Eosinophile",
    "Basophile",
    "Monozyten",
    "Lymphozyten",
    "Plasmazellen",
    "Vorstufen"
]

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

reference_values = get_reference_values(age, gender)

if 'counts' not in st.session_state:
    st.session_state['counts'] = {cell: 0 for cell in wbc_types}

def calculate_percentages():
    total = sum(st.session_state['counts'].values())
    if total == 0:
        return {cell: 0 for cell in wbc_types}
    return {cell: round((count / total) * 100, 1) for cell, count in st.session_state['counts'].items()}

def format_data():
    data = []
    percentages = calculate_percentages()
    for cell, (low, high) in reference_values.items():
        count = st.session_state['counts'].get(cell, 0)
        percent = percentages.get(cell, 0)
        if percent < low:
            status = "⬇️"
        elif percent > high:
            status = "⬆️"
        else:
            status = ""
        data.append([cell, count, f"{percent}%", f"{low}-{high}%", status])
    return pd.DataFrame(data, columns=["Zelltyp", "Gezählte Zellen", "Gezählte %", "Referenzwerte (%)", "Status"])

# Zellzählung Anzeige
st.subheader("Übersicht Zellzählungen")

if sum(st.session_state['counts'].values()) > 0:
    patient_info = f"**Patient:** {gender}"
    if birth_date_str:
        patient_info += f", **Geburtsdatum:** {birth_date_str}"
    if age is not None:
        patient_info += f", **Alter:** {age} Jahre"
    if patient_id:
        patient_info += f", **Patienten-ID:** {patient_id}"

    st.markdown(patient_info)
    st.markdown("⬇️ Wert unter Normbereich | ⬆️ Wert über Normbereich")

    data_df = format_data()

    st.dataframe(
        data_df.style.applymap(
            lambda val: "color: red; font-weight: bold;" if val in ["⬆️", "⬇️"] else "",
            subset=["Status"]
        )
    )
else:
    st.info("Noch keine Zellzählungen vorhanden.")

# Morphologische Beurteilung
st.markdown("---")
st.subheader("Morphologische Beurteilung")

# Überprüfen, ob Ergebnisse vorhanden sind
morpho_results = st.session_state.get('morphology_results', {})
auffaelligkeiten_df = pd.DataFrame(
    [{"Parameter": k, "Schweregrad": v} for k, v in morpho_results.items() if v != "Keine"]
)

if not auffaelligkeiten_df.empty:
    # Tabelle mit farblicher Hervorhebung
    st.table(
        auffaelligkeiten_df.style.applymap(
            lambda val: "color: green;" if val == "Leicht" else
                        "color: orange;" if val == "Mittel" else
                        "color: red;" if val == "Schwer" else ""
        )
    )
else:
    st.info("Keine morphologischen Auffälligkeiten vorhanden.")

# Kommentar hinzufügen
st.markdown("---")
st.subheader("Kommentar ✒️")

comment = st.text_area(
    "Kommentar",
    value=st.session_state.get("comment", ""),
    placeholder="Hier Kommentar eingeben..."
)

# Ergebnisse speichern und herunterladen
st.markdown("---")
col_save, col_download = st.columns(2, gap="small")

with col_save:
    if st.button("Ergebnisse speichern", use_container_width=True):
        result = {
            "patient_id": patient_id,
            "gender": gender,
            "birth_date": birth_date_str,
            "age": age if age is not None else "Nicht angegeben",
            "counts": st.session_state['counts'],
            "morphology_results": st.session_state.get('morphology_results', {}),
            "comment": comment,
            "timestamp": datetime.datetime.now()
        }
        try:
            data_manager.append_record(session_state_key='data_df', record_dict=result)
            st.success("Alle Ergebnisse wurden erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")

with col_download:
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 10)  # Kleinere Schriftgröße
    pdf.cell(0, 8, "Ergebnisse der Zellzählung", ln=True, align="C")
    pdf.ln(4)  # Weniger Abstand nach dem Titel

    # Patient Information
    pdf.set_font("Arial", "", 8)  # Kleinere Schriftgröße
    pdf.multi_cell(0, 6, f"Patienten-ID: {patient_id} | Geschlecht: {gender} | Geburtsdatum: {birth_date_str} | Alter: {age} Jahre")
    pdf.cell(0, 6, f"Zeitpunkt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", ln=True)
    pdf.ln(2)  # Weniger Abstand nach den Patientendaten

    # Zellzählung Table
    pdf.set_font("Arial", "B", 8)  # Kleinere Schriftgröße
    pdf.cell(60, 6, "Zelltyp", border=1)
    pdf.cell(30, 6, "Anzahl", border=1)
    pdf.cell(30, 6, "Referenz", border=1, ln=True)
    pdf.set_font("Arial", "", 8)  # Kleinere Schriftgröße für die Inhalte
    for cell, (low, high) in reference_values.items():
        count = st.session_state['counts'].get(cell, 0)
        ref = f"{low}-{high}%"
        pdf.cell(60, 6, cell, border=1)
        pdf.cell(30, 6, str(count), border=1)
        pdf.cell(30, 6, ref, border=1, ln=True)

    pdf.ln(3)  # Weniger Abstand nach der Tabelle

    # Morphologische Beurteilung Table
    pdf.set_font("Arial", "B", 8)  # Kleinere Schriftgröße
    pdf.cell(0, 6, "Morphologische Beurteilung:", ln=True)
    pdf.ln(2)
    pdf.cell(60, 6, "Parameter", border=1)
    pdf.cell(30, 6, "Schweregrad", border=1, ln=True)
    pdf.set_font("Arial", "", 8)  # Kleinere Schriftgröße für die Inhalte
    for param, severity in st.session_state.get('morphology_results', {}).items():
        pdf.cell(60, 6, param, border=1)
        pdf.cell(30, 6, severity, border=1, ln=True)

    pdf.ln(3)  # Weniger Abstand nach der Tabelle

    # Kommentar Section
    pdf.set_font("Arial", "B", 8)  # Kleinere Schriftgröße
    pdf.cell(0, 6, "Kommentar:", ln=True)
    pdf.set_font("Arial", "", 8)  # Kleinere Schriftgröße für den Kommentar
    pdf.multi_cell(0, 6, comment)

    # Generate PDF Bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')

    # Download Button
    st.download_button(
        label="Ergebnisse als PDF herunterladen",
        data=pdf_bytes,
        file_name="ergebnisse_blutbild.pdf",
        mime="application/pdf",
        use_container_width=True
    )

if st.button("Gespeicherte Daten"):
    st.switch_page("pages/4_Gespeicherte Daten.py")
