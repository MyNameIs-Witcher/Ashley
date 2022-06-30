from weather_bot import get_weather
from API_token import open_weather_token

def main():
    city = input("Input sity: ")
    get_weather(city, open_weather_token)

if __name__ == '__main__':
    main()
