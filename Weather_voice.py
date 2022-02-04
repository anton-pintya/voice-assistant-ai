import re
import requests
import geocoder
from pymorphy2 import MorphAnalyzer
from datetime import datetime, timedelta
from natasha import AddrExtractor, MorphVocab

from VoiceProcessor import VoiceProcessor


class WeatherAPI(VoiceProcessor):
    def __init__(self, question, memory):
        self.appid = '20545223db0fbe4578aff195fb69bb8a'
        self.now_date = datetime.now()
        self.req_date = None
        self.is_city = None
        self.city = None
        self.day = None
        self.question = question

        self.voice = VoiceProcessor()
        self.memory = memory

    def get_city(self):
        morph = MorphVocab()
        city_extractor = AddrExtractor(morph)

        self.is_city = False
        cities = []

        for match in city_extractor(self.question):
            cities.append(match.fact.value)

        if len(cities) != 0:
            morph = MorphAnalyzer()
            self.city = morph.parse(cities[0])[0].normal_form
            del morph
        else:
            if self.memory.storage[-1] == 'weather' and self.memory.weather['city'] is not None:
                self.city = self.memory.weather['city']
                self.is_city = False
            else:
                self.city = geocoder.ip('me').city
                self.is_city = True
        return self.city, self.is_city

    def get_day(self):
        tokens = self.question.split(' ')

        week = {
            'Monday': 'понедельник',
            'Tuesday': 'вторник',
            'Wednesday': 'среда',
            'Thursday': 'четверг',
            'Friday': 'пятница',
            'Saturday': 'суббота',
            'Sunday': 'воскресенье',
        }

        next_day = bool('завтра' in tokens)
        today = bool('сегодня' in tokens)

        if today:
            self.day = datetime.now().date()
            return self.day
        elif next_day:
            self.day = datetime.now().date() + timedelta(days=1)
            return self.day
        else:
            regex = re.compile(r'понедельник\w*|вторник\w*|сред\w*|четверг\w*|пятниц\w*|суббот\w*|воскресень\w*')
            try:
                weekday = re.search(regex, self.question).group(0)
                morph = MorphAnalyzer()
                weekday = morph.parse(weekday)[0].normal_form
                del morph
            except:
                weekday = self.memory.weather['day']

            try:
                weekday = list(week.keys())[list(week.values()).index(weekday)]
                now_date = datetime.now()
                week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                days_dif = week_days.index(weekday) - week_days.index(now_date.strftime('%A'))

                if 0 < days_dif < 5:
                    self.req_date = (now_date + timedelta(days=abs(days_dif))).date()
                    self.day = self.req_date
                elif days_dif + 7 > 5:
                    self.day = None
                else:
                    self.req_date = (now_date + timedelta(days=days_dif + 7)).date()
                    self.day = self.req_date
                return self.day
            except:
                self.day = self.memory.weather['day']
                return self.day

    def get_current(self):
        res = requests.get("http://api.openweathermap.org/data/2.5/weather", params={
            'q': self.city,
            'units': 'metric',
            'lang': 'ru',
            'APPID': self.appid
        })
        data = res.json()
        conditions = []

        for i in range(len(data['weather'])):
            conditions.append(data['weather'][i]['description'])

        if not self.is_city:
            self.voice.say(f"В городе {self.city.capitalize()} сейчас {', '.join(conditions)}")
        else:
            self.voice.say(f"За окном сейчас {data['weather'][0]['description']}")

        self.voice.say(f"Средняя температура: {data['main']['temp']}\n"
              f"Ощущается как: {data['main']['feels_like']}")

    def get_forecast_time(self):
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={
            'q': self.city,
            'units': 'metric',
            'lang': 'ru',
            'APPID': self.appid
        })

        data = res.json()
        form = '%Y-%m-%d %H:%M:%S'

        for info in data['list']:
            if datetime.strptime(info['dt_txt'], form).day - self.now_date.day == 1:
                delta_hours = datetime.strptime(info['dt_txt'], form).hour - self.now_date.hour
                if 0 <= abs(delta_hours) < 3:
                    self.voice.say(f'Завтра в {datetime.strptime(info["dt_txt"], form).time()} в городе {self.city.capitalize()}:\n'
                          f'Температура: {info["main"]["temp"]}\t{info["weather"][0]["description"].capitalize()}')
                    break

    def get_forecast_day(self):
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={
            'q': self.city,
            'units': 'metric',
            'lang': 'ru',
            'APPID': self.appid
        })

        data = res.json()
        form = '%Y-%m-%d %H:%M:%S'

        self.voice.say(f'Прогноз погоды на завтра в городе {self.city.capitalize()}:')
        for info in data['list']:
            if datetime.strptime(info['dt_txt'], form).day - self.now_date.day == 1:
                print(f'Время: {datetime.strptime(info["dt_txt"], form).time()}\t'
                      f'Температура: {info["main"]["temp"]}\t'
                      f'{info["weather"][0]["description"]}')

    def week_forecast_time(self):
        week = {
            'Monday': 'понедельник',
            'Tuesday': 'вторник',
            'Wednesday': 'среда',
            'Thursday': 'четверг',
            'Friday': 'пятница',
            'Saturday': 'суббота',
            'Sunday': 'воскресенье',
        }

        res = requests.get("http://api.openweathermap.org/data/2.5/forecast", params={
            'q': self.city,
            'units': 'metric',
            'lang': 'ru',
            'APPID': self.appid
        })

        data = res.json()
        form = '%Y-%m-%d %H:%M:%S'

        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        self.voice.say(f'Прогноз погоды в городе {self.city.capitalize()} ({week[week_days[self.day.weekday()]]}):')
        for info in data['list']:
            if self.day == datetime.strptime(info['dt_txt'], form).date():
                print(f'{datetime.strptime(info["dt_txt"], form)}\t'
                      f'Температура: {info["main"]["temp"]}\t'
                      f'{info["weather"][0]["description"]}')
