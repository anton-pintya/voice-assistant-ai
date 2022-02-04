import mediapipe as mp
import cv2
import math


class HandDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackingCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackingCon = trackingCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackingCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
    
    def findHands(self, image, draw = True):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)

        return image

    def findPosition(self, image, handNo = 0, draw = True):
        xList = []
        yList = []
        bBox = []
        self.lnList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, ln in enumerate(myHand.landmark):
                h, w, c = image.shape
                cx, cy = int(ln.x * w), int(ln.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lnList.append([id, cx, cy])
                if draw:
                    cv2.circle(image, (cx, cy), 7, (255, 0, 0), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bBox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(image, (bBox[0] - 20, bBox[1] - 20), (bBox[2] + 20, bBox[3] + 20), (0, 255, 0), 2)

        return self.lnList, bBox

    def fingersUp(self):
        fingers = []
        
        if (self.lnList[self.tipIds[0]][1] > self.lnList[self.tipIds[0] - 1][1]) and (self.lnList[self.tipIds[0]][1] > self.lnList[self.tipIds[4]][1]) or (self.lnList[self.tipIds[0]][1] < self.lnList[self.tipIds[0] - 1][1]) and (self.lnList[self.tipIds[0]][1] < self.lnList[self.tipIds[4]][1]):
                fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if self.lnList[self.tipIds[id]][2] < self.lnList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers   

    def findDistance(self, p1, p2, image, draw = True):
        x1, y1 = self.lnList[p1][1], self.lnList[p1][2] 
        x2, y2 = self.lnList[p2][1], self.lnList[p2][2] 
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(image, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(image, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 4)
            cv2.circle(image, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)   
        
        return length, image, [x1, y1, x2, y2, cx, cy]

def main():
    cap = cv2.VideoCapture(0)

    detector = HandDetector()

    while True:
        success, image = cap.read()
        
        image = detector.findHands(image)
        lnList = detector.findPosition(image)
        
        if len(lnList) != 0:
            print(lnList[8])

        cv2.imshow("Finger tracking", image)
        
        if cv2.waitKey(1) == 27:
            break

if __name__ == '__main__':
    main()