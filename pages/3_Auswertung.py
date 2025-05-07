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

# -------------------------------
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

# -------------------------------
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

# -------------------------------
# Morphologische Beurteilung

st.markdown("---")
st.subheader("Morphologische Beurteilung")

if 'morphology_results' in st.session_state and any(
    val != "Keine" for val in st.session_state['morphology_results'].values()
):
    morpho_results = st.session_state['morphology_results']

    morpho_df = pd.DataFrame({
        "Parameter": list(morpho_results.keys()),
        "Schweregrad": list(morpho_results.values())
    })

    auffaelligkeiten_df = morpho_df[morpho_df["Schweregrad"] != "Keine"]

    st.dataframe(
        auffaelligkeiten_df.style.applymap(
            lambda val: "color: green;" if val == "Leicht" else
                         "color: orange;" if val == "Mittel" else
                         "color: red;" if val == "Stark" else "",
            subset=["Schweregrad"]
        )
    )
else:
    st.info("Noch keine morphologischen Auffälligkeiten vorhanden.")

# Kommentar hinzufügen

st.markdown("---")
st.subheader("Kommentar")

comment = st.text_area(
    "Kommentar",
    value=st.session_state.get("comment", ""),
    placeholder="Hier Kommentar eingeben..."
)

# -------------------------------
# Ergebnisse speichern und herunterladen (nebeneinander)

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
            "comment": comment,  # Kommentar hinzufügen
            "timestamp": datetime.datetime.now()
        }
        try:
            data_manager.append_record(session_state_key='data_df', record_dict=result)
            st.success("Alle Ergebnisse wurden erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")


with col_download:
    download_result = {
        "Patienten-ID": patient_id,
        "Geschlecht": gender,
        "Geburtsdatum": birth_date_str,
        "Alter": age if age is not None else "Nicht angegeben",
        "Zeitpunkt": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }

    for cell, count in st.session_state['counts'].items():
        download_result[f"Anzahl {cell}"] = count

    if 'morphology_results' in st.session_state:
        for param, severity in st.session_state['morphology_results'].items():
            download_result[f"Morphologie: {param}"] = severity

    download_df = pd.DataFrame([download_result])

    csv = download_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="Ergebnisse als CSV herunterladen",
        data=csv,
        file_name="ergebnisse_blutbild.csv",
        mime="text/csv",
        use_container_width=True
    )



if st.button("Gespeicherte Daten"):
    st.switch_page("pages/4_Gespeicherte Daten.py")