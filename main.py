import os
import requests

# 台北市座標
LATITUDE = 25.0330
LONGITUDE = 121.5654


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "Asia/Taipei",
        "forecast_days": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    max_temp = data["daily"]["temperature_2m_max"][0]
    rain_probability = data["daily"]["precipitation_probability_max"][0]

    return max_temp, rain_probability


def get_aqi():
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "us_aqi",
        "timezone": "Asia/Taipei",
        "forecast_days": 1
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    values = [x for x in data["hourly"]["us_aqi"] if x is not None]
    return max(values)


def create_advice(temp, rain, aqi):
    advice = []

    if rain >= 60:
        advice.append("☔ 降雨機率達 60%，記得攜帶雨傘。")

    if temp >= 33:
        advice.append("☀️ 最高溫度達 33°C，記得防曬與補充水分。")

    if aqi >= 100:
        advice.append("😷 AQI 達 100，建議配戴口罩。")

    if not advice:
        advice.append("✅ 今日天氣與空氣品質正常，適合外出通勤。")

    return "\n".join(advice)


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        data={"chat_id": chat_id, "text": message},
        timeout=10
    )
    response.raise_for_status()


def main():
    try:
        temp, rain = get_weather()
        aqi = get_aqi()

        advice = create_advice(temp, rain, aqi)

        message = (
            "🚇 智慧通勤風險通知\n\n"
            f"🌡️ 今日最高溫度：{temp}°C\n"
            f"🌧️ 今日最高降雨機率：{rain}%\n"
            f"🌫️ 今日最高 AQI：{aqi}\n\n"
            f"📢 通勤建議：\n{advice}"
        )

        print(message)
        send_telegram(message)

    except requests.RequestException as e:
        print(f"API 或網路連線發生錯誤：{e}")
        raise
    except Exception as e:
        print(f"程式執行發生錯誤：{e}")
        raise


if __name__ == "__main__":
    main()
