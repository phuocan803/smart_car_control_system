# -*- coding: utf-8 -*-
"""
hand.py - MediaPipe Hand Detection Module
NGÀY: 19/11/2025
"""
import cv2
import mediapipe as mp

class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                h, w, c = img.shape
                for id, lm in enumerate(myHand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)
        return lmList
    
    def getAllHandsPosition(self, img):
        allHands = []
        if self.results.multi_hand_landmarks and self.results.multi_handedness:
            h, w, c = img.shape
            for handLms, handedness in zip(self.results.multi_hand_landmarks, self.results.multi_handedness):
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                
                handType = handedness.classification[0].label
                allHands.append({'lmList': lmList, 'type': handType})
        return allHands
    
    def countExtendedFingers(self, lmList):
        if len(lmList) == 0:
            return 0
        
        fingerTips = [8, 12, 16, 20]
        fingerPips = [6, 10, 14, 18]
        
        count = 0
        for tip, pip in zip(fingerTips, fingerPips):
            if lmList[tip][2] < lmList[pip][2] - 20:
                count += 1
        return count
    
    def getHandHeight(self, lmList):
        if len(lmList) == 0:
            return 0
        return (lmList[0][2] + lmList[9][2]) / 2
    
    def analyzeGesture(self, img):
        allHands = self.getAllHandsPosition(img)
        
        if len(allHands) != 2:
            return 'X', "DUNG - Can 2 tay"
        
        leftHand = None
        rightHand = None
        for hand in allHands:
            if hand['type'] == 'Left':
                rightHand = hand
            else:
                leftHand = hand
        
        if leftHand is None or rightHand is None:
            return 'X', "DUNG - Can 2 tay"
        
        leftFingers = self.countExtendedFingers(leftHand['lmList'])
        rightFingers = self.countExtendedFingers(rightHand['lmList'])
        leftHeight = self.getHandHeight(leftHand['lmList'])
        rightHeight = self.getHandHeight(rightHand['lmList'])
        
        if leftHeight < rightHeight - 80:
            return 'D', f"PHAI (L:{leftFingers} R:{rightFingers})"
        elif rightHeight < leftHeight - 80:
            return 'A', f"TRAI (L:{leftFingers} R:{rightFingers})"
        
        if leftFingers <= 1 and rightFingers <= 1:
            return 'W', f"TIEN (L:{leftFingers} R:{rightFingers})"
        elif leftFingers >= 3 and rightFingers >= 3:
            return 'S', f"LUI (L:{leftFingers} R:{rightFingers})"
        else:
            return 'X', f"DUNG (L:{leftFingers} R:{rightFingers})"
