#pip install opencv-contrib-python
#pip install cvzone
#pip install mediapipe #for cvzone
#pip install mouse
#pip install numpy
#pip install threading
#pip install time

import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import numpy as np
import threading
import time


detector = HandDetector(detectionCon=0.9, maxHands=1)
# 1 external webcam | 0 system webcam 
cap = cv2.VideoCapture(0)
cam_w = 640
cam_h = 480
cap.set(3, cam_w)
cap.set(4, cam_h)

frameR = 100 # To solve the issues related to the cursor moving off the right and bottom edges of the screen

l_delay = 0
r_delay = 0
double_delay = 0

def l_clk_delay ():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay = 0
    l_clk_thread = threading.Thread(target= l_clk_delay)

def r_clk_delay ():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target= r_clk_delay)

def double_clk_delay ():
    global double_delay
    global double_clk_thread
    time.sleep(2)
    double_delay = 0
    double_clk_thread = threading.Thread(target= double_clk_delay)

l_clk_thread = threading.Thread(target= l_clk_delay)
r_clk_thread = threading.Thread(target= r_clk_delay)
double_clk_thread = threading.Thread(target= double_clk_delay)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    cv2.rectangle(img, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2 )
    
    if hands:
        lmlist = hands[0]['lmList']
        ind_x = lmlist[8][0]
        ind_y = lmlist[8][1]
        mid_x = lmlist[12][0]
        mid_y = lmlist[12][1]
        fingers = detector.fingersUp(hands[0])
        print(fingers)
        # array[0,1,1,1,1] (all open) [thump,index,middle, ring, little]
        # Fingers are represented as binary values, where 0 indicates a closed finger and 1 indicates an open finger, except for the thumb. For the thumb, 0 represents an open position, and 1 represents a closed position

        # mouse movement
        if fingers [0] == 0 and fingers[1] == 1 and fingers[2] == 0:
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255,255), 2)
            conv_x = int(np.interp(ind_x, (frameR, cam_w - frameR), (0, 1536)))
            conv_y = int(np.interp(ind_y, (frameR, cam_h - frameR), (0, 863)))
            mouse.move(conv_x, conv_y)

        # mouse button clicks
        if fingers [0] == 0 and fingers[1] == 1 and fingers[2] == 1 :
            if abs(ind_x-mid_x) < 25:

                # left click
                if l_delay == 0 and fingers[4] == 0:
                    mouse.click(button="left")
                    l_delay = 1
                    l_clk_thread.start()
                
                # right click
                if r_delay == 0 and fingers[4] == 1:
                    mouse.click(button="right")
                    r_delay = 1
                    r_clk_thread.start()
        
        # mouse scrolling
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[4] == 0: 
            if abs(ind_x-mid_x) < 25:
                mouse.wheel(delta=-1)
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[4] == 1: 
            if abs(ind_x-mid_x) < 25:
                mouse.wheel(delta=1)

        # double click
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 0 and double_delay == 0:
            mouse.double_click(button="left")
            double_delay = 1
            double_clk_thread.start()

        # close all fingers to close program  
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            break

    cv2.imshow("Camera",img)
    cv2.waitKey(1)
