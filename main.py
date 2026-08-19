import pyautogui as pag #to read pixel color
import time
import requests
import os
from dotenv import load_dotenv
import sys
import threading
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout
)

status = None

load_dotenv() #loads variables from our .env file
#we use .env files to store sensitive information like our webhook url so we don't upload it to github by accident!
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
USER_ID = os.getenv("DISCORD_USER_ID")
#we access the .env variables using os.getenv("VARIABLE_NAME")

def color_matches(pixel_color, target_color, tolerance):
    return (
        abs(pixel_color[0] - target_color[0]) <= tolerance
        and abs(pixel_color[1] - target_color[1]) <= tolerance
        and abs(pixel_color[2] - target_color[2]) <= tolerance
    )


def send_discord_noti(webhook_url, user_id):
    timestamp = int(time.time())
    data = {
        "content": f"MATCH FOUND! <t:{timestamp}:R> <@{user_id}>" # <-- message sent on discord
    }
       
    requests.post(webhook_url, json=data) #.post essentially sends a message to the webhook url with the data we specified above


def queue_monitor(webhook_url, user_id):
    match_found = False
    global status

    while match_found == False: #while we haven't found a match, keep checking the pixel color
        pixel_color = pag.pixel(946, 37)

        if color_matches(pixel_color, (147, 255, 0), 20):
            print("Match found!", pixel_color)

            send_discord_noti(webhook_url, user_id)

            match_found = True
            status = "Match found"
            time.sleep(3)
            status = "Idle"

        elif color_matches(pixel_color, (62, 42, 32), 20):
            print("In queue!", pixel_color)

            status = "In queue"

        else:
            print("Error! OW is not focused or your pixel selection is incorrect.", pixel_color)

            status = "Error"

        time.sleep(0.5)


class QueueDetectorGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Overwatch Queue Detector")
        self.setFixedSize(400, 250)

        # Discord user ID input
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Discord User ID")

        # Put .env user ID in the box if we have one
        if USER_ID:
            self.user_id_input.setText(USER_ID)

        # Discord webhook input
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("Discord Webhook URL")

        # Put .env webhook in the box if we have one
        if WEBHOOK_URL:
            self.webhook_input.setText(WEBHOOK_URL)

        # Start button
        self.start_button = QPushButton("Start Detector")
        self.start_button.clicked.connect(self.start_detector)

        # Current detector status
        self.status_label = QLabel("Status: Idle")

        # Put everything vertically in the window
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Discord User ID"))
        layout.addWidget(self.user_id_input)

        layout.addWidget(QLabel("Webhook URL"))
        layout.addWidget(self.webhook_input)

        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(
            self.update_status
        )
        self.status_timer.start(1000)


    def start_detector(self):
        

        user_id = self.user_id_input.text()
        webhook_url = self.webhook_input.text()

        print("User ID:", user_id)
        print("Webhook:", webhook_url)

        self.status_label.setText("Status: Monitoring")

        # Stop users from starting multiple monitors
        self.start_button.setEnabled(False)

        # Run the queue monitor in another thread
        self.monitor_thread = threading.Thread(
            target=queue_monitor,
            args=(webhook_url, user_id),
            daemon=True
        )

        self.monitor_thread.start()

    def update_status(self):
        global status
        self.status_label.setText(
            f"Status: {status}"
        )
        # If the monitor thread has finished, enable Start again
        if hasattr(self, "monitor_thread"):
            if self.monitor_thread.is_alive() == False:
                self.start_button.setEnabled(True)


app = QApplication(sys.argv)
window = QueueDetectorGUI()
window.show()
sys.exit(app.exec())