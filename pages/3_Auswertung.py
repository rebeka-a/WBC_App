import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
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

# -------------------------------
# Patientendaten

# Patienten-ID aus Session holen oder Eingabe
patient_id = st.session_state.get("patient_id", "")

# Geschlecht und Geburtsdatum aus Session holen
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

# -------------------------------
# Zellzählung vorbereiten
# -------------------------------

# Zelltypenliste
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

# Neue Referenzwerte
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

# Counts vorbereiten
if 'counts' not in st.session_state:
    st.session_state['counts'] = {cell: 0 for cell in wbc_types}

# Prozentuale Berechnung
def calculate_percentages():
    total = sum(st.session_state['counts'].values())
    if total == 0:
        return {cell: 0 for cell in wbc_types}
    return {cell: round((count / total) * 100, 1) for cell, count in st.session_state['counts'].items()}

# Tabelle formatieren
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

# -------------------------------
# Zellzählung & Morphologie Anzeige
# -------------------------------

st.subheader("Übersicht Zellzählungen")

# Patienteninformation dynamisch zusammenbauen
patient_info = f"**Patient:** {gender}"
if birth_date_str:
    patient_info += f", **Geburtsdatum:** {birth_date_str}"
if age is not None:
    patient_info += f", **Alter:** {age}"
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

# ---------------------------------
# Morphologische Beurteilung Tabelle
# ---------------------------------

st.markdown("---")
st.subheader("🧬 Morphologische Beurteilung")

if 'morphology_results' in st.session_state:
    morpho_results = st.session_state['morphology_results']

    morpho_df = pd.DataFrame({
        "Parameter": list(morpho_results.keys()),
        "Schweregrad": list(morpho_results.values())
    })

    auffaelligkeiten_df = morpho_df[morpho_df["Schweregrad"] != "Keine"]

    if not auffaelligkeiten_df.empty:
        st.dataframe(
            auffaelligkeiten_df.style.applymap(
                lambda val: "color: green;" if val == "Leicht" else
                             "color: orange;" if val == "Mittel" else
                             "color: red;" if val == "Stark" else "",
                subset=["Schweregrad"]
            )
        )
    else:
        st.info("Keine morphologischen Auffälligkeiten erkannt.")
else:
    st.info("Noch keine morphologischen Beurteilungen gespeichert.")

# -------------------------------
# Ergebnisse speichern
# -------------------------------

st.markdown("---")
if st.button("Gesamte Ergebnisse speichern"):
    result = {
        "patient_id": patient_id,
        "gender": gender,
        "birth_date": birth_date_str,
        "age": age if age is not None else "Nicht angegeben",
        "counts": st.session_state['counts'],
        "morphology_results": st.session_state.get('morphology_results', {}),
        "timestamp": datetime.datetime.now()
    }
    try:
        data_manager.append_record(session_state_key='data_df', record_dict=result)
        st.success("Alle Ergebnisse wurden erfolgreich gespeichert!")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
