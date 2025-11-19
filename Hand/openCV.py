# -*- coding: utf-8 -*-
"""
openCV.py - Test Camera & Hand Gesture Recognition
NGÀY: 19/11/2025
"""
import cv2
import time
import hand as htm

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

pTime = 0
detector = htm.handDetector(detectionCon=0.7, maxHands=2)

colors = {
    'X': (128, 128, 128),
    'W': (0, 255, 0),
    'S': (0, 0, 255),
    'A': (255, 0, 255),
    'D': (0, 255, 255)
}

last_gesture = None

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame = detector.findHands(frame)
    gesture, description = detector.analyzeGesture(frame)
    color = colors.get(gesture, (255, 255, 255))
    
    if gesture != last_gesture:
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Cử chỉ: {gesture} - {description}")
        last_gesture = gesture
    
    cv2.rectangle(frame, (20, 20), (700, 200), color, -1)
    cv2.rectangle(frame, (20, 20), (700, 200), (0, 0, 0), 5)
    
    cv2.putText(frame, f"Output: {gesture}", (40, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 5)
    cv2.putText(frame, description, (40, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4)
    
    cv2.putText(frame, "X: DUNG (khong co tay) | W: TIEN (nam tay)", 
                (20, frame.shape[0] - 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "S: LUI (xoe tay)", 
                (20, frame.shape[0] - 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "A: TRAI (tay phai cao hon) | D: PHAI (tay trai cao hon)", 
                (20, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(frame, f"FPS: {int(fps)}", (frame.shape[1] - 200, 40),
                cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 3)

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
