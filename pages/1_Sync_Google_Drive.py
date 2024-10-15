import streamlit as st
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from PIL import Image

JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


@st.cache_resource
def create_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("../mycreds.txt")
    drive = GoogleDrive(gauth)
    return drive


def list_files(drive):
    all_files = []
    file_list = drive.ListFile(
        {"q": "'19X1I-K__Oq-f_ADcbEZZk430X1JdK8Ib' in parents and trashed=false"}
    ).GetList()
    for file1 in file_list:
        print("title: %s, id: %s" % (file1["title"], file1["id"]))
        file_list2 = drive.ListFile(
            {"q": "'%s' in parents and trashed=false" % file1["id"]}
        ).GetList()
        for file2 in file_list2:
            if file2["title"].lower().endswith(".mp3"):
                print(
                    "title: %s, id: %s, link: %s"
                    % (file2["title"], file2["id"], file2["alternateLink"])
                )
                entry = {
                    "subfolder": file1["title"],
                    "title": file2["title"],
                    "id": file2["id"],
                    "link": file2["alternateLink"],
                }
                all_files.append(entry)
    return pd.DataFrame(all_files)


def upload_csv(drive, df, filename):
    df.to_csv(filename, index=False)
    file1 = drive.CreateFile(
        {
            "title": filename,
            "parents": [{"id": "19X1I-K__Oq-f_ADcbEZZk430X1JdK8Ib"}],
        }
    )
    file1.SetContentFile(filename)
    file1.Upload()
    return "Created file %s with mimeType %s" % (file1["title"], file1["mimeType"])


if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["subfolder", "title", "id", "link"])

st.set_page_config(page_title="Load Files from Drive", page_icon=JLM_LOGO)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Load Files from Google Drive")

drive = create_drive()
st.session_state["df"] = pd.concat(
    [st.session_state["df"], list_files(drive)]
).drop_duplicates()

st.dataframe(st.session_state["df"], hide_index=True)

st.markdown(f"Current number of files: {len(st.session_state['df'])}")

st.button(
    "Sync to Google Drive",
    on_click=upload_csv,
    args=(drive, st.session_state["df"], "all_mp3_files.csv"),
    type="primary",
)
