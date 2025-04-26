import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Page Config als erstes
st.set_page_config(page_title="Zellzählungen, Referenzwerte & Morphologie", layout="wide")

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Setup
st.title("Auswertung")

# DataManager initialisieren
data_manager = DataManager()

# Daten beim Start laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

# -------------------------------
# Patientendaten erfassen
# -------------------------------

st.subheader("Patientendaten")

#Patienten-ID übernehmen oder eingeben
st.subheader("Patientendaten")

# Vorhandene Patientendaten abrufen
gender = st.session_state.get("gender", "Nicht angegeben")
birth_date_str = st.session_state.get("birth_date", "Nicht angegeben")
patient_id = st.session.state.get("patient_id", "Nicht angegeben")

if birth_date_str != "Nicht angegeben":
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    except ValueError:
        birth_date = None
else:
    birth_date = None

if birth_date:
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
else:
    age = "Nicht angegeben"

# -------------------------------
# Zellzählung vorbereiten
# -------------------------------

def get_reference_values(age, gender):
    if age == "Nicht angegeben":
        return {
            "Neutrophile": (40, 75),
            "Basophile": (0, 1),
            "Eosinophile": (1, 6),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    elif age < 1:
        return {"Neutrophile": (50, 80), "Basophile": (0, 1), "Eosinophile": (1, 4), "Monozyten": (4, 10), "Vorstufen": (0, 1)}
    elif age < 5:
        return {"Neutrophile": (30, 60), "Basophile": (0, 1), "Eosinophile": (1, 5), "Monozyten": (2, 10), "Vorstufen": (0, 1)}
    elif age < 12:
        return {"Neutrophile": (35, 60), "Basophile": (0, 1), "Eosinophile": (1, 5), "Monozyten": (2, 10), "Vorstufen": (0, 1)}
    elif age < 18:
        return {"Neutrophile": (40, 65), "Basophile": (0, 1), "Eosinophile": (1, 5), "Monozyten": (2, 10), "Vorstufen": (0, 1)}
    elif gender == "Männlich":
        return {"Neutrophile": (40, 75), "Basophile": (0, 1), "Eosinophile": (1, 6), "Monozyten": (2, 10), "Vorstufen": (0, 1)}
    else:
        return {"Neutrophile": (42, 77), "Basophile": (0, 1), "Eosinophile": (1, 6), "Monozyten": (2, 10), "Vorstufen": (0, 1)}

reference_values = get_reference_values(age, gender)

if 'counts' not in st.session_state:
    st.session_state['counts'] = {cell: 0 for cell in reference_values.keys()}

def calculate_percentages():
    total = sum(st.session_state['counts'].values())
    if total == 0:
        return {cell: 0 for cell in reference_values.keys()}
    return {cell: round((count / total) * 100, 1) for cell, count in st.session_state['counts'].items()}

def format_data():
    data = []
    percentages = calculate_percentages()
    for cell, (low, high) in reference_values.items():
        count = st.session_state['counts'][cell]
        percent = percentages[cell]
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
st.markdown(f"**Patient:** {gender}, **Geburtsdatum:** {birth_date_str}, **Alter:** {age}")
st.markdown("Wichtige Information: ⬇️ Wert unter Normbereich     ⬆️ Wert über Normbereich")

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
        "age": age,
        "counts": st.session_state['counts'],
        "morphology_results": st.session_state.get('morphology_results', {}),
        "timestamp": datetime.datetime.now()
    }
    try:
        data_manager.append_record(session_state_key='data_df', record_dict=result)
        st.success("Alle Ergebnisse wurden erfolgreich gespeichert!")
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
