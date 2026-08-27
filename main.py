import pyautogui as pag #to read pixel colors from the screen
import time #gives us delay/sleep functions
import requests #allows us to send http web requests to discord
import os #lets us interact with the operating system and read env variables
from dotenv import load_dotenv, set_key #loads variables and lets us save variables to our .env file
import sys #gives us access to system-level arguments and exit functions
import threading #allows us to run the queue detector in the background without freezing the ui
from PyQt6.QtCore import Qt, QTimer #imports Qt constants for focus/policies and timer for ui updates
from PyQt6.QtWidgets import (
    QApplication, #manages the gui application lifecycle
    QWidget, #the base window widget
    QLabel, #used to display text on the screen
    QLineEdit, #a single-line text input field
    QPushButton, #a clickable button
    QVBoxLayout #stacks widgets on top of each other vertically
)

status = None #tracks the current detector status like 'In queue' or 'Match found'

load_dotenv() #loads variables from our .env file
#we use .env files to store sensitive information like our webhook url so we don't upload it to github by accident!
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
USER_ID = os.getenv("DISCORD_USER_ID")
#we access the .env variables using os.getenv("VARIABLE_NAME")

#checks if a pixel color is close enough to our target color within a small error tolerance
def color_matches(pixel_color, target_color, tolerance):
    return (
        abs(pixel_color[0] - target_color[0]) <= tolerance
        and abs(pixel_color[1] - target_color[1]) <= tolerance
        and abs(pixel_color[2] - target_color[2]) <= tolerance
    )


#sends a discord notification pinging the user when a match is found
def send_discord_noti(webhook_url, user_id):
    timestamp = int(time.time()) #get current unix timestamp for discord relative time formatting
    data = {
        "content": f"MATCH FOUND! <t:{timestamp}:R> <@{user_id}>" # <-- message sent on discord
    }
       
    requests.post(webhook_url, json=data) #.post essentially sends a message to the webhook url with the data we specified above


#this runs in a background thread and constantly checks the screen pixel color
def queue_monitor(webhook_url, user_id, stop_event):
    match_found = False
    global status

    while match_found == False and not stop_event.is_set(): #while we haven't found a match and haven't stopped, keep checking the pixel color
        pixel_color = pag.pixel(946, 37) #reads the rgb color of the pixel at coordinates (x=946, y=37)

        if color_matches(pixel_color, (147, 255, 0), 30): #green color means match was found!
            print("Match found!", pixel_color)

            send_discord_noti(webhook_url, user_id)

            match_found = True
            status = "Match found"
            stop_event.wait(3) #wait 3 seconds before resetting status so the user can see it
            if not stop_event.is_set():
                status = "Idle"

        elif color_matches(pixel_color, (62, 42, 32), 20): #queue banner color
            print("In queue!", pixel_color)

            status = "In queue"

        else: #any other color means overwatch isn't on the right screen or focused
            print("Error! OW is not focused or your pixel selection is incorrect.", pixel_color)

            status = "Error"

        #waits 0.5s before next check, but immediately stops if stop button was clicked
        if stop_event.wait(0.5):
            break


#our main application window
class QueueDetectorGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Overwatch Queue Detector")
        self.setFixedSize(400, 320) #set a fixed width and height for our window

        #take focus away from inputs on startup so text is not auto-highlighted
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        #discord user id text input box
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Discord User ID")

        #put .env user id in the box if we already have one saved
        if USER_ID:
            self.user_id_input.setText(USER_ID)
            self.user_id_input.deselect() #deselect so it isn't highlighted in blue on launch

        #discord webhook text input box
        self.webhook_input = QLineEdit()
        self.webhook_input.setPlaceholderText("Discord Webhook URL")

        #put .env webhook in the box if we already have one saved
        if WEBHOOK_URL:
            self.webhook_input.setText(WEBHOOK_URL)
            self.webhook_input.deselect() #deselect so it isn't highlighted in blue on launch

        #save button to manually save credentials to .env file
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        #start button to begin monitoring
        self.start_button = QPushButton("Start Detector")
        self.start_button.clicked.connect(self.start_detector)

        #stop button to cancel monitoring
        self.stop_button = QPushButton("Stop Detector")
        self.stop_button.clicked.connect(self.stop_detector)
        self.stop_button.setEnabled(False) #starts disabled until detector is actually running

        self.stop_event = None #will hold our threading event to signal the background loop to stop

        #current detector status display label
        self.status_label = QLabel("Status: Idle")

        #put everything vertically in the window from top to bottom
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Discord User ID"))
        layout.addWidget(self.user_id_input)

        layout.addWidget(QLabel("Webhook URL"))
        layout.addWidget(self.webhook_input)
        layout.addWidget(self.save_button)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        #timer that ticks every second to keep the status label in sync with background thread
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(
            self.update_status
        )
        self.status_timer.start(1000) #1000 ms = 1 second


    def save_settings(self):
        user_id = self.user_id_input.text()
        webhook_url = self.webhook_input.text()

        #manually save the inputs to our .env file
        set_key(".env", "DISCORD_USER_ID", user_id)
        set_key(".env", "DISCORD_WEBHOOK_URL", webhook_url)

        global status
        status = "Saved!"
        self.status_label.setText("Status: Saved!")

    def start_detector(self):
        user_id = self.user_id_input.text()
        webhook_url = self.webhook_input.text()

        print("User ID:", user_id)
        print("Webhook:", webhook_url)

        #automatically save what we typed into our .env file so we don't have to retype it next time!
        set_key(".env", "DISCORD_USER_ID", user_id)
        set_key(".env", "DISCORD_WEBHOOK_URL", webhook_url)

        self.status_label.setText("Status: Monitoring")

        #disable start and enable stop so user can't accidentally spam start
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.stop_event = threading.Event() #creates an event we can use to tell the thread to stop

        #run the queue monitor in a separate background thread so our gui window stays responsive
        self.monitor_thread = threading.Thread(
            target=queue_monitor,
            args=(webhook_url, user_id, self.stop_event),
            daemon=True #daemon thread automatically closes when the app is closed
        )

        self.monitor_thread.start()

    def stop_detector(self):
        #tell the background thread to stop its loop
        if self.stop_event:
            self.stop_event.set()

        global status
        status = "Idle"
        self.status_label.setText("Status: Idle")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_status(self):
        global status
        if status:
            self.status_label.setText(
                f"Status: {status}"
            )
        #if the monitor thread has finished running on its own, reset the buttons
        if hasattr(self, "monitor_thread"):
            if self.monitor_thread.is_alive() == False:
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)


#standard pyqt setup to initialize and run the app
app = QApplication(sys.argv)
window = QueueDetectorGUI()
window.show() #opens the window on your screen
sys.exit(app.exec()) #keeps the app running until the user closes it