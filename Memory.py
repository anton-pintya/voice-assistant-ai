

class Memory:
    def __init__(self):
        '''
        self.storage = {
            'hello': self.hello,  # ---------------------------------------- как зовут
            'bye': self.bye,
            'how_are_you_AI': self.how_are_you_AI,  # ---------------------- ответный вопрос
            'name': self.name,  # ------------------------------------------ как зовут
            'messenger': self.messenger,  # -------------------------------- возможно выбор сайта
            'open_web': self.open_web,  # ---------------------------------- возможно выбор поисковика
            'wiki': self.wiki,  # ------------------------------------------ больше информации
            'time': self.time,
            'money_values': self.money_values,  # -------------------------- график, возможно прогноз
            'new_project': self.new_project,  # ---------------------------- выбор папки или названия
            'weather': self.weather,  # ------------------------------------
            'news': self.news,  # ------------------------------------------ выбор тем и сайтов
            'surrounding': self.surrounding,
            'new_user_photos': self.new_user_photos,  # -------------------- кол-во фоток
            'volume_hand_control': self.volume_hand_control,
            'update_model': self.update_model,
            'argue': self.argue  # -----------------------------------------
        }
        '''
        self.storage = []

        self.hello = {
            'name': None,
            'repeats': 0
        }
        self.how_are_you_AI = {
            'mood': None
        }
        self.name = {
            'username': None
        }
        self.messenger = {
            'web-site': None,
            'search': None
        }
        self.open_web = {
            'browser': None
        }
        self.find_lyrics = {
            'artist': None,
            'song': None,
            'lyrics': None
        }
        self.wiki = {
            'more_info': None,
            'articles': None
        }
        self.money_values = {
            'graphics': None,
            'forecast': None
        }
        self.new_project = {
            'directory': None,
            'filename': None
        }
        self.weather = {
            'city': None,
            'weekday': None,
            'is_city': None,
            'next_day': None,
            'today': None,
            'day': None
        }
        self.news = {
            'topic': None,
            'web-site': None
        }
        self.new_user_photos = {
            'number': None
        }
        self.argue = {
            'good': 0,
            'repeats': 0
        }
