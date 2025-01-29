import streamlit as st
import pandas as pd
from PIL import Image
from supabase import create_client, Client


@st.cache_resource
def create_supa_client():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


JLM_LOGO = Image.open(".streamlit/jlm-logo.png")


st.set_page_config(page_title="Book Orders", page_icon=JLM_LOGO)

with open(".streamlit/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "order" not in st.session_state:
    st.session_state.order = {}

if "supabase" not in st.session_state:
    st.session_state.supabase = create_supa_client()

if "books" not in st.session_state:
    st.session_state.books = pd.DataFrame(
        st.session_state.supabase.table("book_inventory")
        .select("id, book_title")
        .execute()
        .data
    )

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = False
    st.error("Please authenticate from the home page to continue.")

c1, c2 = st.columns([1, 5])
with c1:
    st.image(JLM_LOGO, width=100)
with c2:
    st.title("Between the Lines")

if st.session_state["authentication_status"]:
    st.subheader("Create a New Book Order")

    with st.form(key="address_form"):
        st.markdown("#### Upload MP3 File")
        uploaded_file = st.file_uploader("Upload MP3 File", type=["mp3", "MP3"])
        st.markdown("#### Order Information")
        inmate_name = st.text_input(
            "Book Order Name",
            value=uploaded_file.name.split(".")[0] if uploaded_file else "",
        )
        book_title = st.selectbox("Book Title", st.session_state.books["book_title"])

        st.markdown("#### Address")
        recipient_name = st.text_input("Recipient Name")
        address = st.text_input("Address")
        address2 = st.text_input("Address Line 2")

        a1, a2, a3 = st.columns(3)
        with a1:
            city = st.text_input("City")
        with a2:
            state = st.text_input("State")
        with a3:
            zip_code = st.text_input("Zip Code")

        st.markdown("#### Book Information")
        b1, b2, b3 = st.columns(3)
        with b1:
            recording_made = st.checkbox("Recording Made?")
        with b2:
            book_ordered = st.checkbox("Book Ordered?")
        with b3:
            book_mailed = st.checkbox("Book Mailed?")

        if st.form_submit_button(
            "Create Book Order", type="primary", icon=":material/shopping_cart:"
        ):
            book_id = st.session_state.books.loc[
                st.session_state.books["book_title"] == book_title, "id"
            ].values[0]
            order = {
                "inmate_name": inmate_name,
                "book_id": int(book_id),
                "address_name": recipient_name,
                "address_line_1": address,
                "address_line_2": address2,
                "address_city": city,
                "address_state": state,
                "address_zipcode": zip_code,
                "recording_made": recording_made,
                "book_ordered": book_ordered,
                "label_created": False,
                "book_mailed": book_mailed,
            }

            order = {k: v for k, v in order.items() if v is not None and v != ""}

            st.write(order)

            response = (
                st.session_state.supabase.table("book_orders").insert(order).execute()
            )
            st.success("Book order created successfully!")

    st.subheader("Current Book Orders")
    orders_df = pd.DataFrame(
        st.session_state.supabase.table("book_orders")
        .select(
            "id, inmate_name, book_inventory(book_title), created_at, recording_made, label_created, book_ordered, book_mailed"
        )
        .execute()
        .data
    ).assign(
        created_at=lambda x: pd.to_datetime(x["created_at"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
    st.dataframe(orders_df, hide_index=True)

    st.subheader("Secure Address Upload")

    up1, up2 = st.columns(2)

    with up1:
        st.download_button(
            label="Download to Add Adresses",
            data=orders_df.to_csv(index=False),
            file_name="book_orders_addresses_needed.xlsx",
            mime="text/xlsx",
            icon=":material/download_for_offline:",
        )

    with up2:
        uploaded_file = st.file_uploader("Upload Completed Addresses", type=["xlsx"])
        if uploaded_file is not None:
            uploaded_df = pd.read_excel(uploaded_file)
            st.write(uploaded_df)
            response = (
                st.session_state.supabase.table("book_orders")
                .upsert(uploaded_df)
                .execute()
            )
            st.success("Addresses uploaded successfully!")
            st.write(response)
            st.write(response["data"])
