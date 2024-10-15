import streamlit as st
from PIL import Image

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")
st.set_page_config(page_title="Between the Lines", page_icon=JLM_LOGO)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")

st.markdown(
    """
    Between the Lines provides children of incarcerated female parent/caregivers an audio recording of their parent/caregiver reading a book to them, a personal message from their parent/caregiver and a new, wrapped, copy of the book. Junior League volunteers record the incarcerated parent/caregiver, prepare and send the special book/message packages for delivery to the children.

    This app is designed to help Junior League volunteers manage the process of syncing files from Google Drive, creating address labels, creating QR codes, and parsing who's reading what.
    
    <br><br>
    ### **What would you like to do?**
    """,
    unsafe_allow_html=True,
)

g1, g2 = st.columns(2)

with g1:
    st.page_link(
        "pages/1_Sync_Google_Drive.py",
        label="**Sync Files from Google Drive**",
        icon=":material/add_to_drive:",
        use_container_width=True,
    )
    st.page_link(
        "pages/3_Create_An_Address_Label.py",
        label="**Create an Address Label**",
        icon=":material/contact_mail:",
        use_container_width=True,
    )

with g2:
    st.page_link(
        "pages/2_Create_A_QR_Code.py",
        label="**Create a QR Code**",
        icon=":material/qr_code_scanner:",
        use_container_width=True,
    )
    st.page_link(
        "pages/4_Parse_Whos_Reading_What.py",
        label="**Parse Who's Reading What**",
        icon=":material/menu_book:",
        use_container_width=True,
    )
