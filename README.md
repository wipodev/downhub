# 📥 DownHub: Professional Native Video Downloader

**DownHub** is an advanced and minimalist solution for high-quality video downloading. Unlike conventional browser extensions, it uses a **Chrome Native Messaging** architecture to communicate directly with a natively compiled host (built with Nuitka), enabling robust, efficient download management without the limitations of the browser environment.

## ✨ Key Features

- **Native Architecture:** High-performance, bidirectional communication between the Chrome extension and the operating system via the native messaging protocol.
- **Powerful Engine:** Uses `yt-dlp`, `ffmpeg`, and the `deno` JavaScript runtime to ensure full compatibility with the latest video streams and enable high-speed downloads.
- **Multi-Platform Support:** Dynamic adaptation of the interface and download buttons for:
  - **YouTube**
  - **Kick**
  - **Twitch**
- **Automatic Updates:** Built-in self-updating mechanism for both the native host (`wipodev/updater`) and `yt-dlp`.
- **Intelligent Process Management:** One-click cancellation system that safely terminates the entire process tree (including FFmpeg) and automatically cleans up temporary files (`.part`).
- **Minimalist Interface:** A clean, modern design that seamlessly integrates into each website’s DOM, including visual progress indicators.

## 🛠️ Project Structure

```text
downhub/
├── extension/          # Extension source code (JS, CSS, Manifest)
├── src/                # Modular native host source (Nuitka compiled)
│   ├── native_host.py  # Main entry point and download orchestration
│   ├── config.py       # Paths, version metadata, and logging setup
│   ├── messaging.py    # Chrome Native Messaging stdio binary protocol
│   └── app_updater.py  # Self-update integration via wipodev/updater
├── assets/             # Visual assets and icons
├── bin/                # Bundled runtimes (yt-dlp, ffmpeg, deno)
├── build.py            # Automated Nuitka & Inno Setup build script
├── extension_key.py    # Extension ID and key generator
├── VERSION             # Single source of truth for native host version
└── setup.iss           # Windows installer script (Inno Setup)
```

## 🚀 Installation & Deployment

### End Users (Recommended)

Download the latest signed Windows installer (`DownHub_Installer.exe`) directly from the [GitHub Releases](https://github.com/wipodev/downhub/releases) page and run it.

### Building from Source

#### Prerequisites

- Python 3.11+
- C Compiler (MSVC / Visual Studio Build Tools or MinGW64 for Nuitka)
- Python packages: `nuitka`, `pillow`, and `updater` (`git+https://github.com/wipodev/updater.git`)
- Google Chrome (or Chromium-based browsers)
- Inno Setup 6 (optional, for generating the `.exe` installer)

#### Step 1: Extension & Host Build

Run the automated build script to generate the extension key, compile `DownHubService.exe` natively with Nuitka, and package the installer:

```bash
python build.py --keys --ext --inno

```

#### Step 2: Extension & System Registration

1. Load the `extension/` folder in Chrome via `chrome://extensions` with Developer Mode enabled (or use the packaged release).
2. Run the installer generated in `dist/` to register the Native Messaging Host manifest in the Windows Registry.

## 🔧 Technical Details

### Communication Protocol

The native host (`src/messaging.py`) uses a 32-bit unsigned integer binary header to frame JSON payloads over `stdin`/`stdout`, preventing buffer overflows or stream corruption in Chrome’s `stdio` communication.

### Cancellation Handling

When a user cancels a download, the system executes a `taskkill` command with the `/T` flag to ensure that the main `yt-dlp` process and its child encoding processes (`ffmpeg`) are instantly terminated, releasing file locks for cleanup.

## 🔐 Code Signing & Security Policy

Free code signing provided by [SignPath.io](https://signpath.io/), certificate by [SignPath Foundation](https://signpath.org/).
For details on build provenance, release approvals, privacy, and vulnerability reporting, see [SECURITY.md](SECURITY.md).

## ⚖️ License

This project is licensed under the **Apache License 2.0**. See the `LICENSE` file for more details.

---

Developed by **WipoDev**.
