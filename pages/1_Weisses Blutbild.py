import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Seitenkonfiguration
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

# Zugriffsschutz
LoginManager().go_to_login('Start.py')

# Titel
st.title("Weisses Blutbild")

# DataManager initialisieren
data_manager = DataManager()

# Daten laden
if "data_df" not in st.session_state:
    data_manager.load_app_data(
        session_state_key="data_df",
        file_name="data.csv",
        initial_value=pd.DataFrame(columns=["timestamp", "patient_id", "counts", "gender", "birth_date"])
    )

# Session States initialisieren
if "counts" not in st.session_state:
    st.session_state["counts"] = {
        "Segmentkernige Neutrophile": 0,
        "Stabkernige Neutrophile": 0,
        "Eosinophile": 0,
        "Basophile": 0,
        "Monozyten": 0,
        "Lymphozyten": 0,
        "Plasmazellen": 0,
        "Vorstufen": 0
    }
if "action_history" not in st.session_state:
    st.session_state["action_history"] = []

# --- Patientendaten ---
st.subheader("Patientendaten")

# Hinweis, wenn Patientendaten fehlen
if "patient_id" not in st.session_state and "gender" not in st.session_state and "birth_date" not in st.session_state:
    st.warning("⚠️ Bitte neue Patientendaten eingeben.")

# Patienten-ID eingeben
patient_id = st.text_input(
    "Patienten-ID eingeben", 
    placeholder="z.B. 12345", 
    value=st.session_state.get("patient_id", "")
)

# Geschlecht auswählen
gender = st.selectbox(
    "Geschlecht auswählen:",
    ["", "Männlich", "Weiblich"],
    index=["", "Männlich", "Weiblich"].index(st.session_state.get("gender", "")) if "gender" in st.session_state else 0
)

# Geburtsdatum behandeln (sicher gegen leeren String)
birth_date_str = st.session_state.get("birth_date", "")
if birth_date_str:
    try:
        birth_date_value = datetime.datetime.strptime(birth_date_str, "%d.%m.%Y").date()
    except ValueError:
        birth_date_value = None
else:
    birth_date_value = None

birth_date = st.date_input(
    "Geburtsdatum eingeben:",
    value=birth_date_value
)

# Patientendaten speichern
if patient_id:
    st.session_state["patient_id"] = patient_id
if gender:
    if gender != "":
        st.session_state["gender"] = gender
if birth_date:
    st.session_state["birth_date"] = birth_date.strftime("%d.%m.%Y")

# 🔹 Patientendaten zurücksetzen Button direkt unter der Eingabe
if st.button("🧹 Patientendaten zurücksetzen", key="reset_patient_button", use_container_width=True):
    st.session_state.pop("patient_id", None)
    st.session_state.pop("gender", None)
    st.session_state.pop("birth_date", None)
    st.success("Patientendaten wurden zurückgesetzt!")
    st.rerun()

# Alter berechnen nur wenn Geburtsdatum existiert
if birth_date:
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
else:
    age = None

# Zelltypenliste automatisch basierend auf counts
wbc_types = list(st.session_state["counts"].keys())

button_colors = ["#1f77b4", "#1f77b4", "#d62728", "#9467bd", "#2ca02c", "#ff7f0e", "#8c564b", "#e377c2"]

# --- Zellzählung ---
st.subheader("Zellen zählen")

clicked_cell = None

# 3 Buttons pro Zeile
for i in range(0, len(wbc_types), 3):
    cols = st.columns(3)
    for idx, cell in enumerate(wbc_types[i:i+3]):
        with cols[idx]:
            if st.button(f"➕ {cell} ({st.session_state['counts'][cell]})", key=f"btn_{cell}", use_container_width=True):
                clicked_cell = cell

# Klick auswerten
if clicked_cell:
    st.session_state["counts"][clicked_cell] += 1
    st.session_state["action_history"].append(clicked_cell)
    st.rerun()

# --- Steuerung (nur Zellzählung) ---
st.markdown("---")
st.subheader("Steuerung")

col_undo, col_reset = st.columns(2, gap="small")

with col_undo:
    if st.button("🔙 Rückgängig", key="undo_button", use_container_width=True):
        if st.session_state["action_history"]:
            last_cell = st.session_state["action_history"].pop()
            if st.session_state["counts"][last_cell] > 0:
                st.session_state["counts"][last_cell] -= 1
                st.success(f"Letzte Aktion rückgängig gemacht: {last_cell}")
            else:
                st.warning(f"{last_cell} ist bereits 0.")
            st.rerun()
        else:
            st.info("Keine Aktion vorhanden zum Rückgängigmachen.")

with col_reset:
    if st.button("🧹 Zellzählung zurücksetzen", key="reset_button", use_container_width=True):
        for cell in st.session_state["counts"].keys():
            st.session_state["counts"][cell] = 0
        st.session_state["action_history"].clear()
        st.success("Alle Zählungen wurden zurückgesetzt.")
        st.rerun()

# --- Zellverteilung ---
st.markdown("---")
st.subheader("Zellverteilung")

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(wbc_types, [st.session_state["counts"][cell] for cell in wbc_types],
              color=button_colors, edgecolor='black', alpha=0.8)

ax.set_ylabel("Anzahl der Zellen")
ax.set_xlabel("Blutzelltypen")
ax.set_title("Verteilung der Blutzellen")
ax.set_xticks(np.arange(len(wbc_types)))
ax.set_xticklabels(wbc_types, rotation=30, ha="right")

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{int(height)}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

st.pyplot(fig)

# --- Aktionen (Speichern) ---
st.markdown("---")
st.subheader("⚙️ Aktionen")

if st.button("💾 Zellzählung speichern"):
    new_entry = {
        "timestamp": datetime.datetime.now(),
        "patient_id": st.session_state.get("patient_id", ""),
        "counts": st.session_state["counts"].copy(),
        "gender": st.session_state.get("gender", ""),
        "birth_date": st.session_state.get("birth_date", "")
    }
    new_df = pd.DataFrame([new_entry])
    st.session_state["data_df"] = pd.concat([st.session_state["data_df"], new_df], ignore_index=True)
    data_manager.save_data("data_df")
    st.success("Zellzählung erfolgreich gespeichert!")
