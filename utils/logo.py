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
        <style>
            /* Logo auf mobilen Geräten kleiner darstellen */
            @media (max-width: 768px) {{
                .logo-img {{
                    width: 100px !important;
                    height: auto !important;
                }}
            }}
        </style>

        <div style="display: flex; align-items: flex-start; justify-content: flex-start;
                    margin-bottom: 1rem;">
            <img src="data:image/png;base64,{encoded_logo}" 
                 alt="Logo" 
                 class="logo-img"
                 style="width: 25vw; max-width: 160px; min-width: 80px; height: auto;" />
        </div>
        """,
        unsafe_allow_html=True
    )