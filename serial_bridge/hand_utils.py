# -*- coding: utf-8 -*-
"""
hand_utils.py - MediaPipe Hand Detection & Gesture Analysis Helper Utilities
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

    def getFingersUp(self, lmList):
        tipIds = [4, 8, 12, 16, 20]
        fingers = []
        if len(lmList) == 0:
            return fingers

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def detectGesture(self, img):
        allHands = self.getAllHandsPosition(img)
        
        if len(allHands) == 0:
            return 'X', "No hands detected"
        
        leftHand = None
        rightHand = None
        
        for hand in allHands:
            if hand['type'] == 'Left':
                leftHand = hand
            elif hand['type'] == 'Right':
                rightHand = hand
        
        if leftHand is None or rightHand is None:
            return 'X', "Requires 2 hands"
        
        leftFingers = self.getFingersUp(leftHand['lmList'])
        rightFingers = self.getFingersUp(rightHand['lmList'])
        
        leftCount = sum(leftFingers)
        rightCount = sum(rightFingers)
        
        leftWrist = leftHand['lmList'][0][2]
        rightWrist = rightHand['lmList'][0][2]
        
        # Check Forward / Reverse / Left / Right gesture logic
        if leftCount <= 1 and rightCount <= 1:
            return 'W', "Forward (Both fists closed)"
        
        if leftCount >= 3 and rightCount >= 3:
            return 'S', "Reverse (Both hands open)"
        
        diff = leftWrist - rightWrist
        if diff > 80:
            return 'A', "Turn Left (Right hand raised)"
        elif diff < -80:
            return 'D', "Turn Right (Left hand raised)"
            
        return 'X', "Default / Stop Pose"
