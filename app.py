import streamlit as st
from utils.styles import GLOBAL_CSS
from components import sidebar
from pages import search_order, data_browser, import_excel, export_excel, view_templates

st.set_page_config(page_title="Supply Chain", page_icon="📦", layout="wide", initial_sidebar_state="expanded")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

PAGES = {
    "search_order": search_order, "data_browser": data_browser,
    "import_excel": import_excel, "export_excel": export_excel,
    "view_templates": view_templates
}

page_key = sidebar.render()
PAGES[page_key].render()
