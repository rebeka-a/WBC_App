import streamlit as st
import pandas as pd

# App Setup
st.set_page_config(page_title="Morphologische Beurteilung App", layout="wide")
st.title("Rotes Blutbild")

#Patienten-ID übernehmen oder eingeben
st.subheader("Patientendaten")

if "patient_id" in st.session_state and st.session_state["patient_id"]:
    # Wenn bereits eine Patienten-ID existiert, zeige sie an
    patient_id = st.session_state["patient_id"]
    st.success(f"Patienten-ID übernommen: {patient_id}")
else:
    # Sonst Eingabefeld anbieten
    patient_id = st.text_input("Patienten-ID eingeben (optional)", placeholder="z.B. 12345")
    st.session_state["patient_id"] = patient_id

# Begriffe kategorisiert
form_changes = ["Mikrozytär", "Makrozytär", "Anisozytose", "Poikilozytose", "Targetzellen", "Fragmentozyten", "Sichelzellen", "Sphärozyten", "Elliptozyten", "Stomatozyten"]
color_changes = ["Hypochrom", "Hyperchrom", "Polychromasie"]
inclusions = ["Basophile Tüpfelung", "Howell-Jolly-Körperchen", "Pappenheimer-Körperchen", "Heinz-Innenkörperchen"]
special_behaviors = ["Erythroblasten", "Geldrollenbildung"]

# Alle Begriffe zusammenführen
morphological_changes = form_changes + color_changes + inclusions + special_behaviors

# Ergebnisse speichern
results = {}

st.subheader("Morphologische Auffälligkeiten")
st.markdown("""
Bitte bewerten Sie die morphologischen Veränderungen:
""")

# Kompakt: Begriff + Slider direkt nebeneinander
for change in morphological_changes:
    with st.container():
        col1, col2 = st.columns([2, 5])  # Begriff schmal, Slider breit
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

st.markdown("---")
st.subheader("📋 Zusammenfassung deiner Einschätzungen")

# Zusammenfassung schön auflisten
with st.container():
    for param, severity in results.items():
        if severity != "Keine":  # Nur Auffälligkeiten anzeigen
            st.markdown(f"**{param}**: {style_severity(severity)}")

# Speicherung
st.markdown("---")
if st.button("Ergebnisse speichern"):
    # Alles speichern in eine Tabelle
    results_with_id = results.copy()
    results_with_id["Patienten-ID"] = st.session_state["patient_id"]  # Patienten-ID übernehmen
    
    results_df = pd.DataFrame([results_with_id])
    results_df.to_csv("morphologische_beurteilung_app.csv", index=False)
    st.success("Ergebnisse wurden als 'morphologische_beurteilung_app.csv' gespeichert!")

# Ergebnisse in den Session State schreiben
st.session_state['morphology_results'] = results
