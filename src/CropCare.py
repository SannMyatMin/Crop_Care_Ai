import streamlit as st
import pandas as pd # CSV handling အတွက်
import os
from PIL import Image
from datetime import datetime
from prediction_script import predict_paddy

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

# ---------------- FUNCTIONS ----------------
def load_knowledge():
    import json
    try:
        with open('knowledge.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_shops():
    import json
    try:
        with open('shops.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# NEW FEATURE: Save every prediction to CSV
def log_to_csv(city, disease_name_mm):
    if disease_name_mm == "ကျန်းမာသော စပါးပင်":
        return
        
    file_name = 'disease_data.csv'
    current_time = datetime.now()
    
    # သိမ်းဆည်းမည့် data row
    new_data = {
        "Date": current_time.strftime("%Y-%m-%d"),
        "Time": current_time.strftime("%H:%M:%S"),
        "City": city,
        "Disease": disease_name_mm
    }
    
    df_new = pd.DataFrame([new_data])
    
    # File မရှိသေးရင် Header နဲ့ အသစ်ဆောက်မယ်၊ ရှိပြီးသားဆိုရင် အောက်ကနေ row အသစ်ဆင့်မယ်
    if not os.path.isfile(file_name):
        df_new.to_csv(file_name, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(file_name, mode='a', index=False, header=False, encoding='utf-8-sig')

# ---------------- MAIN APP FUNCTION ----------------
def app():
    knowledge_base = load_knowledge()
    shops_data = load_shops()

    st.markdown("""
    <style>
        .main .block-container { max-width: 1000px; padding-top: 2rem; padding-bottom: 2rem; }
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌾 Crop Care (စပါးရောဂါ ရှာဖွေသူ)")
    st.markdown("အောက်ပါနေရာတွင် စပါးရွက်ပုံရိပ်ကို တင်၍ ရောဂါလက္ခဏာများကို စစ်ဆေးနိုင်ပါသည်။")
    st.write("---")

    selected_city = st.selectbox(
        "မိမိတည်ရှိရာ မြို့နယ်ကို ရွေးချယ်ပါ:",
        options=["မန္တလေးမြို့", "ရန်ကုန်မြို့", "ညောင်တုန်းမြို့", "ပန်းတနော်မြို့"]
    )

    uploaded_file = st.file_uploader("စပါးရွက်ပုံကို ရွေးချယ်ပါ (JPG, PNG)...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1], gap="large")

        result_data = None
        disease_info = None

        with col2:
            st.subheader("🔍 စစ်ဆေးမှု ရလဒ်")
            predict_btn = st.button("စစ်ဆေးမည် (Predict)")
            
            if predict_btn:
                with st.spinner('ခဏစောင့်ပေးပါ... Model က တွက်ချက်နေပါတယ်'):
                    try:
                        result_data = predict_paddy(img)
                        raw_disease = result_data["disease"].lower().replace(" ", "_")
                        disease_info = knowledge_base.get(raw_disease, knowledge_base.get("normal"))
                        
                        # CSV ထဲသို့ Data ပေါင်းထည့်ခြင်း
                        log_to_csv(selected_city, disease_info['name_mm'])

                        raw_variety = result_data["variety"].lower().strip()
                        variety_mm = VARIETY_MAPPING.get(raw_variety, VARIETY_MAPPING["default"])

                        st.success("တွက်ချက်မှု ပြီးစီးပါပြီ!")
                        st.markdown(f"### **{disease_info['name_mm']}**")
                        st.info(f"🌾 **မျိုးစိတ်:** {variety_mm} | 📅 **သက်တမ်း:** {result_data['age']} ရက်")
                        st.write("---")
                        st.markdown("#### 🔬 ဖြစ်ပွားရသည့် အကြောင်းရင်း")
                        st.write(disease_info['cause'])
                        st.markdown("#### 💡 အကြံပြုချက်")
                        treatment_text = disease_info['treatment']
                        lines = treatment_text.split("။")
                        formatted_lines = [f"- {line.strip()}။" for line in lines if line.strip()]
                        st.warning("\n\n".join(formatted_lines))
                    except Exception as e:
                        st.error(f"Error တက်သွားပါသည် - {e}")
            else:
                st.info("ရလဒ်ကို ကြည့်ရှုရန် 'စစ်ဆေးမည်' ခလုတ်ကို နှိပ်ပါ။")

        with col1:
            st.subheader("🖼️ တင်ထားသော ပုံ")
            st.image(img, use_container_width=True)
            
            if disease_info:
                st.write("---")
                chemical_list = disease_info.get("chemical_treatment", [])
                if chemical_list:
                    st.markdown("#### 🧪 အသုံးပြုနိုင်သော ဆေးများ")
                    bullet_chemicals = "\n".join([f"- {chem}" for chem in chemical_list])
                    st.success(bullet_chemicals)

                    matched_shops = [
                        shop for shop in shops_data 
                        if shop.get("city") == selected_city and 
                        any(item in shop.get("sold_items", []) for item in chemical_list)
                    ]

                    st.markdown(f"#### 🏪 {selected_city} တွင် ဝယ်ယူနိုင်သော ဆိုင်များ")
                    if matched_shops:
                        for shop in matched_shops:
                            st.info(f"🏪 **{shop['shop_name_mm']}**\n\n📍 {shop['address']}\n\n📞 {shop['phone_number']}")
                    else:
                        st.warning(f"{selected_city} တွင် အဆိုပါဆေးများ ရောင်းချသောဆိုင် မတွေ့ရှိပါ။")
    else:
        st.info("ကျေးဇူးပြု၍ စစ်ဆေးလိုသော စပါးရွက်ပုံကို အပေါ်တွင် Upload တင်ပေးပါ။")