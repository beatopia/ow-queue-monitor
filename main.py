import pyautogui
import time

while 1:
    pixel_color = pyautogui.pixel(960, 100)
    print(pixel_color)
    time.sleep(1)