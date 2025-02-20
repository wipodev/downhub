# DownTube

DownTube is a project that combines a Python backend and a Chrome extension to download YouTube videos directly from their webpage. This repository provides the necessary tools to use the extension or develop custom modifications.

---

## Repository Structure

```plaintext
└── downtube
    └── api                   # Backend to handle downloads
        └── __init__.py
        └── main.py           # FastAPI server for download requests
    └── extension             # Chrome extension code
        └── icons
        └── background.js     # Background event logic
        └── content.js        # Logic for interacting with YouTube
        └── manifest.json     # Extension configuration
        └── style.css         # User interface styling
    └── .gitignore
    └── build.py              # Script to compile the API and create the installer
    └── README.md
    └── requirements.txt
    └── setup_api.py          # Configuration to compile the backend into an executable
    └── setup_ext.py          # Configuration to compile the backend into an executable
    └── setup_installer.iss   # Inno Setup script for creating a Windows installer
    └── structure.md
```

---

## Requirements

### API

- Python 3.9+
- Python dependencies (installable via pip):
  - `fastapi`
  - `yt-dlp`
  - `uvicorn`
  - `pydantic`
- Windows operating system (for the installer)
- ffmpeg.exe (add it to the `api/bin` folder)
- ffprobe.exe (add it to the `api/bin` folder)

### Chrome Extension

- Google Chrome browser

---

## Installation

### Step 1: Install the Backend

1. Clone this repository:

   ```bash
   git clone https://github.com/wipodev/downtube.git
   cd downtube
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Optional: Build an executable with `setup_api.py`:

   ```bash
   python setup_api.py build
   ```

4. Run the backend:

   ```bash
   python api/main.py
   ```

The server will run on `http://127.0.0.1:8000`.

---

### Step 2: Set Up the Chrome Extension

1. Open Google Chrome and go to `chrome://extensions`.
2. Enable Developer Mode.
3. Click on "Load unpacked extension".
4. Select the `extension` folder within the cloned repository.

Once installed, the extension will be active on YouTube pages.

---

## Usage

1. Open any video on YouTube.
2. You will see a new button with the extension icon in the video control menu.
3. Click the button to start the download.
4. The video will be saved to your system's downloads folder.

---

## Development and Customization

### API

The `api/main.py` file defines the backend handling download requests. You can customize the `yt-dlp` options in the `ydl_opts` variable.

### Extension

- **background.js**: Handles global events, such as tab URL changes.
- **content.js**: Defines the page interaction logic on YouTube. Modify the `injectDownloadButton` function to customize the download button.
- **style.css**: Adjust the styling of the notifications.

---

## Building

### Create a Windows Installer

1. Ensure Inno Setup is installed.
2. Run the `build.py` script:
   ```bash
   python build.py
   ```
3. The installer will be generated in the `Output` folder.

---

## License

This project is distributed under the MIT license.

## Disclaimer

This project is not affiliated, endorsed, or associated with YouTube or Google in any way. It is provided solely for educational and learning purposes. Misuse of this tool to download content without authorization may violate YouTube's terms of service. The author is not responsible for any use of this software.

If you choose to use this project, ensure that you comply with all copyright laws and YouTube's terms of service.
