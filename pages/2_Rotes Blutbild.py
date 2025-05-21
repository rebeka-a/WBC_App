import streamlit as st
import pandas as pd
import datetime
from utils.data_manager import DataManager
from utils.login_manager import LoginManager
from PIL import Image

# App Setup
st.set_page_config(page_title="Morphologische Beurteilung", layout="wide")

# --- DataManager und LoginManager initialisieren ---
data_manager = DataManager()
login_manager = LoginManager(data_manager)
st.sidebar.image("images/logo-bloodcell-counter.png.jpg", use_container_width=True)

# --- Zugriffsschutz ---
login_manager.go_to_login('Start.py')

st.title("Morphologische Beurteilung des Roten Blutbildes")

# --- Patienteninformationen ---
st.subheader("Patientendaten 📋")

# Patienten-ID
patient_id = st.text_input(
    "Patienten-ID",
    value=st.session_state.get("patient_id", ""),
    placeholder="z.B. 12345"
)
if patient_id:
    st.session_state["patient_id"] = patient_id

# Geschlecht
if "gender" not in st.session_state:
    st.session_state["gender"] = ""

gender = st.selectbox(
    "Geschlecht",
    options=["", "Männlich", "Weiblich"],
    index=["", "Männlich", "Weiblich"].index(st.session_state["gender"]) if st.session_state["gender"] in ["Männlich", "Weiblich"] else 0
)
if gender:
    st.session_state["gender"] = gender

# Geburtsdatum
if "birth_date" not in st.session_state:
    st.session_state["birth_date"] = ""

birth_date_input = st.text_input(
    "Geburtsdatum (TT.MM.JJJJ)",
    value=st.session_state.get("birth_date", ""),
    placeholder="z.B. 01.01.2000"
)

# Validierung des Geburtsdatums
try:
    if birth_date_input:
        birth_date_obj = datetime.datetime.strptime(birth_date_input, "%d.%m.%Y").date()
        st.session_state["birth_date"] = birth_date_input
    else:
        birth_date_obj = None
except ValueError:
    birth_date_obj = None
    st.error("Ungültiges Datumsformat! Bitte TT.MM.JJJJ verwenden.")

# Patientendaten zurücksetzen
if st.button("Patientendaten zurücksetzen", key="reset_patient_button", use_container_width=True):
    st.session_state.pop("patient_id", None)
    st.session_state.pop("gender", None)
    st.session_state.pop("birth_date", None)
    st.success("Patientendaten wurden zurückgesetzt!")
    st.rerun()

# Alter berechnen (nur intern genutzt)
if birth_date_obj:
    today = datetime.date.today()
    age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
else:
    age = None

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

st.markdown("---")
st.subheader("Morphologische Auffälligkeiten 🔬")

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

# Farbliche Darstellung je nach Schweregrad
def style_severity(severity):
    if severity == "Stark":
        return ":red[**Stark**]"
    elif severity == "Mittel":
        return ":orange[**Mittel**]"
    elif severity == "Leicht":
        return ":green[**Leicht**]"
    else:
        return ":gray[Keine]"

# --- Zusammenfassung der morphologischen Beurteilung ---
auffaelligkeiten = {param: severity for param, severity in results.items() if severity != "Keine"}

if auffaelligkeiten:
    st.markdown("---")
    st.subheader("Zusammenfassung der morphologischen Beurteilung")
    for param, severity in auffaelligkeiten.items():
        st.markdown(f"**{param}**: {style_severity(severity)}")

# Ergebnisse nur intern im Session State speichern
st.session_state['morphology_results'] = results

if st.button("Zum Weissen Blutbild"):
    st.switch_page("pages/1_Weisses Blutbild.py")
    
if st.button("Zur Auswertung"):
    st.switch_page("pages/3_Auswertung.py")


