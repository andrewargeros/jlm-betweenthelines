import streamlit as st
import pandas as pd
import segno
from PIL import Image
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


@st.cache_resource
def create_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("../mycreds.txt")
    drive = GoogleDrive(gauth)
    return drive


def create_qr(url, output="qr.png"):
    qr = segno.make(url, error="h", version=10, micro=False)
    qr.save(output, scale=100)
    return output


def format_qr(qr_image_path):
    qr_image = Image.open(qr_image_path)
    logo = Image.open(".streamlit/jlm-logo.png")  # Replace with your image path

    qr_width, qr_height = qr_image.size
    logo_size = min(qr_width, qr_height) // 4
    logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)

    logo_x = (qr_width - logo_size) // 2
    logo_y = (qr_height - logo_size) // 2

    qr_image.paste(logo, (logo_x, logo_y), logo.convert("RGBA"))

    return qr_image


def save_all_qr_codes(df):
    for row in df.itertuples():
        qr_image_path = create_qr(row.link, f"media/{row.title.split('.')[0]}.png")
        qr = format_qr(qr_image_path)
        qr.save(f"media/{row.title.split('.')[0]}.png")


def load_drive_csv(drive):
    file_id = "19X1I-K__Oq-f_ADcbEZZk430X1JdK8Ib"
    file = drive.CreateFile({"id": file_id})
    file.GetContentFile("all_mp3_files.csv")
    return pd.read_csv("all_mp3_files.csv")


if "df" not in st.session_state:
    drive = create_drive()
    st.session_state.df = load_drive_csv(drive)

st.set_page_config(page_title="Create a QR Code", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Create a QR Code")

st.dataframe(st.session_state["df"], hide_index=True)

choice = st.selectbox(
    "Select a file to create a QR code", st.session_state["df"]["title"]
)

create1, create2 = st.columns(2)
with create1:
    if st.button(
        "Create QR Code",
        type="primary",
        icon=":material/qr_code_2_add:",
        use_container_width=True,
    ):
        url = (
            st.session_state["df"]
            .loc[st.session_state["df"]["title"] == choice, "link"]
            .values[0]
        )
        qr_image_path = create_qr(url)
        qr_image = format_qr(qr_image_path)

        img_c1, img_c2 = st.columns(2)

        with img_c1:
            st.image(qr_image.resize((6 * 300, 6 * 300)), width=300)

        with img_c2:
            file_name = st.text_input("Enter the file name", value="qr.png")
            st.button(
                "Download QR Code", qr_image.save, file_name, icon=":material/download:"
            )
with create2:
    if st.button(
        "Save All QR Codes",
        type="primary",
        icon=":material/downloading:",
        use_container_width=True,
    ):
        save_all_qr_codes(st.session_state["df"])
        st.write("All QR codes saved to media folder")
        st.balloons()
