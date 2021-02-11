import requests
from datetime import datetime, timedelta
from sheet_editor import SheetEditor
from setup import logger_setup
logger = logger_setup(__name__)

class WeatherData:
    def __init__(self):
        self.api_key = open('weather_api_key.txt', 'r').read()
        self.sheet_editor = SheetEditor()

    def run(self):
        logger.info('Running')
        region_name = 'Krakow'
        lon = 19.937222
        lat = 50.061389
        time = datetime.now() - timedelta(days=1)
        region_weather = self.get_weather_for_region(lon, lat, time)
        temp_avgs = self.parse_weather(region_weather)
        self.sheet_editor.add_day_avgs_for_region(region_name, time, temp_avgs)


    def get_weather_for_region(self, lon, lat, time):
        units = 'metric'
        call = f'https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&units={units}&dt={int(time.timestamp())}&appid={self.api_key}'

        logger.info(f'Call: {call}')
        response_raw = requests.get(call)
        response_dict = dict(response_raw.json())
        logger.info(f'Response dict: {response_dict}')
        return response_dict

    def parse_weather(self, weather_dict):
        sunrise_time = datetime.fromtimestamp(weather_dict['current']['sunrise'])
        sunset_time = datetime.fromtimestamp(weather_dict['current']['sunset'])
        logger.info(f'Sunrise: {sunrise_time}, Sunset: {sunset_time}')
        data = {'night_temps': [], 'day_temps': [], 'night_feels': [], 'day_feels': []}

        for hour in weather_dict['hourly']:
            time = datetime.fromtimestamp(hour['dt'])
            temp = hour['temp']
            feels_like = hour['feels_like']
            if sunrise_time < time < sunset_time:
                data['day_temps'].append(temp)
                data['day_feels'].append(feels_like)
            else:
                data['night_temps'].append(temp)
                data['night_feels'].append(feels_like)

        day_avg = self.average_of_list(data["day_temps"])
        night_avg = self.average_of_list(data["night_temps"])
        day_night_avg = self.average_of_list(data["day_temps"] + data["night_temps"])
        logger.info(f'Day avg: {day_avg}')
        logger.info(f'Night avg: {night_avg}')
        logger.info(f'24h avg: {day_night_avg}')

        return day_avg, night_avg, day_night_avg

    def average_of_list(self, lst):
        return sum(lst) / len(lst)


if __name__ == '__main__':
    wd = WeatherData()
    wd.run()
