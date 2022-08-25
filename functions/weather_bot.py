from settings_app.API_token import open_weather_token, cases_token
import datetime
import requests


def get_weather(city, token=open_weather_token):
    code_to_smile = {
        'Ash': '\U0001F32B',
        'Clear': '\U00002600',
        'Clouds': '\U00002601',
        'Drizzle': '\U00002614',
        'Dust': '\U0001F32B',
        'Fog': '\U0001F32B',
        'Haze': '\U0001F32B',
        'Mist': '\U0001F32B',
        'Rain': '\U00002614',
        'Sand': '\U0001F32B',
        'Smoke': '\U0001F32B',
        'Snow': '\U0001F328',
        'Squall': '\U0001F32B',
        'Thunderstorm': '\U000026A1',
        'Tornado': '\U0001F32B'
    }
    try:
        req = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city.lower()}&appid={token}&units=metric&lang=ru"
        )
        result = req.json()

        try:
            headers = requests.utils.default_headers()
            headers.update({'User-Agent': 'My User Agent 1.0'})
            cases_req = requests.get(f"http://ws3.morpher.ru/russian/declension?s={city}"
                                     f"&token={cases_token}&format=json", headers=headers)
            cases = cases_req.json()
            city_name = cases["П"]
        except Exception:
            city_name = result["name"]
        temp = result["main"]["temp"]
        humidity = result["main"]["humidity"]
        lat = result["coord"]["lat"]
        lon = result["coord"]["lon"]
        sunrise = datetime.datetime.fromtimestamp(result["sys"]["sunrise"]).time()
        sunset = datetime.datetime.fromtimestamp(result["sys"]["sunset"]).time()
        weather = result["weather"][0]["main"]
        description = result["weather"][0]["description"]
        if weather in code_to_smile:
            weather = code_to_smile[weather]
        else:
            weather = None
        wind = result["wind"]["speed"]

        return city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset

    except Exception:
        raise Warning


def main():
    city = input("Введи город: ")
    city_name, temp, humidity, description, weather, wind, lat, lon, sunrise, sunset = get_weather(city)
    print(f"Прогноз погоды в {city_name}\n"
          f"Температура: {temp}︒C\n"
          f"Влажность: {humidity} %\n"
          f"Погода: {description} {weather}\n"
          f"Скорость ветра: {wind} м/с\n"
          f"Координаты города: {lat}, {lon}\n"
          f"Время рассвета: {sunrise}\n"
          f"Время заката: {sunset}"
          )


if __name__ == '__main__':
    main()
