import pyautogui as pag #to read pixel color
import time
import requests
import os
from dotenv import load_dotenv

status = None
load_dotenv() #loads variables from our .env file
#we use .env files to store sensitive information like our webhook url so we don't upload it to github by accident!
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
#we access the .env variables using os.getenv("VARIABLE_NAME")

def send_discord_noti():
    data = {
        "content": "Match found!", # <-- message that will be sent on discord
    }
    requests.post(WEBHOOK_URL, json=data)

def queue_monitor():
    match_found = False
    global status
    while match_found == False:
        pixel_color = pag.pixel(950, 20)
        if pixel_color == (140, 229, 0):
            print("Match found!", pixel_color)
            send_discord_noti()
            match_found = True
            status = "Match found"
        elif pixel_color == (81, 43, 39):
            print("In queue!", pixel_color)
            status = "In queue"
        else:
            print("Something is wrong! OW is not focused or your pixel selection is incorrect.")
            status = "Error"
        time.sleep(1)


queue_monitor()