import streamlit as st
from PIL import Image

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


st.set_page_config(page_title="View/Edit Inventory", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 5])
with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Current Book Inventory")
