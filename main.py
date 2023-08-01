# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 13:36:02 2023

@author: ahmed
"""
from kivy.app import App
#from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.clock import Clock
#from kivy.graphics import Rectangle
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button

import mediapipe as mp
import cv2

import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui
import math

import time
import threading
import tkinter as tk
import pyperclip

wCam, hCam = pyautogui.size()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
pyautogui.FAILSAFE = False

class HandApp(App):
    def build(self):
        self.hand_widget = HandWidget()
        Clock.schedule_interval(self.hand_widget.update, 1.0 / 30)
        return self.hand_widget

    def on_stop(self):
        self.hand_widget.cap.release()
        cv2.destroyAllWindows()
        print("App stopped")

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=int(0.5), trackCon=0.5, model_complexity=1.0):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.model_complexity = model_complexity

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
                    
    def findPosition(self, img, hand='right', draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            if hand == 'right':
                myHand = self.results.multi_hand_landmarks[0]
            else:
                myHand = self.results.multi_hand_landmarks[1]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)

                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                    xmin, xmax = min(xList), max(xList)
                    ymin, ymax = min(yList), max(yList)
                    bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                              (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)

        return self.lmList, bbox

    def leftFingersUp(self):
        leftFingers = []
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                handIndex = self.results.multi_hand_landmarks.index(
                    hand_landmarks)
                handLabel = self.results.multi_handedness[handIndex].classification[0].label
                handLandmarks = []

                for landmarks in hand_landmarks.landmark:
                    handLandmarks.append([landmarks.x, landmarks.y])

                if handLabel == "Left":
                    if handLandmarks[4][0] > handLandmarks[3][0]:
                        leftFingers.append(1)
                    else:
                        leftFingers.append(0) 

                if handLandmarks[8][1] < handLandmarks[6][1]:
                    if handLabel == "Left":
                        leftFingers.append(1)
                else:
                    if handLabel == "Left":
                        leftFingers.append(0)

                if handLandmarks[12][1] < handLandmarks[10][1]:  
                    if handLabel == "Left":
                        leftFingers.append(1)
                else:
                    if handLabel == "Left":
                        leftFingers.append(0)

                if handLandmarks[16][1] < handLandmarks[14][1]:
                    if handLabel == "Left":
                        leftFingers.append(1)
                else:
                    if handLabel == "Left":
                        leftFingers.append(0)

                if handLandmarks[20][1] < handLandmarks[18][1]:
                    if handLabel == "Left":
                        leftFingers.append(1)
                else:
                    if handLabel == "Left":
                        leftFingers.append(0)

        return leftFingers

    def rightFingersUp(self):
        rightFingers = []
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                handIndex = self.results.multi_hand_landmarks.index(
                    hand_landmarks)
                handLabel = self.results.multi_handedness[handIndex].classification[0].label
                handLandmarks = []

                for landmarks in hand_landmarks.landmark:
                    handLandmarks.append([landmarks.x, landmarks.y])

                if handLabel == "Right":
                    if handLandmarks[4][0] < handLandmarks[3][0]:
                        rightFingers.append(1)
                    else:
                        rightFingers.append(0)

                if handLandmarks[8][1] < handLandmarks[6][1]: 
                    if handLabel == "Right":
                        rightFingers.append(1)
                else:
                    if handLabel == "Right":
                        rightFingers.append(0)

                if handLandmarks[12][1] < handLandmarks[10][1]: 
                    if handLabel == "Right":
                        rightFingers.append(1)
                else:
                    if handLabel == "Right":
                        rightFingers.append(0)

                if handLandmarks[16][1] < handLandmarks[14][1]:
                    if handLabel == "Right":
                        rightFingers.append(1)
                else:
                    if handLabel == "Right":
                        rightFingers.append(0)

                if handLandmarks[20][1] < handLandmarks[18][1]: 
                    if handLabel == "Right":
                        rightFingers.append(1)
                else:
                    if handLabel == "Right":
                        rightFingers.append(0)

        return rightFingers   

def openKeyboard(self):    
    root = tk.Tk()
    root.title("Virtual Keyboard")
    
    caps_on = False
    
    def on_key_press(key):
        nonlocal entry
        nonlocal caps_on
        
        if key == 'CapsLock':
            caps_on = not caps_on
            return
        
        if key == 'BackSpace':
            entry.delete(len(entry.get())-1, tk.END)
        elif key == 'Return':
            pyperclip.copy(entry.get())
            root.destroy()
        else:
            if caps_on:
                key = key.upper()
            entry.insert(tk.END, key)
        
    keyboardFrame = tk.Frame(root)
    keyboardFrame.pack(padx=10, pady=10)
    
    keys = [['!', '"', '£', '$', '5%', '^', '&', '*', '(', ')', '_', '+', '{', '}'],
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '[', ']'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', ':', ';', '@', '#'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '#', '<', '>', '?'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
            ['CapsLock', 'BackSpace', ' ','Return']]
    
    for row in keys:
        row_frame = tk.Frame(keyboardFrame)
        row_frame.pack(side=tk.TOP)
        for key in row:
            keyButton = tk.Button(row_frame, text=key, width=8, height=2, 
                                   command=lambda k=key: on_key_press(k))
            keyButton.pack(side=tk.LEFT, padx=2, pady=2)
    
    entryFrame = tk.Frame(root)
    entryFrame.pack(padx=10, pady=10)
    entry = tk.Entry(entryFrame, width=30)
    entry.pack(side=tk.LEFT)
    
    root.mainloop()

def switchTab(self):
    pyautogui.keyDown('alt')
    pyautogui.press('tab')
    
def enter(self):
    pyautogui.press('enter')
    
def paste(self):
    pyautogui.hotkey('ctrl', 'v')
    
def zoomIn(self):
    pyautogui.hotkey('ctrl', '+')

def zoomOut(self):
    pyautogui.hotkey('ctrl', '-')
    
def scrollUp(self):
    pyautogui.scroll(50)

def scrollDown(self):
    pyautogui.scroll(-50)
    
def volumeUp(self):
    currentVol = volume.GetMasterVolumeLevelScalar()
    newVol = min(1.0, currentVol + 0.01)
    volume.SetMasterVolumeLevelScalar(newVol, None)
    print(currentVol)

def volumeDown(self):
    currentVol = volume.GetMasterVolumeLevelScalar()
    if currentVol > 0.0:
        newVol = max(0.0, currentVol - 0.01)
        volume.SetMasterVolumeLevelScalar(newVol, None)
        print(currentVol)
    else:
        print("Volume is already at minimum.")

def brightnessUp(self):
    currentBrightness = sbc.get_brightness()[0]
    newBrightness = min(100, currentBrightness + 10)
    sbc.set_brightness(newBrightness)

def brightnessDown(self):
    currentBrightness = sbc.get_brightness()[0]
    newBrightness = max(0, currentBrightness - 10)
    sbc.set_brightness(newBrightness)

def moveMouse(self, index_x, index_y):
    index_x, index_y = self.lmList[8][1], self.lmList[8][2]
    index_x, index_y = index_x * 2, index_y * 2.5
    pyautogui.moveTo(wCam - index_x, index_y, duration = 0.1)

def clickCursor(self):
    pyautogui.click()

def rightClickCursor(self):
    pyautogui.click(button="right")

GESTURES = {
    (0, 0, 0, 0, 0): "None",
    (0, 0, 0, 0, 1): "Volume Down",
    (0, 0, 0, 1, 0): "None",
    (0, 0, 0, 1, 1): "Volume Up",
    (0, 0, 1, 0, 0): "Right Click",
    (0, 0, 1, 0, 1): "None",
    (0, 0, 1, 1, 0): "None",
    (0, 0, 1, 1, 1): "None",
    (0, 1, 0, 0, 0): "Move Mouse",
    (0, 1, 0, 0, 1): "Switch Tab",
    (0, 1, 0, 1, 0): "None",
    (0, 1, 0, 1, 1): "None",
    (0, 1, 1, 0, 0): "Click",
    (0, 1, 1, 0, 1): "None",
    (0, 1, 1, 1, 0): "None",
    (0, 1, 1, 1, 1): "Open Keyboard",
    (1, 0, 0, 0, 0): "Brightness Down",
    (1, 0, 0, 0, 1): "Paste",
    (1, 0, 0, 1, 0): "None",
    (1, 0, 0, 1, 1): "None",
    (1, 0, 1, 0, 0): "None",
    (1, 0, 1, 0, 1): "None",
    (1, 0, 1, 1, 0): "None",
    (1, 0, 1, 1, 1): "None",
    (1, 1, 0, 0, 0): "Brightness Up",
    (1, 1, 0, 0, 1): "Zoom In",
    (1, 1, 0, 1, 0): "None",
    (1, 1, 0, 1, 1): "None",
    (1, 1, 1, 0, 0): "Scroll Down",
    (1, 1, 1, 0, 1): "Zoom Out",
    (1, 1, 1, 1, 0): "Scroll Up",
    (1, 1, 1, 1, 1): "Enter",
}

FUNCTIONS = {
    "Volume Up": volumeUp,
    "Volume Down": volumeDown,
    "Move Mouse": lambda hand_widget: moveMouse(hand_widget, hand_widget.lmList[8][1], hand_widget.lmList[8][2]),
    "Click": clickCursor,
    "Brightness Up": brightnessUp,
    "Brightness Down": brightnessDown,
    "Right Click": rightClickCursor,
    "Open Keyboard": openKeyboard,
    "Switch Tab": switchTab,
    "Paste": paste, 
    "Enter": enter,
    "Zoom In": zoomIn,
    "Zoom Out": zoomOut,
    "Scroll Up": scrollUp,
    "Scroll Down": scrollDown
    # "None": None
}

class HandWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector = handDetector()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)
        self.lmList = []
        self.running = True

        self.cols = 2
        self.rows = 1

        self.cameraWidget = Image(size_hint=(0.8, 1))
        self.add_widget(self.cameraWidget)

        self.buttonsLayout = GridLayout(cols=1, size_hint=(None, None), size=(200, 100))
        self.add_widget(self.buttonsLayout)

        self.functionsDropdown = DropDown()
        for functionName in FUNCTIONS.keys():
            button = Button(text=functionName, size_hint_y=None)
            button.bind(on_release=lambda btn: self.functionsDropdown.select(btn.text))
            self.functionsDropdown.add_widget(button)
        self.dropdownButton = Button(text="Select Functions",
                                      font_size="20sp",
                                      background_color=(1, 1, 1, 1),
                                      color=(1, 1, 1, 1),
                                      size_hint=(1, None),
                                      height=50)
        self.dropdownButton.bind(on_release=self.functionsDropdown.open)
        self.functionsDropdown.bind(on_select=self.onFunctionSelected)
        self.buttonsLayout.add_widget(self.dropdownButton)

        Window.bind(on_key_down=self.on_keyboard_down)

    def on_keyboard_down(self, window, key, *args):
        if key == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            HandApp.stop(self)
            self.running = False

    def onFunctionSelected(self, dropdown, functionName):
        gesture = tuple(self.detector.leftFingersUp())
        for g, fn in GESTURES.items():
            if fn == functionName and g != gesture:
                GESTURES[g] = "None"

        GESTURES[gesture] = functionName

    def update(self, dt):
        if not self.running:
            return
        
        success, img = self.cap.read()

        #imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img = self.detector.findHands(img)
        self.lmList, bbox = self.detector.findPosition(img, draw=True)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(
            size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.cameraWidget.texture = texture
        self.cameraWidget.size = (self.width, self.height/1.2)
        self.cameraWidget.pos = (self.x, self.y)
        success, img = self.cap.read()

        if len(self.lmList) != 0:
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            if 250 < area < 1000:
                leftFingers = self.detector.leftFingersUp()
                rightFingers = self.detector.rightFingersUp()

                print("Left Hand: " + str(leftFingers))
                print("Right Hand:" + str(rightFingers))
                
                leftGesture = tuple(self.detector.leftFingersUp())
                rightGesture = tuple(self.detector.rightFingersUp())

                leftFunctionName = GESTURES.get(leftGesture)
                rightFunctionName = GESTURES.get(rightGesture)

                if leftFunctionName and leftFunctionName.lower() != 'none':
                    leftFunction = FUNCTIONS.get(leftFunctionName)
                    if leftFunction:
                        self.leftThread = threading.Thread(target=leftFunction, args=(self,))
                        self.leftThread.start()

                        if leftFunctionName in ['Click', 'Right Click', 'Open Keyboard', 'Switch Tab', 'Paste', 'Enter', "Zoom In", "Zoom Out"]:
                            time.sleep(1)
                
                if rightFunctionName and rightFunctionName.lower() != 'none':
                    rightFunction = FUNCTIONS.get(rightFunctionName)
                    if rightFunction:
                        self.rightThread = threading.Thread(target=rightFunction, args=(self,))
                        self.rightThread.start()

                        if rightFunctionName in ['Click', 'Right Click', 'Open Keyboard', 'Switch Tab', 'Paste', 'Enter', "Zoom In", "Zoom Out"]:
                            time.sleep(1)

if __name__ == '__main__':
    HandApp().run()
