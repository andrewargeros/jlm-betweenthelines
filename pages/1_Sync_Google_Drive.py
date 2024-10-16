import streamlit as st
import pandas as pd
from pathlib import Path
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
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


def upload_csv(drive_df, supa_df, supabase):
    upload = drive_df.query("id not in @supa_df['id']")
    upload = upload[["id", "title", "link"]].to_dict(orient="records")
    supabase.table("mp3_files").insert(upload).execute()


st.set_page_config(page_title="Load Files from Drive", page_icon=JLM_LOGO)

if "supabase" not in st.session_state:
    st.session_state.supabase = create_supa_client()

if "mp3_df" not in st.session_state:
    st.session_state.mp3_df = pd.DataFrame(
        st.session_state.supabase.table("mp3_files").select("*").execute().data
    )

if "drive_files" not in st.session_state:
    st.session_state.drive_files = pd.DataFrame(
        columns=["subfolder", "title", "id", "link"]
    )


with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 5])

with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")
st.subheader("Load Files from Google Drive")

drive = create_drive()
st.session_state["drive_files"] = pd.concat(
    [st.session_state["drive_files"], list_files(drive)]
).drop_duplicates()

st.dataframe(st.session_state["mp3_df"], hide_index=True)


foo = st.session_state["drive_files"].query(
    "id not in @st.session_state['mp3_df']['id']"
)

if not foo.empty:
    st.markdown(f"Additional Files to Add: {len(foo)}")
    st.dataframe(foo, hide_index=True)

st.button(
    "Sync to Google Drive",
    on_click=upload_csv,
    args=(
        st.session_state["drive_files"],
        st.session_state["mp3_df"],
        st.session_state["supabase"],
    ),
    type="primary",
    icon=":material/add_to_drive:",
)

st.subheader("Link a File to a Book Order")
orders = st.session_state.supabase.table("book_orders").select("*").execute().data
order_df = (
    pd.DataFrame(orders)
    .query("mp3_file_id.isnull()")
    .assign(stub=lambda x: x["inmate_name"] + " - " + x["id"].astype(str))
)
unclaimed_files = st.session_state["mp3_df"].query("id not in @order_df['mp3_file_id']")

with st.form(key="link_form"):
    order_stub = st.selectbox("Select an Order", order_df["stub"])
    file_id = st.selectbox("Select a File ID", unclaimed_files["id"])
    if st.form_submit_button(
        "Link File to Order", type="primary", icon=":material/link:"
    ):
        order_id = order_df.query("stub == @order_stub")["id"].values[0]
        st.session_state.supabase.table("book_orders").update(
            {"mp3_file_id": file_id}
        ).eq("id", order_id).execute()

        st.success("File linked to order successfully.")
