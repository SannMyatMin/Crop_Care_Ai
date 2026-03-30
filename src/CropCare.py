import streamlit as st
import pandas as pd
import os
import json
import sys
from PIL import Image
from datetime import datetime

# ---------------- 0. SYSTEM PATH SETUP ----------------
# Folder structure နက်နေပါက import ရှာတွေ့ရန်အတွက်
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from prediction_script import predict_paddy
except ImportError:
    # တကယ်လို့ src folder ထဲမှာ ရှိနေရင်
    from src.prediction_script import predict_paddy

# ---------------- 1. VARIETY MAPPING ----------------
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

# ---------------- 2. DATA LOADING FUNCTIONS ----------------
def load_knowledge():
    try:
        with open('knowledge.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Knowledge file load လုပ်ရာတွင် အခက်အခဲရှိပါသည်: {e}")
        return {}

def load_shops():
    try:
        with open('shops.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Shops file load လုပ်ရာတွင် အခက်အခဲရှိပါသည်: {e}")
        return []

def log_to_csv(city, disease_name_mm):
    if disease_name_mm == "ကျန်းမာသော စပါးပင်":
        return
        
    file_name = 'disease_data.csv'
    current_time = datetime.now()
    
    new_data = {
        "Date": current_time.strftime("%Y-%m-%d"),
        "Time": current_time.strftime("%H:%M:%S"),
        "City": city,
        "Disease": disease_name_mm
    }
    
    df_new = pd.DataFrame([new_data])
    
    if not os.path.isfile(file_name):
        df_new.to_csv(file_name, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(file_name, mode='a', index=False, header=False, encoding='utf-8-sig')

# ---------------- 3. MAIN APP ----------------
def main():
    knowledge_base = load_knowledge()
    shops_data = load_shops()

    st.set_page_config(page_title="Crop Care - Paddy Disease Detector", layout="wide")

    st.markdown("""
    <style>
        .main .block-container { max-width: 1100px; padding-top: 2rem; }
        .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #2e7d32; color: white; font-weight: bold; border: none; }
        .stButton>button:hover { background-color: #1b5e20; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌾 Crop Care (စပါးရောဂါ ရှာဖွေသူ)")
    st.markdown("စပါးရွက်ပုံရိပ်ကို အသုံးပြု၍ ရောဂါရှာဖွေခြင်းနှင့် ကုသနည်းလမ်းညွှန်များကို ကြည့်ရှုနိုင်ပါသည်။")
    st.write("---")

    # Sidebar သို့မဟုတ် အပေါ်တွင် မြို့ရွေးရန်
    selected_city = st.selectbox(
        "📍 မိမိတည်ရှိရာ မြို့နယ်ကို ရွေးချယ်ပါ:",
        options=["မန္တလေးမြို့", "ရန်ကုန်မြို့", "ညောင်တုန်းမြို့", "ပန်းတနော်မြို့"]
    )

    uploaded_file = st.file_uploader("📸 စပါးရွက်ပုံကို ရွေးချယ်ပါ...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1], gap="large")

        # Session state ကို သုံးပြီး ရလဒ်များကို သိမ်းထားခြင်း
        if 'last_result' not in st.session_state:
            st.session_state['last_result'] = None

        with col2:
            st.subheader("🔍 စစ်ဆေးမှု ရလဒ်")
            predict_btn = st.button("စစ်ဆေးမည် (Predict Now)")
            
            if predict_btn:
                with st.spinner('AI က ပုံကို စစ်ဆေးနေပါတယ်... ခဏစောင့်ပေးပါ'):
                    try:
                        result = predict_paddy(img)
                        # ရောဂါအမည်ကို key အဖြစ်ပြောင်းလဲခြင်း (ဥပမာ- "Blast" -> "blast")
                        disease_key = result["disease"].lower().replace(" ", "_")
                        
                        # Knowledge ထဲမှ ရှာဖွေခြင်း
                        disease_info = knowledge_base.get(disease_key, knowledge_base.get("normal"))
                        
                        # ရလဒ်များကို သိမ်းဆည်းခြင်း
                        st.session_state['last_result'] = {
                            "info": disease_info,
                            "age": result['age'],
                            "variety": result['variety']
                        }
                        
                        log_to_csv(selected_city, disease_info['name_mm'])
                        st.success("တွက်ချက်မှု အောင်မြင်ပါသည်။")
                        
                    except Exception as e:
                        st.error(f"Prediction Error: {e}")

            # ရလဒ်များကို ပြသခြင်း
            if st.session_state['last_result']:
                res = st.session_state['last_result']
                info = res['info']
                
                raw_variety = res['variety'].lower().strip()
                variety_mm = VARIETY_MAPPING.get(raw_variety, VARIETY_MAPPING["default"])

                st.markdown(f"### **{info['name_mm']}**")
                st.info(f"🌾 **မျိုးစိတ်:** {variety_mm} | 📅 **သက်တမ်း:** {res['age']} ရက်")
                
                st.markdown("#### 🔬 ဖြစ်ပွားရသည့် အကြောင်းရင်း")
                st.write(info['cause'])
                
                st.markdown("#### 💡 ကုသရန် အကြံပြုချက်")
                treatment_text = info['treatment']
                formatted_lines = [f"- {l.strip()}။" for l in treatment_text.split("။") if l.strip()]
                st.warning("\n\n".join(formatted_lines))

        with col1:
            st.subheader("🖼️ တင်ထားသော ပုံ")
            # use_container_width logic
            st.image(img, width=450)
            
            if st.session_state['last_result']:
                info = st.session_state['last_result']['info']
                st.write("---")
                
                # Chemical Key ကို အကြီးအသေး နှစ်မျိုးလုံး စစ်ဆေးခြင်း
                chem_list = info.get("chemical_treatment") or info.get("Chemical_treatment") or []
                
                if chem_list:
                    st.markdown("#### 🧪 အသုံးပြုနိုင်သော ဆေးများ")
                    clean_chems = [c.strip() for c in chem_list]
                    st.success("\n".join([f"- {c}" for c in clean_chems]))

                    # ဆိုင်များကို ရှာဖွေသည့် Logic (Smart Matching)
                    matched_shops = []
                    target_chems = [c.lower() for c in clean_chems]
                    
                    for shop in shops_data:
                        # မြို့အမည်နှင့် ဆေးအမည် တိုက်စစ်ခြင်း
                        shop_city = str(shop.get("city", "")).strip()
                        if shop_city == selected_city.strip():
                            shop_items = [str(item).strip().lower() for item in shop.get("sold_items", [])]
                            if any(target in shop_items for target in target_chems):
                                matched_shops.append(shop)

                    st.markdown(f"#### 🏪 {selected_city} ရှိ ဆေးဆိုင်များ")
                    if matched_shops:
                        for shop in matched_shops:
                            with st.expander(f"🏪 {shop['shop_name_mm']}"):
                                st.write(f"📍 **လိပ်စာ:** {shop['address']}")
                                st.write(f"📞 **ဖုန်း:** {shop['phone_number']}")
                    else:
                        st.warning(f"လက်ရှိတွင် {selected_city} ၌ အဆိုပါဆေးများ ရရှိနိုင်မည့်ဆိုင် မတွေ့ရှိသေးပါ။")
    else:
        st.info("စစ်ဆေးလိုသော စပါးရွက်ပုံကို Upload တင်ပေးပါ။")
        st.session_state['last_result'] = None

if __name__ == "__main__":
    main()