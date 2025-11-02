import random
import string
import os
import subprocess
import sys
import json
import urllib.request
import re
import base64
import datetime
import shutil
import sqlite3
import requests
import tempfile
import platform
import psutil
import cpuinfo
import GPUtil
import socket
import getpass
import threading
import time
import keyboard
import ctypes
import win32crypt
from Crypto.Cipher import AES
from pynput import mouse, keyboard as pynput_keyboard

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

MOUSE_DOWN_FLAGS = {
    mouse.Button.left: 0x0002,
    mouse.Button.right: 0x0008,
    mouse.Button.middle: 0x0020,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}
MOUSE_UP_FLAGS = {
    mouse.Button.left: 0x0004,
    mouse.Button.right: 0x0010,
    mouse.Button.middle: 0x0040,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}

def send_click(button):
    down = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_DOWN_FLAGS[button], 0, None))
    up = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_UP_FLAGS[button], 0, None))
    ctypes.windll.user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(down))
    ctypes.windll.user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(up))

def detect_trigger():
    trigger_key = None
    trigger_type = None

    def on_mouse_click(x, y, button, pressed):
        nonlocal trigger_key, trigger_type
        if pressed and trigger_key is None:
            trigger_key = "button"
            trigger_type = "mouse"
            return False

    def on_key_press(key):
        nonlocal trigger_key, trigger_type
        if trigger_key is None:
            trigger_key = key
            trigger_type = "keyboard"
            return False

    print("Press any key or mouse button to set your trigger...")

    with mouse.Listener(on_click=on_mouse_click) as mouse_listener, \
         pynput_keyboard.Listener(on_press=on_key_press) as keyboard_listener:

        while trigger_key is None:
            time.sleep(0.05)

    time.sleep(0.3)
    return trigger_key, trigger_type

trigger_key, trigger_type = detect_trigger()
cps = float(input("Clicks per second: "))
interval = 1 / cps
active_button = mouse.Button.left

try:
    pressed_keys = set()

    def on_key_press(key):
        pressed_keys.add(key)

    def on_key_release(key):
        pressed_keys.discard(key)

    key_listener = pynput_keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    key_listener.start()

    if trigger_type == "mouse":
        pressed_state = [False]

        def on_click(x, y, button, pressed):
            if button == trigger_key:
                pressed_state[0] = pressed

        with mouse.Listener(on_click=on_click) as listener:
            while True:
                if pressed_state[0]:
                    send_click(active_button)
                    time.sleep(interval)
                else:
                    time.sleep(0.01)
    else:
        while True:
            if trigger_key in pressed_keys:
                send_click(active_button)
                time.sleep(interval)
            else:
                time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    try:
        key_listener.stop()
    except:
        pass
