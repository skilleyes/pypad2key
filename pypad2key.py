from inputs import get_gamepad
#from pynput.keyboard import Key, Controller

#keyboard = Controller()

import win32api
import win32con

import ctypes
import time

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

z_pressed = False

while 1:
    events = get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)
        if (event.ev_type == 'Key' and event.code == 'BTN_SOUTH'):
            if (event.state == 1):
                print('A pressed')
                #keyboard.press('A')
            else:
                print('A released')
                #keyboard.release('A')

        if (event.ev_type == 'Absolute' and event.code == 'ABS_RZ'):
            if (event.state > 30 and z_pressed == False):
                print('Z pressed')
                #keyboard.press('z')
                #win32api.keybd_event(0x5A, 0, 0, 0)
                PressKey(0x11)
                z_pressed = True
            elif (event.state <= 30 and z_pressed == True):
                print('Z released')
                #keyboard.release('z')
                #win32api.keybd_event(0x5A, 0, 2, 0)                             
                ReleaseKey(0x11)
                z_pressed = False
