import os
import sys
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_path)

import streamlit as st
from streamlit_option_menu import option_menu

# Folder နာမည် 'src' သို့ ပြောင်းထားသည်ဟု ယူဆပါသည်
import src.home as home
import src.CropCare as CropCare
import src.marketplace as marketplace
import src.news as news

# Page Config (Main တစ်ခုတည်းမှာပဲ ရှိရပါမယ်)
st.set_page_config(page_title="AgriSense AI", layout="wide", page_icon="🌾")

# ---------------- SIDEBAR STYLE ----------------
st.markdown("""
<style>
section[data-testid="stSidebar"] { width: 220px !important; }
.sidebar-title { font-size: 22px !important; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR MENU ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌾 AgriSense AI</div>', unsafe_allow_html=True)
    
    main_menu = option_menu(
        menu_title=None,
        options=["Home", "CropCare", "Marketplace", "News"],
        icons=["house", "leaf", "shop", "newspaper"],
        menu_icon="cast",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#2e7d32"},
        }
    )

# ---------------- PAGE ROUTING ----------------
if main_menu == "Home":
    home.app()
elif main_menu == "CropCare":
    CropCare.app()
elif main_menu == "Marketplace":
    marketplace.app()
elif main_menu == "News":
    news.app()