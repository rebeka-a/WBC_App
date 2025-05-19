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
        <div style="position: relative; margin-top: 0; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{encoded_logo}"
                 style="
                     display: block;
                     width: 140px;
                     height: auto;
                     max-width: 100%;
                 "
                 alt="Logo" />
        </div>
        """,
        unsafe_allow_html=True
    )