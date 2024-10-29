from flask_cors import CORS;
from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

apiKey = "dd94f859a0e52d6e4767fddf735f04a7"

# Function to fetch weather data from API
def search_weather(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=Metric&appid={apiKey}'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Function to update summary text based on weather data
def update_summary(data):
    physiography = ''
    rainfall = ''
    temperatureAndAltitude = ''
    relativeHumidity = ''
    wind = ''

    current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)  # Sri Lanka time

    sea_level = data.get('main', {}).get('sea_level', 0)
    weather_main = data['weather'][0]['main']
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']

    # Physiography summary based on sea level
    if sea_level < 500:
        physiography = (
            "Most of the world's commercially grown rubber occurs within 10° of the equator at altitudes of less than 500m. The Sri Lanka rubber plantations lie within 7° of the equator and are situated between 80°.09' and 81°.04' E longitudes and 6°.50' and 7°.38' N latitudes. Your rubber field is within the ideal sea level."
        )
    else:
        physiography = "The sea level is higher than the optimal range for rubber plantations. Consider lower altitudes for better suitability."

    # Rainfall summary
    if weather_main == 'Rain':
        if current_time.hour >= 17:
            rainfall = (
                "The ideal annual rainfall for rubber should fall within the range of 1650mm - 3000mm. High rainfall can favor foliage and panel diseases. Rainfall in the late evening and ceases before 03:00 hours to allow for optimal tapping conditions."
            )
        else:
            rainfall = "The ideal annual rainfall for rubber should fall within the range of 1650mm - 3000mm. High rainfall can favor foliage and panel diseases."
    else:
        rainfall = "Current conditions indicate no rain. Optimal rubber production requires careful attention to rainfall patterns. Also, low rainfall can depress growth and yield."

    # Temperature summary
    if 23 <= temperature <= 28:
        temperatureAndAltitude = "The temperature is within the ideal range for rubber tree growth."
    elif temperature < 23:
        temperatureAndAltitude = "Lower temperatures can increase the risk of diseases such as phytophthora secondary leaf fall and oidium leaf disease."
    elif temperature > 28:
        temperatureAndAltitude = "The temperature is quite high for rubber fields. High temperatures, especially above 30°C, can adversely affect tree performance by increasing evapotranspiration."

    # Humidity summary
    if 80 <= humidity <= 100:
        relativeHumidity = "The relative humidity is within the ideal range for rubber production, favoring crop growth and reducing evapotranspiration."
    if humidity > 100:
        relativeHumidity = "High relative humidity can promote crop growth but also increase the incidence of diseases."
    else:
        relativeHumidity = "Low humidity is not good for the rubber tree."

    # Wind summary
    if wind_speed > 75:
        wind = "The wind speed is high, which could cause severe damage to rubber trees, especially those with dense canopies of moisture-laden foliage."
    else:
        wind = "The wind speed is within a safe range for rubber trees."

    summary_text = (
        f"Physiography: {physiography}\n\n"
        f"Rainfall: {rainfall}\n\n"
        f"Temperature and Altitude: {temperatureAndAltitude}\n\n"
        f"Relative Humidity: {relativeHumidity}\n\n"
        f"Wind: {wind}"
    )

    return summary_text

@app.route('/', methods=['POST'])
def home():
    summary_text = ''
    try:
        # Extract JSON data from the request
        data = request.get_json()
        city = data.get('city')

        # If city is provided, fetch weather data
        if city:
            weather_data = search_weather(city)
            if weather_data:
                summary_text = update_summary(weather_data)
            return jsonify({"summary": summary_text}), 200
        else:
            return jsonify({"error": "City not provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

