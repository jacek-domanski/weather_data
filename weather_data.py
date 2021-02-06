import requests
from datetime import datetime, timedelta

if __name__ == '__main__':
    now = datetime.now()
    print(now.timestamp())

    call = http://api.openweathermap.org/data/2.5/onecall/timemachine?lat=60.99&lon=30.9&dt=1586468027&appid={API key}