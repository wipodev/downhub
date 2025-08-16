# DownHub

DownHub is an application that bundles a **Python FastAPI backend**, a **local Tkinter GUI**, and a **Chrome extension** to download videos seamlessly from multiple platforms.

Initially created for **YouTube**, it now supports **Kick**, and since it uses `yt-dlp`, you can also download from most other video sites by pasting the URL into the GUI.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Building](#building)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## Overview

DownHub runs a **local background service (DownHubService.exe)** that listens for download requests. A **GUI client** allows pasting any video URL, and a **Chrome extension** injects a download button into YouTube and Kick video players.

All downloaded files are automatically saved to the user’s **Downloads** folder, with audio and video streams merged via **FFmpeg**.

---

## Features

- One‑click download directly from **YouTube** and **Kick** players.
- GUI to paste and download from any `yt-dlp` supported site.
- Background FastAPI service exposing `/download` and `/status` endpoints.
- Task management with progress and error reporting.
- GUI with clipboard paste and real‑time logs.
- Chrome extension with custom button injection and toast notifications.
- Bundled **FFmpeg/ffprobe** executables for processing.
- Windows installer built with **Inno Setup**.

---

## How It Works

1. **Chrome extension** injects a Download button into the video player (YouTube/Kick).
2. Clicking the button sends the video URL to the local FastAPI backend.
3. Backend spawns a `yt-dlp` job that downloads video+audio and merges them to MP4.
4. Progress and status updates are exposed at `/status/<task_id>`.
5. GUI can trigger the same `/download` endpoint by pasting URLs manually.
6. Once finished, the file is placed in the user’s **Downloads** directory.

---

## Architecture

- **Backend (**``**)**: FastAPI + `yt-dlp` job manager with task tracking.
- **GUI (**``**)**: Tkinter app for pasting URLs and viewing logs.
- **Extension (**``**)**: Manifest v3 extension that injects buttons and sends requests to backend.
- **Build system**: `setup_api.py` (cx_Freeze) compiles backend/GUI, `setup_installer.iss` builds Windows installer.

---

## Project Structure

```
└── downtube
    └── api
        └── main.py        # FastAPI backend service
        └── gui.py         # Tkinter GUI
        └── bin/           # ffmpeg + ffprobe executables
    └── extension
        └── content.js     # Injects buttons into players
        └── background.js  # Forwards requests to backend
        └── manifest.json  # Chrome extension manifest (MV3)
        └── toast.css      # Notification styles
    └── assets             # Icons
    └── build.py           # Build pipeline
    └── run_all.py         # Runs backend + GUI for dev
    └── setup_api.py       # cx_Freeze build config
    └── setup_installer.iss# Inno Setup installer script
```

---

## Requirements

### API / GUI

- Python 3.9+
- Dependencies: `fastapi`, `yt-dlp`, `uvicorn`, `pydantic`, `tkinter`, `requests`
- Windows OS (installer provided)
- `ffmpeg.exe` and `ffprobe.exe` (bundled in `api/bin`)

### Chrome Extension

- **Google Chrome** (Manifest v3 support)

---

## Installation

### Step 1 — Backend + GUI

1. Clone repository:

   ```bash
   git clone https://github.com/wipodev/downhub.git
   cd downhub
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend:

   ```bash
   python api/main.py
   ```

   Runs at `http://127.0.0.1:8000`.

4. Optionally start the GUI:

   ```bash
   python api/gui.py
   ```

### Step 2 — Chrome Extension

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `extension/` folder

---

## Usage

### From Chrome Extension

- Open a YouTube or Kick video.
- A **Download button** appears.
- Click to start; video saves to **Downloads** folder.

### From GUI

- Run **DownHubGUI.exe** (or `python api/gui.py`).
- Paste any supported URL.
- Click **Download** → file saved in **Downloads**.

---

## Building

### Windows Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Run build script:
   ```bash
   python build.py
   ```
3. Installer will appear in `Output/`.

---

## License

This project is licensed under the **MIT License**.

---

## Disclaimer

This project is **not affiliated with YouTube, Kick, or Google**. It is intended for educational purposes only. Downloading copyrighted content without authorization may violate terms of service. The author assumes no responsibility for misuse.
