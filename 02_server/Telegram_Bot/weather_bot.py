from API_token import open_weather_token
from pprint import pprint
import datetime
import requests

def get_weather(city, open_weather_token):

    code_to_smile = {
        "Clear" : "Ясно \U00002600",
        "Clouds" : "Облачно \U00002601",
        "Rain" : "Дождь \U00002614",
        "Drizzle" : "Дождь \U00002614",
        "Thunderstorm" : "Гроза \U000026A1",
        "Snow" : "Снег \U0001F328",
        "Mist" : "Туман \U0001F32B"
    }

    try:
        req = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric&lang=ru'
        )
        result = req.json()
        #pprint(result)

        city_name = result["name"]
        temp = result["main"]["temp"]
        humidity = result["main"]["humidity"]
        lat = result["coord"]["lat"]
        lon = result["coord"]["lon"]
        sunrise = datetime.datetime.fromtimestamp(result["sys"]["sunrise"]).time()
        sunset = datetime.datetime.fromtimestamp(result["sys"]["sunset"]).time()
        weather = result["weather"][0]["main"]
        if weather in code_to_smile:
            weather = code_to_smile[weather]
        else:
            weather = "Посмотри в окно, я не понимаю, что там происходит"
        wind = result["wind"]["speed"]

        print(f"\tПрогноз погоды в {city_name}е\n"
              f"\tТемпература: {temp}︒C\n"
              f"\tВлажность: {humidity} мм.рт.ст.\n"
              f"\tПогода: {weather}\n"
              f"\tСкорость ветра: {wind} м/с\n"
              f"\tКоординаты города: {lat}, {lon}\n"
              f"\tВремя рассвета: {sunrise}\n"
              f"\tВремя заката: {sunset}"
              )

    except Exception as ex:
        print(ex)
        print("Wrong name of city!")

def main():
    city = input("Input sity: ")
    get_weather(city, open_weather_token)

if __name__ == '__main__':
    main()
