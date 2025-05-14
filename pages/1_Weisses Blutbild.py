import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# --- Seitenkonfiguration ---
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

# --- DataManager und LoginManager initialisieren ---
data_manager = DataManager()
login_manager = LoginManager(data_manager)

# --- Zugriffsschutz ---
login_manager.go_to_login('Start.py')

# --- Hauptbereich ---
st.title("Weisses Blutbild")

# --- Daten laden ---
if "data_df" not in st.session_state:
    data_manager.load_app_data(
        session_state_key="data_df",
        file_name="data.csv",
        initial_value=pd.DataFrame(columns=["timestamp", "patient_id", "counts", "gender", "birth_date"])
    )

# --- Session States initialisieren ---
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

if "toast_shown_100" not in st.session_state:
    st.session_state["toast_shown_100"] = False
if "toast_shown_200" not in st.session_state:
    st.session_state["toast_shown_200"] = False
if "previous_total_cells" not in st.session_state:
    st.session_state["previous_total_cells"] = 0

# --- Patientendaten ---
st.subheader("Patientendaten 📋")

if not (st.session_state.get("patient_id") and st.session_state.get("gender") and st.session_state.get("birth_date")):
    st.warning("Bitte neue Patientendaten eingeben.")

patient_id = st.text_input(
    "Patienten-ID",
    placeholder="z.B. 12345",
    value=st.session_state.get("patient_id", "")
)

gender = st.selectbox(
    "Geschlecht",
    ["", "Männlich", "Weiblich"],
    index=["", "Männlich", "Weiblich"].index(st.session_state.get("gender", "")) if "gender" in st.session_state else 0
)

birth_date_input = st.text_input(
    "Geburtsdatum (TT.MM.JJJJ)",
    placeholder="z.B. 01.01.2000",
    value=st.session_state.get("birth_date", "")
)

try:
    if birth_date_input:
        birth_date_value = datetime.datetime.strptime(birth_date_input, "%d.%m.%Y").date()
    else:
        birth_date_value = None
except ValueError:
    birth_date_value = None
    st.error("Ungültiges Datumsformat! Bitte TT.MM.JJJJ verwenden.")

if patient_id:
    st.session_state["patient_id"] = patient_id
if gender:
    st.session_state["gender"] = gender
if birth_date_value:
    st.session_state["birth_date"] = birth_date_value.strftime("%d.%m.%Y")

if st.button("Patientendaten zurücksetzen", use_container_width=True):
    st.session_state.pop("patient_id", None)
    st.session_state.pop("gender", None)
    st.session_state.pop("birth_date", None)
    st.success("Patientendaten wurden zurückgesetzt!")
    st.rerun()

# --- Zellzählung ---
st.markdown("---")
st.subheader("Zellen zählen 🔬")

total_cells = sum(st.session_state["counts"].values())
previous_total = st.session_state["previous_total_cells"]
st.session_state["previous_total_cells"] = total_cells

st.info(f"**Gesamtanzahl der gezählten Zellen:** {total_cells}")

# --- Hinweise bei 100 und 200 Zellen als Toast ---
if total_cells >= 100 and previous_total < 100:
    st.toast("Es wurden 100 Zellen gezählt!", icon="🔔")
    st.session_state["toast_shown_100"] = True

if total_cells >= 200 and previous_total < 200:
    st.toast("Es wurden 200 Zellen gezählt!", icon="🔔")
    st.session_state["toast_shown_200"] = True

# Rücksetzen, wenn Rückgängig gemacht wurde
if total_cells < 100:
    st.session_state["toast_shown_100"] = False
if total_cells < 200:
    st.session_state["toast_shown_200"] = False

# --- Zelltypen-Buttons ---
wbc_types = list(st.session_state["counts"].keys())
button_colors = ["#1f77b4", "#1f77b4", "#d62728", "#9467bd", "#2ca02c", "#ff7f0e", "#8c564b", "#e377c2"]

clicked_cell = None

for i in range(0, len(wbc_types), 3):
    cols = st.columns(3)
    for idx, cell in enumerate(wbc_types[i:i+3]):
        with cols[idx]:
            if st.button(f"➕ {cell} ({st.session_state['counts'][cell]})", key=f"btn_{cell}", use_container_width=True):
                clicked_cell = cell

if clicked_cell:
    st.session_state["counts"][clicked_cell] += 1
    st.session_state["action_history"].append(clicked_cell)
    st.rerun()

# --- Steuerung: Undo und Reset ---
st.markdown("---")
st.subheader("Steuerung")

col_undo, col_reset = st.columns(2, gap="small")

with col_undo:
    if st.button("Rückgängig", key="undo_button", use_container_width=True):
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
    if st.button("Zellzählung zurücksetzen", key="reset_button", use_container_width=True):
        for cell in st.session_state["counts"].keys():
            st.session_state["counts"][cell] = 0
        st.session_state["action_history"].clear()
        st.session_state["toast_shown_100"] = False
        st.session_state["toast_shown_200"] = False
        st.session_state["previous_total_cells"] = 0
        st.success("Alle Zählungen wurden zurückgesetzt.")
        st.rerun()

# --- Zellverteilung Diagramm ---
st.markdown("---")
st.subheader("Zellverteilung 📊")

fig, ax = plt.subplots(figsize=(12, 6))

cell_counts = [st.session_state["counts"][cell] for cell in wbc_types]

bars = ax.bar(
    wbc_types,
    cell_counts,
    color=button_colors,
    edgecolor='black',
    alpha=0.8
)

ax.set_ylabel("Anzahl der Zellen")
ax.set_xlabel("Blutzelltypen")
ax.set_title("Verteilung der Blutzellen")
ax.set_xticks(np.arange(len(wbc_types)))
ax.set_xticklabels(wbc_types, rotation=30, ha="right")

if cell_counts:
    max_count = max(cell_counts)
    ax.set_ylim(0, max(max_count * 1.2, 5))

for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f'{int(height)}',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords="offset points",
        ha='center',
        va='bottom',
        fontsize=9
    )

st.pyplot(fig)

# --- Navigation ---
if st.button("Zum Roten Blutbild"):
    st.switch_page("pages/2_Rotes Blutbild.py")

if st.button("Zur Auswertung"):
    st.switch_page("pages/3_Auswertung.py")
