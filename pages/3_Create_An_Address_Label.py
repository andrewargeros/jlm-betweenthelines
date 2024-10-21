import streamlit as st
from PIL import Image
from blabel import LabelWriter

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


st.set_page_config(page_title="Create an Address Label", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "labe_writer" not in st.session_state:
    html_file = "templates/address_label_template.html"
    css_file = "templates/address_label_template.css"
    st.session_state.label_writer = LabelWriter(html_file, css_file)

if "address" not in st.session_state:
    st.session_state.address = {}

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Create an Address Label")

if st.session_state["authentication_status"]:
    with st.form(key="address_form"):
        input_type = st.radio("Input Type", ["Manual", "Pick a Row"])

        name = st.text_input("Name")
        address = st.text_input("Address")
        address2 = st.text_input("Address Line 2")
        a1, a2, a3 = st.columns(3)
        with a1:
            city = st.text_input("City")
        with a2:
            state = st.text_input("State")
        with a3:
            zip_code = st.text_input("Zip Code")

        if st.form_submit_button(
            "Create Address Label", type="primary", icon=":material/local_shipping:"
        ):
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <h3>{name}</h3>
                    <p>{address}</p>
                    <p>{address2}</p>
                    <p>{city}, {state} {zip_code}</p>""",
                unsafe_allow_html=True,
            )

            address = [
                {
                    "logo": ".streamlit/jlm-logo.png",
                    "address_name": name,
                    "address_1": address,
                    "address_2": address2,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                }
            ]

            st.session_state.label_writer.write_labels(address, target="test.pdf")
