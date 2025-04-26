import streamlit as st
import pandas as pd
import datetime

# App Setup
st.set_page_config(page_title="Morphologische Beurteilung App", layout="wide")
st.title("Rotes Blutbild")

# --- Patienteninformationen ---

st.subheader("Patientendaten")

# Patienten-ID überprüfen oder neu eingeben
if "patient_id" not in st.session_state or not st.session_state["patient_id"]:
    patient_id = st.text_input("Patienten-ID eingeben", placeholder="z.B. 12345")
    if patient_id:
        st.session_state["patient_id"] = patient_id
else:
    patient_id = st.session_state["patient_id"]
    st.success(f"Patienten-ID übernommen: {patient_id}")

# Geschlecht und Geburtsdatum überprüfen oder neu eingeben
if "gender" not in st.session_state or "birth_date" not in st.session_state:
    gender = st.radio("Geschlecht auswählen:", ["Männlich", "Weiblich"], index=0)
    birth_date = st.date_input("Geburtsdatum eingeben:")
    st.session_state["gender"] = gender
    st.session_state["birth_date"] = birth_date.strftime("%d.%m.%Y")
else:
    gender = st.session_state["gender"]
    birth_date_str = st.session_state["birth_date"]
    try:
        birth_date = datetime.datetime.strptime(birth_date_str, "%d.%m.%Y").date()
    except ValueError:
        birth_date = None

# Alter berechnen
if birth_date:
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
else:
    age = None

# Patienteninfo schön darstellen
patient_info = f"**Geschlecht:** {gender}"
if birth_date:
    patient_info += f", **Geburtsdatum:** {birth_date.strftime('%d.%m.%Y')}"
if age is not None:
    patient_info += f", **Alter:** {age} Jahre"
if patient_id:
    patient_info += f", **Patienten-ID:** {patient_id}"

st.markdown(patient_info)

# --- Morphologische Auffälligkeiten ---

# Begriffe kategorisiert
form_changes = [
    "Mikrozytär", "Makrozytär", "Anisozytose", "Poikilozytose",
    "Targetzellen", "Fragmentozyten", "Sichelzellen", "Sphärozyten",
    "Elliptozyten", "Stomatozyten"
]
color_changes = ["Hypochrom", "Hyperchrom", "Polychromasie"]
inclusions = ["Basophile Tüpfelung", "Howell-Jolly-Körperchen", "Pappenheimer-Körperchen", "Heinz-Innenkörperchen"]
special_behaviors = ["Erythroblasten", "Geldrollenbildung"]

# Alle Begriffe zusammenführen
morphological_changes = form_changes + color_changes + inclusions + special_behaviors

# Ergebnisse speichern
results = {}

st.subheader("Morphologische Auffälligkeiten")
st.markdown("Bitte bewerten Sie die morphologischen Veränderungen:")

# Kompakt: Begriff + Slider direkt nebeneinander
for change in morphological_changes:
    with st.container():
        col1, col2 = st.columns([2, 5])
        with col1:
            st.markdown(f"**{change}:**")
        with col2:
            results[change] = st.select_slider(
                label="",
                options=["Keine", "Leicht", "Mittel", "Stark"],
                value="Keine",
                key=change
            )

# Hilfsfunktion für schöne Farbdarstellung
def style_severity(severity):
    if severity == "Stark":
        return ":red[**Stark**]"
    elif severity == "Mittel":
        return ":orange[**Mittel**]"
    elif severity == "Leicht":
        return ":green[**Leicht**]"
    else:
        return ":gray[Keine]"

# --- Zusammenfassung der Eingaben ---

st.markdown("---")
st.subheader("📋 Zusammenfassung deiner Einschätzungen")

with st.container():
    for param, severity in results.items():
        if severity != "Keine":
            st.markdown(f"**{param}**: {style_severity(severity)}")

# --- Speicherung ---

st.markdown("---")
if st.button("Ergebnisse speichern"):
    results_with_id = results.copy()
    results_with_id["Patienten-ID"] = st.session_state.get("patient_id", "")
    
    results_df = pd.DataFrame([results_with_id])
    results_df.to_csv("morphologische_beurteilung_app.csv", index=False)
    st.success("Ergebnisse wurden als 'morphologische_beurteilung_app.csv' gespeichert!")

# Ergebnisse im Session State sichern
st.session_state['morphology_results'] = results
