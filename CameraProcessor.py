import cv2
import numpy as np
from PIL import Image
import os

import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import autopy


class CameraProcessor:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640)
        self.cam.set(4, 480)

        cascade_path = 'C:/Users/a_pin/AppData/Local/Programs/Python/Python38/Lib/site-packages/cv2/data' \
                       '/haarcascade_frontalface_default.xml '
        self.face_detector = cv2.CascadeClassifier(cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.output_info = True

    def faces_update(self):
        current_mod = float(os.path.getmtime('image_dataset'))
        with open('config_trainer.txt', 'r') as f:
            previous_mod = float(f.read())
        if current_mod != previous_mod:
            os.remove('config_trainer.txt')
            with open('config_trainer.txt', 'w') as f:
                f.write(str(current_mod))
            if self.output_info:
                print("База данных пользователей обновлена")
                self.output_info = False
            return False
        else:
            if self.output_info:
                print("Новых пользователей не найдено")
                self.output_info = False
            return True

    def make_image(self):
        face_name = input('Введите имя нового пользователя (для отмены напишите "отмена"): ')
        if face_name == 'отмена':
            return print('Задача отменена')

        path = 'C:/Users/a_pin/OneDrive/Рабочий стол/Friday AI/image_dataset'
        imagePaths = [os.path.join(path, file) for file in os.listdir(path)]

        names = []
        for imagePath in imagePaths:
            name = os.path.split(imagePath)[-1].split(".")[0]
            if name not in names:
                names.append(name)
        face_id = len(names)

        count = 0
        while True:
            suc, img = self.cam.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                count += 1
                cv2.imwrite(f"C:/Users/a_pin/OneDrive/Рабочий стол/Friday AI/image_dataset/"
                            f"{face_name}.{face_id}.{count}.jpg", gray[y: y + h, x: x + w])

            cv2.imshow("Face", img)

            if cv2.waitKey(1) == 27 or count >= 200:
                cv2.destroyAllWindows()
                return 'Запомнила!'

    def make_model(self):
        path = 'C:/Users/a_pin/OneDrive/Рабочий стол/Friday AI/image_dataset'
        imagePaths = [os.path.join(path, file) for file in os.listdir(path)]
        faceSamples = []
        ids = []

        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = self.face_detector.detectMultiScale(img_numpy)

            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y + h, x:x + w])
                ids.append(id)

        self.recognizer.train(faceSamples, np.array(ids))
        self.recognizer.write('trainer.yml')

    def face_recognition(self, show=True, check=False):
        self.recognizer.read('trainer.yml')
        font = cv2.FONT_HERSHEY_SIMPLEX

        path = 'C:/Users/a_pin/OneDrive/Рабочий стол/Friday AI/image_dataset'
        imagePaths = [os.path.join(path, file) for file in os.listdir(path)]

        guests = []
        names = []
        for imagePath in imagePaths:
            name = os.path.split(imagePath)[-1].split(".")[0]
            if name not in names:
                names.append(name)
        names.append('Unknown')

        minW = 0.1 * self.cam.get(3)
        minH = 0.1 * self.cam.get(4)

        while True:
            suc, img = self.cam.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH)),
            )
            ids = []
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                id, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
                ids.append(id)

                if confidence < 100:
                    if  confidence < 15:
                        id = "Unknown"
                    else:
                        id = names[id]

                    if ('Anton' in id) and (int(100 - confidence) >= 55) and check:
                        return True
                    elif ('Anton' in id) and len(faces) == 1 and (int(100 - confidence) >= 40) and check:
                        return True
                else:
                    id = "Unknown"

                if id not in guests:
                    guests.append(id)
                confidence = "{0}%".format(round(100 - confidence))

                cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

            if show:
                cv2.imshow("Camera", img)
                if cv2.waitKey(1) == 27:
                    cv2.destroyAllWindows()
                    print(f'Вот, кого я увидела: {", ".join(guests)}')
                    break

    def check_admin(self):
        return self.face_recognition(show=False, check=True)

    def who_am_i(self):
        self.recognizer.read('trainer.yml')

        path = 'C:/Users/a_pin/OneDrive/Рабочий стол/Friday AI/image_dataset'
        imagePaths = [os.path.join(path, file) for file in os.listdir(path)]

        id = 'Unknown'
        confidence = 'None'
        names = []
        for imagePath in imagePaths:
            name = os.path.split(imagePath)[-1].split(".")[0]
            if name not in names:
                names.append(name)
        names.append('Unknown')

        minW = 0.1 * self.cam.get(3)
        minH = 0.1 * self.cam.get(4)

        count_frames = 0
        while count_frames < 30:
            suc, img = self.cam.read()
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH)),
            )

            for (x, y, w, h) in faces:

                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                id, confidence = self.recognizer.predict(gray[y:y + h, x:x + w])
                if 20 <= confidence < 100:
                    id = names[id]

            count_frames += 1

        return id, confidence

    def volume_control(self):
        detector = htm.HandDetector(detectionCon=0.7, maxHands=1)

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        while True:
            success, image = self.cam.read()
            image = cv2.flip(image, 1)

            image = detector.findHands(image)
            lnList, bBox = detector.findPosition(image, draw=False)

            if len(lnList) != 0:
                area = (bBox[2] - bBox[0]) * (bBox[3] - bBox[1]) // 100

                if 100 < area < 1100:
                    length, image, lineInfo = detector.findDistance(4, 8, image)

                    volPer = np.interp(length, [15, 210], [0, 100])

                    smoothness = 10
                    volPer = smoothness * round(volPer / smoothness)

                    fingers = detector.fingersUp()

                    if not fingers[4] and not fingers[3]:
                        volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                        finalVolume = volPer
                        showVol = True
                        cv2.circle(image, (lineInfo[4], lineInfo[5]), 10, (0, 230, 0), cv2.FILLED)
                    elif fingers[4] and fingers[3] and not fingers[0]:
                        cv2.destroyAllWindows()
                        break
                    elif fingers[4] and fingers[3]:
                        try:
                            if showVol:
                                print(f'Громкость: {finalVolume}')
                                showVol = False
                        except UnboundLocalError:
                            pass

            cv2.imshow("Finger tracking", image)

            if cv2.waitKey(1) == 27:
                cv2.destroyAllWindows()
                break

    def finger_mouse(self):
        wCam, hCam = 640, 480
        self.cam.set(3, wCam)
        self.cam.set(4, hCam)

        wScr, hScr = autopy.screen.size()
        frameR = 50

        smoothning = 3
        pLocX, pLocY = 0, 0

        detector = htm.HandDetector(detectionCon=0.8, maxHands=1)
        scroll_allowed = True

        while True:
            success, image = self.cam.read()
            image = cv2.flip(image, 1)

            image = detector.findHands(image)
            lnList, bBox = detector.findPosition(image, draw=False)

            if len(lnList) != 0:
                x1, y1 = lnList[8][1], lnList[8][2]
                x2, y2 = lnList[4][1], lnList[4][2]

                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR - 75), (0, hScr))

                cLocX = pLocX + (x3 - pLocX) / smoothning
                cLocY = pLocY + (y3 - pLocY) / smoothning

                cv2.rectangle(image, (frameR, frameR), (wCam - frameR, hCam - frameR - 75), (0, 255, 0), 2)

                fingers = detector.fingersUp()

                if not fingers[2]:
                    autopy.mouse.move(cLocX, cLocY)
                    pLocX, pLocY = cLocX, cLocY
                if fingers[2] and fingers[1] and x2 >= x1:
                    autopy.mouse.click()
                if fingers[0] and fingers[1] and fingers[4] and not fingers[2] and not fingers[3]:
                    if scroll_allowed:
                        autopy.mouse.click(autopy.mouse.Button.MIDDLE)
                    else:
                        scroll_allowed = True
                if fingers[0] and fingers[1] and fingers[2] and fingers[3] and fingers[4]:
                    cv2.destroyAllWindows()
                    break

            cv2.imshow("Finger tracking", image)

            if cv2.waitKey(1) == 27:
                break
