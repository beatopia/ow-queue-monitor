import pyautogui as pag
import time

while 1:
    pixel_color = pag.pixel(950, 20)
    if pixel_color == (140, 229, 0):
        print("Match found!", pixel_color)
    elif pixel_color == (81, 43, 39):
        print("In queue!", pixel_color)
    else:
        print("Something is wrong! OW is not focused or your pixel selection is incorrect.")
    time.sleep(1)
