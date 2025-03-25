import streamlit as st
import pandas as pd
import datetime

# Titel der App
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

st.title("📋 Gesammelte Zellzählungen & Referenzwerte")
st.markdown("Hier findest du die gesammelten Zellzählungen sowie die Referenzwerte für Blutzellen.")

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

# Möglichkeit, die Daten als CSV herunterzuladen
def save_to_csv():
    data_df.to_csv("blood_cell_counts.csv", index=False)
    st.success("✅ Daten erfolgreich gespeichert!")

st.button("💾 Speichern als CSV", on_click=save_to_csv)