import streamlit as st
from PIL import Image
import base64
from io import BytesIO

def show_logo(path="images/logo.png"):
    def logo_to_base64(img):
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    logo = Image.open(path)
    encoded_logo = logo_to_base64(logo)

    st.markdown(
        f'<img src="data:image/png;base64,{encoded_logo}" width="140">',
        unsafe_allow_html=True
    )