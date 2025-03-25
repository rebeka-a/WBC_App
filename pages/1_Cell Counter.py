import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Titel der App
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

st.title("📋 Gesammelte Zellzählungen")

# Patientendaten erfassen (nicht in der Sidebar)
st.subheader("🧑‍⚕️ Patientendaten")
gender = st.radio("Geschlecht auswählen:", ["Männlich", "Weiblich"], index=0)
birth_date = st.date_input("Geburtsdatum eingeben:")

# Patientendaten in Session-State speichern
st.session_state["gender"] = gender
st.session_state["birth_date"] = birth_date.strftime("%d.%m.%Y")

# Berechnung des Alters
if birth_date:
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
else:
    age = "Nicht angegeben"

# Dynamische Referenzwerte nach Geschlecht und detaillierter Altersgruppe
def get_reference_values(age, gender):
    if age == "Nicht angegeben":
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]
    elif age < 1:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]
    elif age < 5:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]
    elif age < 12:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]
    elif age < 18:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]
    else:
        return ["Neutrophile", "Basophile", "Eosinophile", "Monozyten", "Vorstufen"]

wbc_types = get_reference_values(age, gender)
button_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

# Initialisierung der Session-State-Werte, falls nicht vorhanden
if 'counts' not in st.session_state:
    st.session_state['counts'] = {cell: 0 for cell in wbc_types}

# Funktion zum Erhöhen der Zellzahlen
def increase_count(cell_type):
    st.session_state['counts'][cell_type] += 1

# Anzeige der Buttons mit aktuellen Werten
st.subheader("🩸 Zellen zählen")
st.markdown("Klicke auf die Buttons, um die Zellzahl zu erhöhen:")

cols = st.columns(len(wbc_types))
for i, cell in enumerate(wbc_types):
    with cols[i]:
        if st.button(f"{cell}\n({st.session_state['counts'][cell]})", key=f"btn_{cell}"):
            increase_count(cell)
            st.rerun()

st.markdown("---")

# Diagramm zur Visualisierung der Zellverteilung
st.subheader("📊 Zellverteilung")
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(wbc_types, [st.session_state['counts'][cell] for cell in wbc_types], color=button_colors, edgecolor='black', alpha=0.8)
ax.set_ylabel("Anzahl der Zellen", fontsize=12)
ax.set_xlabel("Blutzelltypen", fontsize=12)
ax.set_title("Verteilung der Blutzellen", fontsize=14, fontweight='bold')
ax.set_xticks(np.arange(len(wbc_types)))
ax.set_xticklabels(wbc_types, rotation=30, ha="right", fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
st.pyplot(fig)