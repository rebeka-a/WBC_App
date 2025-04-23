import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

LoginManager().go_to_login('Start.py')


st.title("📋 Gesammelte Zellzählungen")

# Initialisiere DataManager
data_manager = DataManager()

# Daten beim Start korrekt laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(session_state_key="data_df", file_name="data.csv", initial_value=pd.DataFrame(columns=["timestamp", "counts", "gender", "birth_date"]))

# Zählstand initialisieren
if "counts" not in st.session_state:
    st.session_state["counts"] = {
        "Neutrophile": 0,
        "Basophile": 0,
        "Eosinophile": 0,
        "Monozyten": 0,
        "Vorstufen": 0
    }

# Patientendaten erfassen
st.subheader("🧑‍⚕️ Patientendaten")
gender = st.radio("Geschlecht auswählen:", ["Maennlich", "Weiblich"], index=0)
birth_date = st.date_input("Geburtsdatum eingeben:")

st.session_state["gender"] = gender
st.session_state["birth_date"] = birth_date.strftime("%d.%m.%Y")

# Alter berechnen
today = datetime.date.today()
age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Zelltypen definieren
def get_reference_values(age, gender):
    if age < 1:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten"]
    elif age < 5:
        return ["Neutrophile", "Eosinophile", "Monozyten"]
    elif age < 12:
        return ["Neutrophile", "Basophile", "Monozyten"]
    elif age < 18:
        return ["Neutrophile", "Eosinophile"]
    else:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]

wbc_types = get_reference_values(age, gender)
button_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

# Zellzählung
st.subheader("🩸 Zellen zählen")
cols = st.columns(len(wbc_types))
for i, cell in enumerate(wbc_types):
    with cols[i]:
        # Display the cell type and count
        st.markdown(f"**{cell} ({st.session_state['counts'][cell]})**")
        # Buttons for increasing and decreasing the count
        if st.button("➕", key=f"btn_increase_{cell}"):
            st.session_state['counts'][cell] += 1
        if st.button("➖", key=f"btn_decrease_{cell}"):
            if st.session_state['counts'][cell] > 0:  # Prevent negative counts
                st.session_state['counts'][cell] -= 1

# Speichern
if st.button("Speichern"):
    new_entry = {
        "timestamp": datetime.datetime.now(),
        "counts": st.session_state["counts"].copy(),
        "gender": st.session_state["gender"],
        "birth_date": st.session_state["birth_date"]
    }
    new_df = pd.DataFrame([new_entry])
    st.session_state["data_df"] = pd.concat([st.session_state["data_df"], new_df], ignore_index=True)
    data_manager.save_data("data_df")

st.markdown("---")

# Tabelle sortieren
if not st.session_state['data_df'].empty:
    # Konvertiere 'timestamp' in datetime, falls nötig
    st.session_state['data_df']['timestamp'] = pd.to_datetime(st.session_state['data_df']['timestamp'], errors='coerce')
    
    # Sortiere die Daten
    df_sorted = st.session_state['data_df'].sort_values(by='timestamp', ascending=False)
    st.dataframe(df_sorted)
else:
    st.info("Keine Daten vorhanden. Bitte Ergebnisse speichern, um sie hier anzuzeigen.")

# Plot
st.subheader("📊 Zellverteilung")
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(wbc_types, [st.session_state['counts'][cell] for cell in wbc_types], color=button_colors, edgecolor='black', alpha=0.8)
ax.set_ylabel("Anzahl der Zellen")
ax.set_xlabel("Blutzelltypen")
ax.set_title("Verteilung der Blutzellen")
ax.set_xticks(np.arange(len(wbc_types)))
ax.set_xticklabels(wbc_types, rotation=30, ha="right")
st.pyplot(fig)
