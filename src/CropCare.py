import streamlit as st
import pandas as pd
import os
import json
import sys
from PIL import Image
from datetime import datetime

# ---------------- 1. SETUP PATHS ----------------
# လက်ရှိ file (app.py) ရှိတဲ့ folder ကို base အဖြစ်ယူမယ်
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

# prediction_script ကို import လုပ်ခြင်း
sys.path.append(BASE_DIR)
try:
    from prediction_script import predict_paddy
except ImportError:
    st.error("prediction_script.py ကို ရှာမတွေ့ပါ။ ဖိုင်တည်နေရာကို ပြန်စစ်ပေးပါ။")

# ---------------- 2. VARIETY MAPPING ----------------
VARIETY_MAPPING = {
    "adt45": "အေဒီတီ-၄၅ (ADT 45)",
    "irland": "အိုင်ယာလန် (Irland)",
    "onthan": "အုန်းသန့် (Onthan)",
    "pusa": "ပူဆာ (Pusa)",
    "ipt": "အိုင်ပီတီ (IPT)",
    "at307": "အေတီ-၃၀၇ (AT 307)",
    "at354": "အေတီ-၃၅၄ (AT 354)",
    "at362": "အေတီ-၃၆၂ (AT 362)",
    "at401": "အေတီ-၄၀၁ (AT 401)",
    "at308": "အေတီ-၃၀၈ (AT 308)",
    "default": "အထွေထွေ စပါးမျိုး"
}

# ---------------- 3. LOAD DATA ----------------
def load_knowledge():
    path = get_path('knowledge.json')
    if not os.path.exists(path):
        st.error(f"ဖိုင်မတွေ့ပါ: {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_shops():
    path = get_path('shops.json')
    if not os.path.exists(path):
        st.error(f"ဖိုင်မတွေ့ပါ: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ---------------- 4. MAIN APP ----------------
def main():
    knowledge_base = load_knowledge()
    shops_data = load_shops()

    st.set_page_config(page_title="Crop Care", layout="wide")
    
    st.title("🌾 Crop Care (စပါးရောဂါ ရှာဖွေသူ)")
    st.write("---")

    selected_city = st.selectbox(
        "📍 မိမိတည်ရှိရာ မြို့နယ်ကို ရွေးချယ်ပါ:",
        options=["မန္တလေးမြို့", "ရန်ကုန်မြို့", "ညောင်တုန်းမြို့", "ပန်းတနော်မြို့"]
    )

    uploaded_file = st.file_uploader("📸 စပါးရွက်ပုံကို ရွေးချယ်ပါ...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1], gap="large")

        # Predict လုပ်ပြီးသား result ကို ခေတ္တသိမ်းထားရန်
        if 'last_res' not in st.session_state:
            st.session_state.last_res = None

        with col2:
            st.subheader("🔍 စစ်ဆေးမှု ရလဒ်")
            if st.button("စစ်ဆေးမည် (Predict)"):
                with st.spinner('ခဏစောင့်ပေးပါ...'):
                    try:
                        res = predict_paddy(img)
                        d_key = res["disease"].lower().replace(" ", "_")
                        d_info = knowledge_base.get(d_key, knowledge_base.get("normal"))
                        
                        st.session_state.last_res = {
                            "info": d_info,
                            "age": res['age'],
                            "variety": res['variety']
                        }
                    except Exception as e:
                        st.error(f"Error: {e}")

            # ရလဒ်များကို ပြသခြင်း
            if st.session_state.last_res:
                info = st.session_state.last_res['info']
                v_mm = VARIETY_MAPPING.get(st.session_state.last_res['variety'].lower().strip(), VARIETY_MAPPING["default"])

                st.markdown(f"### **{info['name_mm']}**")
                st.info(f"🌾 **မျိုးစိတ်:** {v_mm} | 📅 **သက်တမ်း:** {st.session_state.last_res['age']} ရက်")
                st.write(f"**အကြောင်းရင်း:** {info['cause']}")
                
                st.warning(f"**အကြံပြုချက်:** \n\n {info['treatment']}")

        with col1:
            st.subheader("🖼️ တင်ထားသော ပုံ")
            st.image(img, use_container_width=True)
            
            if st.session_state.last_res:
                info = st.session_state.last_res['info']
                # Case-insensitive check for chemical key
                chem_list = info.get("chemical_treatment") or info.get("Chemical_treatment") or []
                
                if chem_list:
                    st.write("---")
                    st.markdown("#### 🧪 အသုံးပြုနိုင်သော ဆေးများ")
                    st.success(", ".join(chem_list))

                    # --- SHOP MATCHING LOGIC ---
                    matched_shops = []
                    target_chems = [c.strip().lower() for c in chem_list]
                    
                    for shop in shops_data:
                        # မြို့အမည် တူမတူစစ် (Space ဖယ်ပြီးစစ်)
                        if str(shop.get("city", "")).strip() == selected_city.strip():
                            shop_items = [str(i).strip().lower() for i in shop.get("sold_items", [])]
                            # ဆေးတစ်မျိုးမျိုး ကိုက်ညီရင် ဆိုင်စာရင်းထဲထည့်
                            if any(tc in shop_items for tc in target_chems):
                                matched_shops.append(shop)

                    st.markdown(f"#### 🏪 {selected_city} ရှိ ဆေးဆိုင်များ")
                    if matched_shops:
                        for s in matched_shops:
                            with st.expander(f"🏪 {s['shop_name_mm']}"):
                                st.write(f"📍 {s['address']}")
                                st.write(f"📞 {s['phone_number']}")
                    else:
                        st.warning(f"{selected_city} တွင် ဤရောဂါအတွက် ဆေးရနိုင်သောဆိုင် မတွေ့သေးပါ။")

    else:
        st.session_state.last_res = None
        st.info("ကျေးဇူးပြု၍ ပုံတင်ပေးပါ။")

if __name__ == "__main__":
    main()