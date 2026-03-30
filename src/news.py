import streamlit as st
import pandas as pd
import plotly.express as px
import os
from weather import get_weather

# ---------------- 1. WEATHER TRANSLATION WITH LARGE EMOJIS ----------------
def translate_weather(description):
    # Emoji ကို size ကြီးအောင် span tag ဖြင့် ထည့်ထားခြင်း
    weather_dict = {
        "clear sky": "<span style='font-size: 45px;'>☀️</span> သာယာသော မိုးကောင်းကင်",
        "few clouds": "<span style='font-size: 45px;'>🌤️</span> တိမ်အနည်းငယ်ရှိသည်",
        "scattered clouds": "<span style='font-size: 45px;'>☁️</span> တိမ်အသင့်အတင့်ရှိသည်",
        "broken clouds": "<span style='font-size: 45px;'>☁️</span> တိမ်ထူထပ်နေသည်",
        "shower rain": "<span style='font-size: 45px;'>🌦️</span> မိုးဖွဲဖွဲရွာနေသည်",
        "rain": "<span style='font-size: 45px;'>🌧️</span> မိုးရွာနေသည်",
        "thunderstorm": "<span style='font-size: 45px;'>⛈️</span> မိုးသက်မုန်တိုင်းဖြစ်နေသည်",
        "snow": "<span style='font-size: 45px;'>❄️</span> နှင်းကျနေသည်",
        "mist": "<span style='font-size: 45px;'>🌫️</span> မြူများဆိုင်းနေသည်",
        "overcast clouds": "<span style='font-size: 45px;'>☁️</span> တိမ်များအလွန်ထူထပ်နေသည်",
        "light rain": "<span style='font-size: 45px;'>🌦️</span> မိုးဖွဲဖွဲရွာနေသည်",
        "moderate rain": "<span style='font-size: 45px;'>🌧️</span> မိုးအသင့်အတင့်ရွာနေသည်",
        "heavy intensity rain": "<span style='font-size: 45px;'>🌧️</span> မိုးသည်းထန်စွာရွာနေသည်"
    }
    return weather_dict.get(description.lower(), description)

def app():
    st.title("📊 Agri Dashboard & News")
    st.write("---")

    # ---------------- 2. WEATHER SECTION ----------------
    st.subheader("🌦️ လက်ရှိ မိုးလေဝသ အခြေအနေ")
    
    all_cities = ["Yangon", "Mandalay", "Naypyidaw", "Bago", "Pathein", "Monywa", "Taunggyi", "Sittwe", "Myitkyina", "Pyay", "Hpa-An"]
    
    selected_weather_city = st.selectbox("မိုးလေဝသကြည့်လိုသည့် မြို့ကိုရွေးပါ:", options=all_cities)
    
    weather_data = get_weather(selected_weather_city)

    if isinstance(weather_data, dict):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="အပူချိန်", value=f"{weather_data['temperature']}°C", delta=weather_data['weather_emoji'])
        with col2:
            st.metric(label="စိုထိုင်းဆ", value=f"{weather_data['humidity']}%")
        with col3:
            st.metric(label="လေတိုက်နှုန်း", value=f"{weather_data['wind_speed']} m/s")
        with col4:
            # ကျန်တဲ့ metric label တွေနဲ့ အမြင့်ညီအောင် div တစ်ခုထဲမှာ ထည့်သွင်းခြင်း
            mm_description = translate_weather(weather_data['description'])
            
            st.markdown(f"""
                <div style='display: flex;'>
                    <p style='margin: 0; font-weight: bold; color: rgba(250, 250, 250, 0.6); font-size: 14px;'>လက်ရှိအခြေအနေ</p>
                    <div style='display: flex; align-items: center; gap: 5px; padding-top: 7px;'>
                        {mm_description}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        if "rain" in weather_data['description'].lower():
            st.warning("🌧️ မိုးရွာရန် အလားအလာရှိသဖြင့် ပိုးသတ်ဆေးဖျန်းခြင်းကို ခေတ္တဆိုင်းငံ့ထားပါ။")
        elif weather_data['temperature'] > 35:
            st.error("🔥 အပူချိန်လွန်ကဲနေသဖြင့် အပင်များ ရေငတ်ခြင်းမှ ကာကွယ်ရန် ရေသွင်းခြင်းကို ဂရုစိုက်ပါ။")
    else:
        st.error(f"ရာသီဥတု အချက်အလက် ယူ၍မရပါ - {weather_data}")

    st.write("---")

    # ---------------- 3. DISEASE DASHBOARD SECTION ----------------
    st.subheader("📈 ရောဂါကျရောက်မှု အချက်အလက်များ (Analytics)")

    csv_path = 'disease_data.csv'

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date'])
                df['Month'] = df['Date'].dt.strftime('%B %Y')

                dash_col1, dash_col2 = st.columns(2)
                
                with dash_col1:
                    dashboard_cities = df['City'].unique().tolist()
                    selected_dash_city = st.selectbox("မြို့နယ်ကိုရွေးချယ်ပါ:", options=dashboard_cities)
                
                with dash_col2:
                    city_df = df[df['City'] == selected_dash_city]
                    available_months = city_df['Month'].unique().tolist()
                    selected_month = st.selectbox("လကိုရွေးချယ်ပါ:", options=available_months)
                
                final_df = city_df[city_df['Month'] == selected_month]

                if not final_df.empty:
                    chart_data = final_df['Disease'].value_counts().reset_index()
                    chart_data.columns = ['Disease', 'Count']

                    fig = px.bar(
                        chart_data, 
                        x='Disease', 
                        y='Count',
                        title=f"{selected_dash_city} မြို့၏ {selected_month} လအတွင်း ရောဂါဖြစ်ပွားမှု",
                        labels={'Disease': 'ရောဂါအမည်', 'Count': 'အကြိမ်အရေအတွက်'},
                        color='Disease',
                        text_auto=False, 
                        template="plotly_dark"
                    )
                    
                    fig.update_yaxes(
                        showticklabels=False, 
                        title_text="အကြိမ်အရေအတွက်", 
                        visible=True
                    )
                    
                    fig.update_layout(
                        showlegend=False, 
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("ရွေးချယ်ထားသော လအတွက် အချက်အလက်မရှိပါ။")
            else:
                st.warning("CSV ဖိုင်အတွင်း အချက်အလက်များ မရှိသေးပါ။")
        except Exception as e:
            st.error(f"Data ဖတ်ရာတွင် အမှားအယွင်းရှိနေပါသည် - {e}")
    else:
        st.info("📊 စာရင်းအချက်အလက်များ ပြသရန် Prediction Data (CSV) လိုအပ်နေပါသေးသည်။ စပါးရောဂါအရင် စစ်ဆေးပေးပါ။")

    st.write("---")
    st.markdown("### 📢 စိုက်ပျိုးရေးဆိုင်ရာ အကြံပြုချက်များ")
    st.write("- ရေသွင်းရေထုတ် စနစ်တကျ ပြုလုပ်ပါ။")
    st.write("- မျိုးစေ့ကို စနစ်တကျ ရွေးချယ်ပါ။")