# 📥 DownHub: Professional Native Video Downloader

**DownHub** is an advanced and minimalist solution for high-quality video downloading. Unlike conventional browser extensions, it uses a **Chrome Native Messaging** architecture to communicate directly with a native Python host, enabling robust, efficient download management without the limitations of the browser environment.

## ✨ Key Features

- **Native Architecture:** High-performance, bidirectional communication between the Chrome extension and the operating system via the native messaging protocol.
- **Powerful Engine:** Uses the `yt-dlp` binary to ensure compatibility with the latest video algorithms and enable high-speed downloads.
- **Multi-Platform Support:** Dynamic adaptation of the interface and download buttons for:
  - **YouTube**
  - **Kick**
  - **Twitch**
- **Intelligent Process Management:** One-click cancellation system that safely terminates the entire process tree (including FFmpeg) and automatically cleans up temporary files (`.part`).
- **Minimalist Interface:** A clean, modern design that seamlessly integrates into each website’s DOM, including visual progress indicators.

## 🛠️ Project Structure

```text
downhub/
├── extension/          # Extension source code (JS, CSS, Manifest)
├── src/                # Native Python host
├── assets/             # Visual assets and icons
├── bin/                # External binaries (yt-dlp, ffmpeg)
├── build.py            # Build automation script
├── extension_key.py    # Extension ID and key generator
└── setup.iss           # Installer creation script (Inno Setup)
```

## 🚀 Installation & Deployment

### Prerequisites

- Python 3.x
- Google Chrome (or Chromium-based browsers)
- Inno Setup 6 (optional, for generating the `.exe` installer)

### Step 1: Extension Setup

1. Run `extension_key.py` to generate a unique ID for your extension and link it to the native host.
2. Load the `extension/` folder in Chrome via `chrome://extensions` with Developer Mode enabled.

### Step 2: Native Host Build

Run the build script to generate the service executable:

```bash
python build.py --keys
```

### Step 3: System Registration

For Chrome to recognize the host, the JSON manifest must be registered in the Windows registry:

1. Use the installer generated with `build.py --inno`, or
2. Manually apply the `install_host.reg` file.

## 🔧 Technical Details

### Communication Protocol

The native host (`native_host.py`) uses a binary packet structure to handle message lengths, preventing common buffer overflow issues in Chrome’s `stdio` communication.

### Cancellation Handling

When a user cancels a download, the system executes a `taskkill` command with the `/T` flag to ensure that the main `yt-dlp` process and its child encoding processes (FFmpeg) are instantly terminated, releasing file locks for cleanup.

## ⚖️ License

This project is licensed under the **Apache License 2.0**. See the `LICENSE` file for more details.

---

Developed by **WipoDev**.
