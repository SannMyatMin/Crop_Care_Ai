import streamlit as st
import json

def load_shops():
    try:
        # JSON file လမ်းကြောင်းကို သေချာစစ်ဆေးပါ (shops.json သို့မဟုတ် data/shops.json)
        with open("shops.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Shops.json file ကို ရှာမတွေ့ပါ။")
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

def app():
    st.title("🛒 Marketplace (ဆေးအရောင်းဆိုင်များ)")
    st.markdown("မိမိတို့လိုအပ်သော စိုက်ပျိုးရေးသုံးဆေးဝါးများကို အောက်ပါဆိုင်များတွင် ဝယ်ယူနိုင်ပါသည်။")
    st.write("---")

    shops = load_shops()

    if not shops:
        st.warning("လက်ရှိတွင် ပြသရန် ဆိုင်အချက်အလက်များ မရှိသေးပါ။")
        return

    # ဆိုင်တစ်ဆိုင်ချင်းစီကို Loop ပတ်ပြီး ပြသခြင်း
    for shop in shops:
        # Expander သို့မဟုတ် Container သုံးပြီး ဆိုင်အချက်အလက်ကို ပြသခြင်း
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown("### 🏪") # ဆိုင် Icon
            
            with col2:
                st.subheader(shop['shop_name_mm'])
                
                # အချက်အလက်များကို အစက်လေးများ (Bullet points) နှင့် ပြခြင်း
                st.markdown(f"📍 **မြို့နယ်:** {shop['city']}")
                st.markdown(f"🏠 **လိပ်စာ:** {shop['address']}")
                st.markdown(f"📞 **ဖုန်းနံပါတ်:** `{shop['phone_number']}`")
                
                # ရောင်းချသော ပစ္စည်းများကို Badge ပုံစံမျိုး စာလုံးစောင်းလေးများဖြင့် ပြခြင်း
                items_str = " , ".join(shop['sold_items'])
                st.info(f"📦 **ရောင်းချသောပစ္စည်းများ:**\n\n{items_str}")
                
            st.write("---") # ဆိုင်တစ်ဆိုင်နှင့် တစ်ဆိုင်ကြား မျဉ်းတားခြင်း

# ဤနေရာတွင် logic အားလုံးကို app() function ထဲမှာ ထည့်ထားမှသာ app.py က ခေါ်သုံးနိုင်ပါမည်။