
import requests

api_key = "f85efd938fa3d5894ffbc9af37cef8cb"

def weather_emoji(weather_id):
    if   200 <= weather_id <= 232: return "⛈️"
    elif 300 <= weather_id <= 321: return "🌦️"
    elif 500 <= weather_id <= 531: return "🌧️"
    elif 600 <= weather_id <= 622: return "🌨️"
    elif 701 <= weather_id <= 761: return "🌫️"
    elif weather_id == 771: return "🌬️"
    elif weather_id == 781: return "🌪️"
    elif weather_id == 800: return "☀️"
    elif 801 <= weather_id <= 804: return "☁️"
    else: return "🌤️"

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["cod"] == 200:
            return {
                "temperature" : data["main"]["temp"],
                "description" : data["weather"][0]["description"],
                "weather_emoji" : weather_emoji(data["weather"][0]["id"]),
                "humidity": data["main"]["humidity"],
                "wind_speed" : data["wind"]["speed"]
            }
    except requests.exceptions.HTTPError:
        return str(response.status_code)
    except requests.exceptions.ConnectionError:
        return str("Connection Error")
    except requests.exceptions.Timeout:
        return str("Timeout Error")
    except requests.exceptions.RequestException as e:
        return str(f"Request Error: {e}")