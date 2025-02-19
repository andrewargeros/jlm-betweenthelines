import streamlit as st
import pandas as pd
import segno
import os
import pyshorteners
from PIL import Image
from io import BytesIO
from datetime import datetime
from supabase import create_client, Client

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


@st.cache_resource
def create_supa_client():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


def create_qr(url, output="qr.png"):
    qr = segno.make(url, error="h", version=4, micro=False)
    qr.save(output, scale=100)
    return output


def format_qr(qr_image_path):
    qr_image = Image.open(qr_image_path)
    logo = Image.open(".streamlit/jlm-logo.png")  # Replace with your image path

    qr_width, qr_height = qr_image.size
    logo_size = min(qr_width, qr_height) // 4
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    logo_x = (qr_width - logo_size) // 2
    logo_y = (qr_height - logo_size) // 2

    qr_image.paste(logo, (logo_x, logo_y), logo.convert("RGBA"))

    return qr_image


def save_all_qr_codes(df, supabase):
    temp_dir = f"media/{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    for row in df.itertuples():
        url = supabase.storage.from_("mp3-uploads").get_public_url(row.name)
        url = st.session_state.shortener.tinyurl.short(url)
        qr_image_path = create_qr(url, f"{temp_dir}/{row.name.split('.')[0]}.png")
        qr = format_qr(qr_image_path)
        qr.save(f"{temp_dir}/{row.name.split('.')[0]}.png")

    os.system(f"zip -r {temp_dir}.zip {temp_dir}")
    os.system(f"rm -rf {temp_dir}")
    return temp_dir + ".zip"


def create_button():
    st.session_state["create"] = True


if "shortener" not in st.session_state:
    st.session_state.shortener = pyshorteners.Shortener()

st.set_page_config(page_title="Create a QR Code", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = False
    st.error("Please authenticate from the home page to continue.")


c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Create a QR Code")

if "supabase" not in st.session_state:
    st.session_state.supabase = create_supa_client()

if "df" not in st.session_state:
    json_data = (
        st.session_state.supabase.table("book_orders")
        .select("inmate_name, book_inventory(book_title), address_name, mp3_file_id")
        .execute()
        .data
    )
    st.session_state.df = pd.DataFrame(json_data)
    files = st.session_state.supabase.storage.from_("mp3-uploads").list()
    files_df = pd.DataFrame(files)

    st.session_state.df = st.session_state.df.merge(
        files_df, left_on="mp3_file_id", right_on="id", how="inner"
    )


if "create" not in st.session_state:
    st.session_state.create = False

if st.session_state["authentication_status"]:
    st.dataframe(st.session_state["df"], hide_index=True)

    choice = st.selectbox(
        "Select a file to create a QR code", st.session_state["df"]["name"]
    )

    create1, create2 = st.columns(2)
    with create1:
        st.button(
            "Create QR Code",
            type="primary",
            icon=":material/qr_code_2_add:",
            use_container_width=True,
            on_click=create_button,
        )
        if st.session_state["create"]:
            url = st.session_state.supabase.storage.from_("mp3-uploads").get_public_url(
                choice
            )
            url = st.session_state.shortener.tinyurl.short(url)

            qr_image_path = create_qr(url)
            qr_image = format_qr(qr_image_path)

            st.image(qr_image.resize((6 * 300, 6 * 300)), width=300)

            file_name = st.text_input("Enter the file name", value="qr.png")
            qr_image_buffer = BytesIO()
            qr_image.save(qr_image_buffer, format="PNG")
            st.download_button(
                "Download QR Code",
                qr_image_buffer.getvalue(),
                file_name,
                icon=":material/download:",
                mime="image/png",
                use_container_width=True,
            )

    with create2:
        if st.button(
            "Save All QR Codes",
            type="primary",
            icon=":material/downloading:",
            use_container_width=True,
        ):
            zip_file_path = save_all_qr_codes(
                st.session_state["df"], st.session_state["supabase"]
            )
            with open(zip_file_path, "rb") as fp:
                st.download_button(
                    label="Download ZIP with all QR Codes",
                    data=fp,
                    file_name=zip_file_path.split("/")[-1],
                    mime="application/zip",
                    icon=":material/download:",
                )
            st.balloons()
