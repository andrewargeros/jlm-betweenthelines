import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
from supabase import create_client, Client

file_path = str(Path(__file__).parent)
JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


@st.cache_resource
def create_supa_client():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


def get_mp3_files(supabase: Client) -> pd.DataFrame:
    res = supabase.storage().from_("mp3-uploads").list()
    return pd.DataFrame(res)


st.set_page_config(page_title="Upload and Sync MP3s", page_icon=JLM_LOGO)

if "supabase" not in st.session_state:
    st.session_state.supabase = create_supa_client()

if "xsupabase_files" not in st.session_state:
    st.session_state.xsupabase_files = get_mp3_files(st.session_state.supabase)

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = False
    st.error("Please authenticate from the home page to continue.")


with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Upload and Sync MP3 Recording Files")


if st.session_state["authentication_status"]:

    st.subheader("Current Files in Database")
    st.dataframe(st.session_state.xsupabase_files, hide_index=True)

    u1, u2 = st.columns(2)

    with u1:
        st.subheader("Upload MP3 File")
        uploaded_file = st.file_uploader("Upload MP3 File", type=["mp3"])
        if uploaded_file:
            if type(uploaded_file) != list:
                uploaded_file = [uploaded_file]
            for file in uploaded_file:
                st.session_state.supabase.storage().from_("mp3-uploads").upload(
                    file.name, file.getvalue()
                )
            st.success(f"{len(uploaded_file)} File(s) uploaded successfully.")

    with u2:
        if st.button("Sync Files", icon=":material/sync:"):
            st.session_state.xsupabase_files = get_mp3_files(st.session_state.supabase)

    st.subheader("Link a File to a Book Order")
    orders = st.session_state.supabase.table("book_orders").select("*").execute().data
    order_df = (
        pd.DataFrame(orders)
        .query("mp3_file_id.isnull()")
        .assign(stub=lambda x: x["inmate_name"] + " - " + x["id"].astype(str))
    )
    unclaimed_files = st.session_state["xsupabase_files"].query(
        "id not in @order_df['mp3_file_id']"
    )

    with st.form(key="link_form"):
        order_stub = st.selectbox("Select an Order", order_df["stub"])
        file_name = st.selectbox("Select a File ID", unclaimed_files["name"])
        if st.form_submit_button(
            "Link File to Order", type="primary", icon=":material/link:"
        ):
            file_id = unclaimed_files.query("name == @file_name")["id"].values[0]
            order_id = order_df.query("stub == @order_stub")["id"].values[0]
            st.session_state.supabase.table("book_orders").update(
                {"mp3_file_id": file_id}
            ).eq("id", order_id).execute()

            st.success("File linked to order successfully.")
