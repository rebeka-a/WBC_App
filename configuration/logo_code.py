# components/logo.py

import streamlit as st
from PIL import Image
import base64
from io import BytesIO

def show_logo(path="images/logo.png"):
    def logo_to_base64(image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    logo = Image.open(path)
    encoded_logo = logo_to_base64(logo)

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            margin-bottom: 1rem;
            padding-left: 0rem;
        ">
            <img src="data:image/png;base64,{encoded_logo}"
                 style="width: 140px; max-width: 100%; height: auto;"
                 alt="Logo" />
        </div>
        """,
        unsafe_allow_html=True
    )