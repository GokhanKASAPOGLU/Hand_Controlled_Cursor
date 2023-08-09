# Import required libraries
import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import numpy as np
import threading
import time

# Create a hand detector object with specific parameters
detector = HandDetector(detectionCon=0.9, maxHands=1)

# Initialize the webcam capture with specified dimensions
# 1 external webcam | 0 system webcam 
cap = cv2.VideoCapture(0)
cam_w = 640
cam_h = 480
cap.set(3, cam_w)
cap.set(4, cam_h)

# Define a margin to prevent cursor from going off the screen edges
frameR = 100

# Initialize delay variables for left, right, and double clicks
l_delay = 0
r_delay = 0
double_delay = 0

# Functions to reset click delays
def l_clk_delay():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay = 0
    l_clk_thread = threading.Thread(target=l_clk_delay)

def r_clk_delay():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target=r_clk_delay)

def double_clk_delay():
    global double_delay
    global double_clk_thread
    time.sleep(2)
    double_delay = 0
    double_clk_thread = threading.Thread(target=double_clk_delay)

# Initialize thread objects for click delay functions
l_clk_thread = threading.Thread(target=l_clk_delay)
r_clk_thread = threading.Thread(target=r_clk_delay)
double_clk_thread = threading.Thread(target=double_clk_delay)

# Main loop
while True:
    # Capture frame from the webcam
    success, img = cap.read()
    img = cv2.flip(img, 1)
    
    # Detect hands in the frame
    hands, img = detector.findHands(img, flipType=False)
    
    # Draw a rectangle to indicate the active area for hand tracking
    cv2.rectangle(img, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2 )
    
    if hands:
        lmlist = hands[0]['lmList']
        ind_x = lmlist[8][0]
        ind_y = lmlist[8][1]
        mid_x = lmlist[12][0]
        mid_y = lmlist[12][1]
        fingers = detector.fingersUp(hands[0])
        print(fingers)
        
        # array[0,1,1,1,1] (all open) [thump, index, middle, ring, little]
        # Fingers are represented as binary values, where 0 indicates a closed finger and 1 indicates an open finger.
        # Except for the thumb. For the thumb, 0 represents an open position, and 1 represents a closed position

        # Handle mouse movement
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0:
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255, 255), 2)
            conv_x = int(np.interp(ind_x, (frameR, cam_w - frameR), (0, 1536)))
            conv_y = int(np.interp(ind_y, (frameR, cam_h - frameR), (0, 863)))
            mouse.move(conv_x, conv_y)

        # Handle mouse button clicks
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1:
            if abs(ind_x - mid_x) < 25:
                
                # Left click
                if l_delay == 0 and fingers[4] == 0:
                    mouse.click(button="left")
                    l_delay = 1
                    l_clk_thread.start()

                # Right click
                if r_delay == 0 and fingers[4] == 1:
                    mouse.click(button="right")
                    r_delay = 1
                    r_clk_thread.start()

        # Handle mouse scrolling
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[4] == 0:
            if abs(ind_x - mid_x) < 25:
                mouse.wheel(delta=-1)
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[4] == 1:
            if abs(ind_x - mid_x) < 25:
                mouse.wheel(delta=1)

        # Handle double click
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 0 and double_delay == 0:
            mouse.double_click(button="left")
            double_delay = 1
            double_clk_thread.start()

        # Close all fingers to exit the program
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            break

    # Display the image with annotations
    cv2.imshow("Camera", img)
    cv2.waitKey(1)
