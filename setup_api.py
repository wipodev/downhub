from cx_Freeze import setup, Executable

build_options = {
    "packages": ["os", "sys", "fastapi", "yt_dlp", "uvicorn"],
    "excludes": ["tkinter"],
    "include_files": [
      ("api/bin/ffmpeg.exe", "bin/ffmpeg.exe"),
      ("api/bin/ffprobe.exe", "bin/ffprobe.exe"),
    ],
}

executables = [
    Executable(
        script="api/main.py",
        target_name="DownloadService.exe",
        icon="assets/icon.ico",
        base="win32gui",
    )
]

setup(
    name="DownloadService",
    version="0.0.2",
    description="YouTube video download service",
    options={"build_exe": build_options},
    executables=executables,
)
