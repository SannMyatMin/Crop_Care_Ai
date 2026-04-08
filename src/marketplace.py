import streamlit as st
import json

def load_shops():
    try:
        
        with open("shops.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Shops.json file ကို ရှာမတွေ့ပါ။")
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def app():
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

    st.title("🛒 Marketplace (ဆေးအရောင်းဆိုင်များ)")
    st.markdown("မိမိတို့လိုအပ်သော စိုက်ပျိုးရေးသုံးဆေးဝါးများကို အောက်ပါဆိုင်များတွင် ဝယ်ယူနိုင်ပါသည်။")
    st.write("---")

    shops = load_shops()

    if not shops:
        st.warning("လက်ရှိတွင် ပြသရန် ဆိုင်အချက်အလက်များ မရှိသေးပါ။")
        return

    
    for shop in shops:
        
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown("### 🏪")
            
            with col2:
                st.subheader(shop['shop_name_mm'])
                
                st.markdown(f"📍 **မြို့နယ်:** {shop['city']}")
                st.markdown(f"🏠 **လိပ်စာ:** {shop['address']}")
                st.markdown(f"📞 **ဖုန်းနံပါတ်:** `{shop['phone_number']}`")
                
                items_str = " , ".join(shop['sold_items'])
                st.info(f"📦 **ရောင်းချသောပစ္စည်းများ:**\n\n{items_str}")
                
            st.write("---")