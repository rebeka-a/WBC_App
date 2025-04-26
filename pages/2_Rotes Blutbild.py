import streamlit as st
import pandas as pd
import datetime

# App Setup
st.set_page_config(page_title="Morphologische Beurteilung App", layout="wide")
st.title("Rotes Blutbild")

# --- Patienteninformationen ---

st.subheader("Patientendaten")

# Patienten-ID
patient_id = st.text_input(
    "Patienten-ID eingeben",
    value=st.session_state.get("patient_id", ""),
    placeholder="z.B. 12345"
)
if patient_id:
    st.session_state["patient_id"] = patient_id

# Geschlecht
if "gender" not in st.session_state:
    st.session_state["gender"] = ""

gender = st.selectbox(
    "Geschlecht auswählen:",
    options=["", "Männlich", "Weiblich"],
    index=["", "Männlich", "Weiblich"].index(st.session_state["gender"]) if st.session_state["gender"] in ["Männlich", "Weiblich"] else 0
)

if gender != "":
    st.session_state["gender"] = gender
else:
    st.session_state["gender"] = ""

# Geburtsdatum
if "birth_date" in st.session_state:
    try:
        birth_date = datetime.datetime.strptime(st.session_state["birth_date"], "%d.%m.%Y").date()
    except:
        birth_date = None
else:
    birth_date = None

birth_date_input = st.date_input(
    "Geburtsdatum eingeben:",
    value=birth_date if birth_date else None,
    format="DD.MM.YYYY"
)

if birth_date_input:
    st.session_state["birth_date"] = birth_date_input.strftime("%d.%m.%Y")
else:
    st.session_state["birth_date"] = ""

# 🔹 Patientendaten zurücksetzen Button direkt unter der Eingabe:
if st.button("🧹 Patientendaten zurücksetzen", key="reset_patient_button", use_container_width=True):
    st.session_state.pop("patient_id", None)
    st.session_state.pop("gender", None)
    st.session_state.pop("birth_date", None)
    st.success("Patientendaten wurden zurückgesetzt!")
    st.rerun()

# Alter berechnen
if st.session_state.get("birth_date"):
    birth_date_obj = datetime.datetime.strptime(st.session_state["birth_date"], "%d.%m.%Y").date()
    today = datetime.date.today()
    age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
else:
    age = None

# Patienteninfo schön darstellen
patient_info = ""

if st.session_state.get("gender"):
    patient_info += f"**Geschlecht:** {st.session_state['gender']}"
else:
    patient_info += "**Geschlecht:** Nicht angegeben"

if st.session_state.get("birth_date"):
    patient_info += f", **Geburtsdatum:** {st.session_state['birth_date']}"

if age is not None:
    patient_info += f", **Alter:** {age} Jahre"

if st.session_state.get("patient_id"):
    patient_info += f", **Patienten-ID:** {st.session_state['patient_id']}"

st.markdown(patient_info)

# --- Morphologische Auffälligkeiten ---

form_changes = [
    "Mikrozytär", "Makrozytär", "Anisozytose", "Poikilozytose",
    "Targetzellen", "Fragmentozyten", "Sichelzellen", "Sphärozyten",
    "Elliptozyten", "Stomatozyten"
]
color_changes = ["Hypochrom", "Hyperchrom", "Polychromasie"]
inclusions = ["Basophile Tüpfelung", "Howell-Jolly-Körperchen", "Pappenheimer-Körperchen", "Heinz-Innenkörperchen"]
special_behaviors = ["Erythroblasten", "Geldrollenbildung"]

morphological_changes = form_changes + color_changes + inclusions + special_behaviors

results = {}

st.subheader("Morphologische Auffälligkeiten")
st.markdown("Bitte bewerten Sie die morphologischen Veränderungen:")

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

# Farbliche Darstellung
def style_severity(severity):
    if severity == "Stark":
        return ":red[**Stark**]"
    elif severity == "Mittel":
        return ":orange[**Mittel**]"
    elif severity == "Leicht":
        return ":green[**Leicht**]"
    else:
        return ":gray[Keine]"

# --- Zusammenfassung ---

st.markdown("---")
st.subheader("📋 Zusammenfassung deiner Einschätzungen")

with st.container():
    for param, severity in results.items():
        if severity != "Keine":
            st.markdown(f"**{param}**: {style_severity(severity)}")

# --- Speicherung ---

st.markdown("---")
if st.button("Ergebnisse speichern"):
    if not st.session_state.get("patient_id") or not st.session_state.get("gender") or not st.session_state.get("birth_date"):
        st.error("Bitte vollständige Patientendaten eingeben (ID, Geschlecht, Geburtsdatum), bevor gespeichert werden kann!")
    else:
        results_with_id = results.copy()
        results_with_id["Patienten-ID"] = st.session_state.get("patient_id", "")
        results_with_id["Geschlecht"] = st.session_state.get("gender", "")
        results_with_id["Geburtsdatum"] = st.session_state.get("birth_date", "")

        results_df = pd.DataFrame([results_with_id])
        results_df.to_csv("morphologische_beurteilung_app.csv", index=False)
        st.success("Ergebnisse wurden als 'morphologische_beurteilung_app.csv' gespeichert!")

# Ergebnisse im Session State sichern
st.session_state['morphology_results'] = results
