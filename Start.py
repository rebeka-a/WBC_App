import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager


# Titel der App
st.set_page_config(page_title="Blood Cell Data & Reference Values", layout="wide")

# Initialize the data manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="WBC_Data")  # switch drive

# Login-Logik
login_manager = LoginManager(data_manager)
login_manager.login_register()


# Titel der App
st.title("Blood Cell Counter")
st.write("This app helps you to count blood cells and compare them with reference values.")

# Load the data from the persistent storage into the session state
data_manager.load_user_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value=pd.DataFrame(columns=["timestamp", "counts", "gender", "birth_date"]),  # Initialisiere mit Standardspalten
    parse_dates=['timestamp']
)

# Navigation über separate Seiten
