from inputs import get_gamepad
from threading import Thread
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

class PWM(Thread):
    def __init__(self, keyScanCode):
        Thread.__init__(self)
        self.keyScanCode = keyScanCode
        self.stop = False
        self.percentage = 0.0
        self.period = 0.1

    def stopPWM(self):
        self.stop = True

    # percentage between 0 and 1
    def setPercentage(self, percentage):
        if (percentage > 1.0):
            self.percentage = 1.0
        elif (percentage < 0.0):
            self.percentage = 0.0
        else: 
            self.percentage = percentage

    def run(self):
        while (self.stop != True):
            PressKey(self.keyScanCode)
            time.sleep(self.period * self.percentage)
            ReleaseKey(self.keyScanCode)
            time.sleep(self.period * (1 - self.percentage))
            
deadzone_x = 500
sensitivity_x = 1.4
z_pressed = False
s_pressed = False
turn_right_pwm = None
turn_left_pwm = None
dpad_up_pressed = False
dpad_down_pressed = False
dpad_left_pressed = False
dpad_right_pressed = False

while 1:
    events = get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)

        # Handbrake button TR
        if (event.ev_type == 'Key' and event.code == 'BTN_TR'):
            if (event.state == 1):
                print('Space pressed')
                PressKey(0x39)
            else:
                print('Space released')
                ReleaseKey(0x39)

        # Camera button BTN_THUMBR
        if (event.ev_type == 'Key' and event.code == 'BTN_THUMBR'):
            if (event.state == 1):
                print('C pressed')
                PressKey(0x2E)
            else:
                print('C released')
                ReleaseKey(0x2E)

        # Dpad actionnables
        if (event.ev_type == 'Absolute' and event.code == 'ABS_HAT0Y'):
            if (event.state == -1):
                print('Ddap up pressed')
                PressKey(0x02)
                dpad_up_pressed = True
            elif (event.state == 1):
                print('Ddap down pressed')
                PressKey(0x04)
                dpad_down_pressed = True
            else:
                if (dpad_up_pressed):
                    print('Ddap up released')
                    ReleaseKey(0x02)
                    dpad_up_pressed = False
                if (dpad_down_pressed):
                    print('Ddap down released')
                    ReleaseKey(0x04)
                    dpad_down_pressed = False

        if (event.ev_type == 'Absolute' and event.code == 'ABS_HAT0X'):
            if (event.state == -1):
                print('Dpad left pressed')
                PressKey(0x05)
                dpad_left_pressed = True
            elif (event.state == 1):
                print('Dpad right pressed')
                PressKey(0x03)
                dpad_right_pressed = True
            else:
                if (dpad_left_pressed):
                    print('Dpad left released')
                    ReleaseKey(0x05)
                    dpad_left_pressed = False
                if (dpad_right_pressed):
                    print('Dpad right released')
                    ReleaseKey(0x03)
                    dpad_right_pressed = False

        # Right trigger
        if (event.ev_type == 'Absolute' and event.code == 'ABS_RZ'):
            if (event.state > 30 and z_pressed == False):
                print('Z pressed')
                PressKey(0x11)
                z_pressed = True
            elif (event.state <= 30 and z_pressed == True):
                print('Z released')                      
                ReleaseKey(0x11)
                z_pressed = False

        # Left trigger
        if (event.ev_type == 'Absolute' and event.code == 'ABS_Z'):
            if (event.state > 30 and s_pressed == False):
                print('S pressed')
                PressKey(0x1F)
                s_pressed = True
            elif (event.state <= 30 and s_pressed == True):
                print('S released')                      
                ReleaseKey(0x1F)
                s_pressed = False

        # Left Analog X
        if (event.ev_type == 'Absolute' and event.code == "ABS_X"):
            # Turn right
            if (event.state > deadzone_x):
                if (turn_right_pwm == None):
                    print('Turning right')
                    turn_right_pwm = PWM(0x20)
                    turn_right_pwm.start()
                else:
                    print('updating right percentage')
                    turn_right_pwm.setPercentage((event.state - deadzone_x) / (32768 - deadzone_x) * sensitivity_x)
            if (event.state <= deadzone_x and turn_right_pwm != None):
                print('Stop turning right')
                turn_right_pwm.stopPWM()
                turn_right_pwm = None

            # Turn left    
            if (event.state < -deadzone_x):
                if (turn_left_pwm == None):
                    print('Turning left')
                    turn_left_pwm = PWM(0x1E)
                    turn_left_pwm.start()
                else:
                    print('updating left percentage')
                    turn_left_pwm.setPercentage((-event.state - deadzone_x) / (32768 - deadzone_x) * sensitivity_x)
            if (event.state >= -deadzone_x and turn_left_pwm != None):
                print('Stop turning left')
                turn_left_pwm.stopPWM()
                turn_left_pwm = None
            
