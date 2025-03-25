import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# Initialize the data manager
data_manager = DataManager(fs_protocol='webdav', fs_root_folder="WBC_Data")  # switch drive


# Load the data from the persistent storage into the session state
data_manager.load_user_data(
    session_state_key='data_df', 
    file_name='data.csv', 
    initial_value=pd.DataFrame(), 
    parse_dates=['timestamp']
)

# Titel der App
st.set_page_config(page_title="Blood Cell Counter", layout="wide")

# Navigation über separate Seiten
st.title("Blood Cell Counter")
