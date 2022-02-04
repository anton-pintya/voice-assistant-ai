import speech_recognition as sr
import pyttsx3


class VoiceProcessor:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 235)

    def get_command(self):
        try:
            r = sr.Recognizer()
            with sr.Microphone(device_index=1) as source:
                r.adjust_for_ambient_noise(source, duration=1)
                print('[log] Говорите')
                audio = r.listen(source, phrase_time_limit=4)
            command = r.recognize_google(audio, language='ru-RU').lower()
            return command
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print('[log] Проверьте подключение к сети Интернет')

    def say(self, words):
        print(words)
        self.engine.say(words)
        self.engine.runAndWait()
        self.engine.stop()
