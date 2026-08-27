# Overwatch Queue Monitor

A lightweight Windows app that detects when your Overwatch queue pops and sends a Discord notification to your phone.

Built so I can leave my computer while I'm in queue without missing the start of my match.

For more details on how I built it and why it exists, read the full project write-up on [my website]([https://luzniak.dev/](https://luzniak.dev/blog/ow-queue-monitor)).

## Download

**[Download the latest Windows release](https://github.com/beatopia/ow-queue-monitor/releases/latest)**

Download `Overwatch.Queue.Monitor.exe` from the **Assets** section and run it.

No Python installation is required.

> Windows may show a SmartScreen warning because the executable is not code-signed.

## How to Use

1. Open Overwatch in **fullscreen**.
2. Open `Overwatch.Queue.Monitor.exe`.
3. Enter your Discord user ID and webhook URL.
4. Start the queue monitor.
5. Queue for a game.
6. Get a Discord notification when your match is found.

The monitor automatically stops after detecting a match.

## Discord Setup

You'll need:

* Your Discord user ID
* A Discord webhook URL

To create a webhook:

1. Open the Discord channel you want notifications sent to.
2. Go to **Edit Channel → Integrations → Webhooks**.
3. Create a webhook.
4. Copy its URL into the app.

To copy your Discord user ID, enable **Developer Mode** in Discord and right-click your account → **Copy User ID**.

Keep your webhook URL private. Anyone with the URL can send messages through it.

## Notes

* Windows only
* Overwatch must be visible in fullscreen
* Detection may not work correctly on unsupported resolutions or UI layouts

## Running From Source

```bash
git clone https://github.com/beatopia/ow-queue-monitor.git
cd ow-queue-monitor
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python main.py
```

