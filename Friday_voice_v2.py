import os
import pickle
import json
import random

import nltk

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from CommandProcessor_voice import CommandProcessor
from VoiceProcessor import VoiceProcessor


class FridayAI(CommandProcessor, VoiceProcessor):
    def __init__(self):
        self.processor = CommandProcessor()
        self.voice = VoiceProcessor()

        self.CONFIG = json.load(
            open('dataset.json', 'r', encoding='utf-8'))
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 4), min_df=1, max_df=0.75)
        self.classifier = RandomForestClassifier()
        self.output_info = True

    def config_mod(self):
        current_mod = float(os.path.getmtime('dataset.json'))
        with open('config_version.txt', 'r') as f:
            previous_mod = float(f.read())
        if current_mod != previous_mod:
            os.remove('config_version.txt')
            with open('config_version.txt', 'w') as f:
                f.write(str(current_mod))
            if self.output_info:
                print("[log] Переобучена")
                self.output_info = False
            return False
        else:
            if self.output_info:
                print("[log] Модель без изменений")
                self.output_info = False
            return True

    def train(self):
        x = []
        y = []
        for intent in self.CONFIG['intents']:
            x += self.CONFIG['intents'][intent]['examples']
            y += [intent] * len(self.CONFIG['intents'][intent]['examples'])

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
        self.vectorizer.fit(x_train)
        x_vectorized = self.vectorizer.fit_transform(x_train).toarray()
        pickle.dump(self.vectorizer, open('vectorizer.pkl', 'wb'))

        self.classifier.fit(x_vectorized, y_train)
        while self.classifier.score(self.vectorizer.transform(x_test), y_test) < 0.78:
            self.classifier.fit(x_vectorized, y_train)
        self.voice.say(f'Точность текущей модели: {round(self.classifier.score(self.vectorizer.transform(x_test), y_test), 3)}')
        pickle.dump(self.classifier, open('model.pkl', 'wb'))

        return self.vectorizer, self.classifier

    def compare(self, s1, s2):
        return (nltk.edit_distance(s1, s2) / (len(s1 + s2) / 2)) < 0.4

    def get_intent(self, question):
        for intent in self.CONFIG['intents']:
            for example in self.CONFIG['intents'][intent]['examples']:
                if self.compare(example, question):
                    return intent

    def get_intent_ml(self, question):
        if self.config_mod():
            vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
            model = pickle.load(open('model.pkl', 'rb'))
        else:
            vectorizer, model = self.train()
        intent = model.predict(vectorizer.transform([question]))[0]
        return intent

    def talk(self):
        question = None
        while question is None:
            question = self.voice.get_command()
        print(question)

        if self.get_intent(question) is not None:
            intent = self.get_intent(question)
            print(f'[log] Found: {intent}')
        else:
            intent = self.get_intent_ml(question)
            print(f'[log] Predicted: {intent}')

        if intent == 'update_model':
            self.voice.say(random.choice(self.CONFIG['intents'][intent]['responses']))
            self.train()
            self.voice.say('Модель переобучена')

        self.processor.initialize(intent, question, self.CONFIG)

    def start(self, check=True):
        if check:
            if self.processor.check_admin():
                print('[log] Доступ разрешен')
                return True
        else:
            return True


if __name__ == "__main__":
    print("[log] Подождите")
    bot = FridayAI()
    #if bot.start():
    bot.config_mod()
    while True:
        bot.talk()
