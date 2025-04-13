import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

LoginManager().go_to_login('Start.py') 

# Initialisiere DataManager
data_manager = DataManager()

if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=[])

st.title("📋 Gesammelte Zellzählungen & Referenzwerte")
st.markdown("Hier findest du die gesammelten Zellzählungen sowie die Referenzwerte für Blutzellen.")

if 'data_df' not in st.session_state:
    st.session_state['data_df'] = pd.DataFrame()  # Leeres DataFrame als Standardwert


# Abrufen der Patientendaten aus Session-State, falls vorhanden
gender = st.session_state.get("gender", "Nicht angegeben")
birth_date = st.session_state.get("birth_date", "Nicht angegeben")

# Berechnung des Alters

birth_date_str = st.session_state.get("birth_date", "Nicht angegeben")
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
    
# Dynamische Referenzwerte nach Geschlecht und detaillierter Altersgruppe
def get_reference_values(age, gender):
    if age == "Nicht angegeben":
        return {
            "Neutrophile": (40, 75),
            "Basophile": (0, 1),
            "Eosinophile": (1, 6),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    elif age < 1:  # Neugeborene
        return {
            "Neutrophile": (50, 80),
            "Basophile": (0, 1),
            "Eosinophile": (1, 4),
            "Monozyten": (4, 10),
            "Vorstufen": (0, 1)
        }
    elif age < 5:  # Kleinkinder
        return {
            "Neutrophile": (30, 60),
            "Basophile": (0, 1),
            "Eosinophile": (1, 5),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    elif age < 12:  # Schulkinder
        return {
            "Neutrophile": (35, 60),
            "Basophile": (0, 1),
            "Eosinophile": (1, 5),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    elif age < 18:  # Jugendliche
        return {
            "Neutrophile": (40, 65),
            "Basophile": (0, 1),
            "Eosinophile": (1, 5),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    elif gender == "Männlich":
        return {
            "Neutrophile": (40, 75),
            "Basophile": (0, 1),
            "Eosinophile": (1, 6),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }
    else:
        return {
            "Neutrophile": (42, 77),  # Leicht höhere Werte für Frauen
            "Basophile": (0, 1),
            "Eosinophile": (1, 6),
            "Monozyten": (2, 10),
            "Vorstufen": (0, 1)
        }

reference_values = get_reference_values(age, gender)

# Initialisierung der Session-State-Werte, falls nicht vorhanden
if 'counts' not in st.session_state:
    st.session_state['counts'] = {cell: 0 for cell in reference_values.keys()}

# Berechnung der Gesamtzahl der Zellen
def calculate_percentages():
    total = sum(st.session_state['counts'].values())
    if total == 0:
        return {cell: 0 for cell in reference_values.keys()}
    return {cell: round((count / total) * 100, 1) for cell, count in st.session_state['counts'].items()}

# Daten in eine formatierte Tabelle umwandeln
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

# Anzeige der Tabelle mit farbigen Werten
st.subheader("📊 Übersicht der Zellzählungen und Referenzwerte")
st.markdown(f"**Patient:** {gender}, Geburtsdatum: {birth_date}, Alter: {age}")
st.markdown("Falls ein Wert zu niedrig ist, wird ein ⬇️ angezeigt. Falls ein Wert zu hoch ist, wird ein ⬆️ angezeigt.")
data_df = format_data()
st.dataframe(data_df.style.applymap(lambda val: "color: red; font-weight: bold;" if val in ["⬆️", "⬇️"] else "", subset=["Status"]))

st.markdown("---")



if st.button("Ergebnisse speichern"):
    # Initialisierung und Registrierung von 'data_df', falls nicht vorhanden
    
    result = {
        "gender": st.session_state["gender"],
        "birth_date": st.session_state["birth_date"],
        "age": age,
        "counts": st.session_state['counts'],
        "timestamp": datetime.datetime.now()  # Aktueller Zeitstempel
    }
    try:
        data_manager.append_record(session_state_key='data_df', record_dict=result)
        st.success("Ergebnisse wurden erfolgreich gespeichert!")
        st.write("Gespeicherte Ergebnisse:", result)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Ergebnisse: {e}")
