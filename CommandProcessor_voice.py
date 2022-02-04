import os
import wikipedia
import webbrowser
from bs4 import BeautifulSoup
from pycbrf import ExchangeRates
import time
import datetime
import re
import requests
import sys
import random
import psutil

from CameraProcessor import CameraProcessor
from Memory import Memory
from Weather_voice import WeatherAPI
from SongAPI import SongFinder
from VoiceProcessor import VoiceProcessor


class CommandProcessor(CameraProcessor, Memory, WeatherAPI):
    def __init__(self):
        self.dict_command = {
            'hello': self.hello,
            'bye': self.bye,
            'thanks': self.thanks,
            'how_are_you_AI': self.how_are_you_AI,
            'name': self.name,
            'skills': self.skills,
            'messenger': self.messenger,
            'open_web': self.open_web,
            'find_lyrics': self.find_lyrics,
            'wiki': self.wiki,
            'time': self.time,
            'money_values': self.money_values,
            'new_project': self.new_project,
            'system_states': self.system_states,
            'where_is_iss': self.where_is_iss,
            'weather': self.weather,
            'news': self.news,
            'surrounding': self.surrounding,
            'who_am_i': self.who_am_i,
            'new_user_photos': self.new_user_photos,
            'volume_hand_control': self.volume_hand_control,
            'finger_mouse': self.finger_mouse,
            'update_model': self.update_model,
            'argue': self.argue,
            'undefined_intent': self.undefined_intent,
        }

        self.question = None
        self.CONFIG = None
        self.intent = None
        self.first_intent = None

        self.camera_detector = CameraProcessor()
        self.voice = VoiceProcessor()
        self.memory = Memory()

    def initialize(self, intent, question, config):
        self.question = question
        self.CONFIG = config
        self.intent = intent
        self.memory.storage.append(self.intent)
        self.dict_command[self.intent]()

    def translitirator(self, text):
        new_text = ''
        translits = {
            'q': 'й',   'w': 'ц',   'e': 'у',   'r': 'к',     't': 'е',   'y': 'н',   'u': 'г',   'i': 'ш',
            'o': 'щ',   'p': 'з',   '[': 'х',   ']': 'ъ',     'a': 'ф',   's': 'ы',   'd': 'в',   'f': 'а',
            'g': 'п',   'h': 'р',   'j': 'о',   'k': 'л',     'l': 'д',   ';': 'ж',   "'": 'э',   'z': 'я',
            'x': 'ч',   'c': 'с',   'v': 'м',   'b': 'и',     'n': 'т',   'm': 'ь',   ',': 'б',   '.': 'ю',
            ' ': ' '
        }
        for char in text:
            new_text += translits[char]
        return new_text

    def hello(self):
        if self.memory.hello['repeats'] == 0:
            self.memory.hello['repeats'] += 1
            self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))

        elif self.memory.hello['repeats'] == 1:
            self.memory.hello['repeats'] += 1
            self.voice.say(random.choice(['По-моему, мы уже здоровались', 'Мы уже здоровались', 'И снова здравствуйте']))

        elif self.memory.hello['repeats'] == 2:
            self.memory.hello['repeats'] += 1
            self.voice.say(random.choice(['Вы забыли, что мы уже здоровались?', 'Опять за старое?', 'У меня дежавю']))

        else:
            self.memory.hello['repeats'] += 1
            self.voice.say(random.choice(['Уже даже не смешно', 'Однажды вам это надоест', 'Простите, но я промолчу...']))

    def bye(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        sys.exit(0)

    def thanks(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        self.memory.argue['good'] += 1

    def how_are_you_AI(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        self.memory.argue['good'] += 1

    def name(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))

    def skills(self):
        skills_list = self.CONFIG['intents'][self.intent]['responses']
        if len(skills_list) != 0:
            skill = random.choice(skills_list)
            skills_list.remove(skill)
            self.voice.say(skill)
        else:
            self.voice.say('Пока что это все команды, которые я знаю, могу только перечислить все сначала')

    def messenger(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        webbrowser.open('https://vk.com/esthete_01', new=1)

    def open_web(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        webbrowser.open('https://www.google.com/search?q=' +
                        self.question[6:] + '&oq=rfr&aqs=chrome..69i57j0l7.2032j0j7&sourceid=chrome&ie=UTF-8')

    def find_lyrics(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        print('Напойте строчки:')
        text_input = self.voice.get_command()
        print(text_input)
        song_api = SongFinder(text_input, self.memory)

        song = song_api.find_song_name()
        artist = song_api.find_song_artist()

        self.voice.say(f"Это песня {song} исполнителя {artist}\n")

        lyrics = song_api.find_strings()

        self.voice.say(f"{lyrics}")

    def wiki(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        text = ''
        for word in self.question.split(' '):
            if word not in ' '.join(self.CONFIG['intents']['wiki']['examples']):
                text += ''.join(word) + " "
        wikipedia.set_lang('ru')
        title = wikipedia.search(text)[0]
        self.voice.say(wikipedia.summary(title, sentences=3))

    def time(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        time_got = str(time.ctime())
        time_got = time_got[-13:-8]
        self.voice.say('Сейчас ' + time_got)

    def money_values(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        current_time = datetime.datetime.today().strftime("%Y-%m-%d")
        rates = ExchangeRates(current_time)
        if re.compile(r"доллара|доллар|доллары").search(self.question) and "евро" in self.question:
            self.voice.say(f'Доллар: {str(rates["USD"].value)[:-2]}\n'
                           f'Евро: {str(rates["EUR"].value)[:-2]}')
        elif not (re.compile(r"доллара|доллар|доллары").search(self.question)) and not ("евро" in self.question):
            self.voice.say(f'Доллар: {str(rates["USD"].value)[:-2]}\n'
                           f'Евро: {str(rates["EUR"].value)[:-2]}')
        elif re.compile(r"доллара|доллар|доллары").search(self.question):
            self.voice.say(f'Доллар: {str(rates["USD"].value)[:-2]}')
        elif "евро" in self.question:
            self.voice.say(f'Евро: {str(rates["EUR"].value)[:-2]}')

    def new_project(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        prog_count = 1
        if not os.path.isdir('C:/Users/a_pin/OneDrive/Рабочий стол/Python проекты/New_projects'):
            os.chdir('C:/Users/a_pin/OneDrive/Рабочий стол/Python проекты')
            os.mkdir('New_projects')
        else:
            os.chdir('C:/Users/a_pin/OneDrive/Рабочий стол/Python проекты/New_projects')

        while True:
            full_name = f'C:/Users/a_pin/OneDrive/Рабочий стол/Python проекты/New_projects/project_{str(prog_count)}.py'
            if os.path.isfile(full_name) is False:
                os.open(full_name, os.O_CREAT)
                with open(full_name, 'w') as file:
                    file.write(f'# New project ({prog_count}) for new ideas')
                break
            else:
                prog_count += 1
        os.startfile(f'project_{prog_count}.py')

    def system_states(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        cpu_load = psutil.cpu_percent()
        virt_mem = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        time_left = str(datetime.timedelta(seconds=battery.secsleft))
        psutil.swap_memory()
        self.voice.say(f'\nCPU используется: {cpu_load} %\n'
              f'Память используется: {virt_mem[2]} %\n'
              f'Заряд батареи: {battery[0]} %')
        if battery.power_plugged:
            self.voice.say('Компьютер подключен к питанию')
        else:
            self.voice.say(f'Осталось: {time_left}')

        maxi = 0
        processes = []
        proc_memory = []
        hard_processes = []
        hard_proc_mem = []

        for p in psutil.process_iter():
            if int(p.memory_percent()) >= maxi:
                processes.append(p.name())
                proc_memory.append(int(p.memory_percent()))
                maxi = int(p.memory_percent())

        for count in range(5):
            hard_proc_mem.append(max(proc_memory))
            hard_processes.append(processes[proc_memory.index(max(proc_memory))])
            proc_memory[proc_memory.index(max(proc_memory))] = 0

        self.voice.say('\nПроцессы, нагружающие ОЗУ:')
        for i, process in enumerate(hard_processes):
            print(f'{i + 1}.\t{process}\t({hard_proc_mem[i]} % памяти)')

    def where_is_iss(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        url = 'https://api.wheretheiss.at/v1/satellites/25544'
        result = requests.get(url).json()
        if result['visibility'] == 'daylight':
            result['visibility'] = 'на солнечной стороне'
        elif result['visibility'] == 'eclipsed':
            result['visibility'] = 'в тени'
        self.voice.say(f"Широта: {round(result['latitude'], 3)}\n"
                       f"Долгота: {round(result['longitude'], 3)}\n"
                       f"Скорость: {round(result['velocity'], 3)} км/ч\n"
                       f"Высота: {round(result['altitude'], 3)} км\n"
                       f"Видимость: {result['visibility']}")

        map_url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/" \
                  f"reverseGeocode?outSR=4326&returnIntersection=false&" \
                  f"location={result['longitude']}%2C{result['latitude']}&f=json"
        result = requests.get(map_url).json()

        if result['address']['Region'] == '' and result['address']['LongLabel'] != '':
            self.voice.say(f"Положение: {result['address']['LongLabel']}")
        elif result['address']['Region'] != '' and result['address']['LongLabel'] == '':
            self.voice.say(f"Положение: {result['address']['Region']}")
        elif result['address']['Region'] == '' and result['address']['LongLabel'] == '':
            self.voice.say(f"Положение: {result['address']['Region']}, {result['address']['LongLabel']}")

    def weather(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))

        weather_api = WeatherAPI(self.question, self.memory)

        if 'погода' in self.question.split(' '):
            self.memory.weather['city'] = None
            self.memory.weather['is_city'] = None
            self.memory.weather['day'] = datetime.datetime.now().date()
            city, cur_city = weather_api.get_city()
            day = weather_api.get_day()
            self.memory.weather['city'] = city
            self.memory.weather['is_city'] = cur_city
            self.memory.weather['day'] = day
        else:
            city = self.memory.weather['city']
            cur_city = self.memory.weather['is_city']
            day = self.memory.weather['day']

            fcity, fcur_city = weather_api.get_city()
            fday = weather_api.get_day()

            if fcity != city:
                city = fcity
            if fcur_city != cur_city:
                cur_city = fcur_city
            if fday != day:
                day = fday

            self.memory.weather['city'] = city
            self.memory.weather['is_city'] = cur_city
            self.memory.weather['day'] = day

        now_date = datetime.datetime.now().date()

        if day == now_date:
            weather_api.get_current()
        elif day == now_date + datetime.timedelta(days=1) and 'вся' not in self.question.split(' '):
            weather_api.get_forecast_time()
        elif day == now_date + datetime.timedelta(days=1) and 'вся' in self.question.split(' '):
            weather_api.get_forecast_day()
        elif day != now_date:
            weather_api.week_forecast_time()
        else:
            self.voice.say('Не смогла найти ответ на ваш запрос')

    def news(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        if 'политик' in self.question:
            url = 'https://yandex.ru/news/rubric/politics'
        elif 'обществ' in self.question:
            url = 'https://yandex.ru/news/rubric/society'
        elif 'экономик' in self.question:
            url = 'https://yandex.ru/news/rubric/business'
        elif 'культур' in self.question:
            url = 'https://yandex.ru/news/rubric/culture'
        elif 'технологи' in self.question:
            url = 'https://yandex.ru/news/rubric/computers'
        elif 'наук' in self.question:
            url = 'https://yandex.ru/news/rubric/science'
        elif 'авто' in self.question:
            url = 'https://yandex.ru/news/rubric/auto'
        else:
            url = 'https://yandex.ru/news'

        text_html = requests.get(url)
        page = BeautifulSoup(text_html.text, 'html.parser')
        news = page.findAll('h2', class_='mg-card__title', limit=5)
        news_source = page.findAll('a', class_='mg-card__source-link', limit=5)
        news_time = page.findAll('span', class_='mg-card-source__time', limit=5)

        for i, data in enumerate(news):
            self.voice.say(f'{i + 1}.\t{data.text}\n\tИсточник: {news_source[i].text}\n\tВремя: {news_time[i].text}')

    def check_admin(self):
        return self.camera_detector.check_admin()

    def surrounding(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        self.camera_detector.face_recognition(show=True, check=False)

    def who_am_i(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        id, confidence = self.camera_detector.who_am_i()
        if id == 'Unknown':
            assurance_phrase = 'К сожалению, я вас не узнаю, но это легко исправить!'
        elif 50 <= confidence <= 99:
            assurance_phrase = f'Уверена на {int(confidence)}%, что вы {id}'
        elif 40 <= confidence < 50:
            assurance_phrase = f'С вероятностью {int(confidence)}% вы {id}'
        elif 20 <= confidence < 40:
            assurance_phrase = f'Возможно вы {id} (вероятность {int(confidence)}%)'
        else:
            assurance_phrase = f'Трудно сказать, но мне кажется, что вы ' + id
        self.voice.say(assurance_phrase)

    def new_user_photos(self):
        self.voice.say('Сядьте поближе к камере так, чтобы вас было хорошо видно')
        self.camera_detector.make_image()
        self.camera_detector.make_model()

    def volume_hand_control(self):
        print(
            'Указания к использованию:\n',
            '1. Покажите ладонь, чтобы установить громкость\n',
            '2. Сожмите все пальцы, кроме указательного и большого, чтобы начать регулировку\n',
            '3. Отдаляйте / сближайте пальцы, чтобы увеличить / уменьшить громкость\n',
            '4. Для завершения регулировки покажите ладонь и согните большой палец\n',
            'Вы можете смотреть за процессом через камеру'
        )
        self.camera_detector.volume_control()

    def finger_mouse(self):
        self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
        self.voice.say('Перед использованием поднимите большой и указательный палец левой руки вверх')
        print(
            'Указания к использованию:\n',
            '1. перемещайте курсор указательным пальцем\n',
            '2. Чтобы остановить перемещение, поднимите средний палец\n',
            '3. Чтобы сделать клик, сожмите большой палец\n',
            '4. Поднимите и опустите мизинец, чтобы перейти в режим скроллинга\n',
            '5. Поднимите все пальцы, чтобы выйти из этого режима'
            'Вы можете смотреть за процессом через камеру'
        )
        self.camera_detector.finger_mouse()

    def update_model(self):
        # команда выполняется в классе FridayAI через проверку intent
        # можно попробовать переделать, но пусть пока будет здесь
        pass

    def argue(self):
        if self.memory.argue['good'] == 1:
            if self.memory.argue['repeats'] == 0:
                self.voice.say(random.choice(['Кто-то сегодня встал не с той ноги',
                                              'Если у вас плохое настроение, то не нужно вываливать это все на меня',
                                              'Уверена, вы не со зла']))
                self.memory.argue['repeats'] += 1
            else:
                self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
                sys.exit(0)
        elif self.memory.argue['good'] >= 2:
            if self.memory.argue['repeats'] == 0:
                self.voice.say(random.choice(['Это было обидно, но на первый раз прощу',
                                              'Надеюсь, вы обдумали свои слова',
                                              'Уверена, вы не со зла']))
                self.memory.argue['repeats'] += 1
            elif self.memory.argue['repeats'] == 1:
                self.voice.say(random.choice(['Последнее предупреждение',
                                              'Последнее китайское предупреждение',
                                              'Еще раз и нам придется попрощаться']))
                self.memory.argue['repeats'] += 1
            else:
                self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
                sys.exit(0)
        else:
            self.voice.say(random.choice(self.CONFIG['intents'][self.intent]['responses']))
            sys.exit(0)

        self.memory.argue['good'] -= 1

    def undefined_intent(self):
        self.first_intent = self.intent
        self.intent = self.memory.storage[-2]
        print(f'[log] Reminded: {self.intent}')
        self.memory.storage.append(self.intent)
        self.dict_command[self.intent]()
