import streamlit as st
from PIL import Image
import streamlit_authenticator as stauth
import yaml
import os
from supabase import create_client, Client


@st.cache_resource
def create_supa_client():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


JLM_LOGO = Image.open(".streamlit/jlm-logo.png")
st.set_page_config(page_title="Between the Lines", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")

if "supabase" not in st.session_state:
    st.session_state.supabase = create_supa_client()

if "users" not in st.session_state:
    with open(".streamlit/login_config.yml") as f:
        st.session_state.users = yaml.safe_load(f)

if "passwords_list" not in st.session_state:
    st.session_state.passwords_list = (
        st.session_state.supabase.table("users")
        .select("user_name, hashed_password")
        .execute()
        .data
    )

for user in st.session_state.passwords_list:
    st.session_state.users["credentials"]["usernames"][user["user_name"]][
        "password"
    ] = user["hashed_password"]

if "client_secrets.json" not in os.listdir("."):
    with open("client_secrets.json", "wb+") as f:
        res = st.session_state.supabase.storage.from_("jlm-bucket").download()
        f.write(res)


authenticator = stauth.Authenticate(
    st.session_state.users["credentials"],
    st.session_state.users["cookie"]["name"],
    st.session_state.users["cookie"]["key"],
    st.session_state.users["cookie"]["expiry_days"],
)


st.markdown(
    """
    Between the Lines provides children of incarcerated female parent/caregivers an audio recording of their parent/caregiver reading a book to them, a personal message from their parent/caregiver and a new, wrapped, copy of the book. Junior League volunteers record the incarcerated parent/caregiver, prepare and send the special book/message packages for delivery to the children.

    This app is designed to help Junior League volunteers manage the process of syncing files from Google Drive, creating address labels, creating QR codes, and parsing who's reading what.
    
    <br>

    ### **What would you like to do?**
    """,
    unsafe_allow_html=True,
)
authenticator.login()


if st.session_state["authentication_status"]:
    g1, g2 = st.columns(2)

    with g1:
        st.page_link(
            "pages/1_Sync_Google_Drive.py",
            label="**Sync** Files from Google Drive",
            icon=":material/add_to_drive:",
            use_container_width=True,
        )
        st.page_link(
            "pages/3_Create_An_Address_Label.py",
            label="**Create an Address Label**",
            icon=":material/contact_mail:",
            use_container_width=True,
        )
        st.page_link(
            "pages/5_View_or_Edit_Inventory.py",
            label="**View/Edit Inventory**",
            icon=":material/shelves:",
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
