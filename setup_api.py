from cx_Freeze import setup, Executable

build_options = {
    "packages": ["os", "sys", "fastapi", "yt_dlp", "uvicorn", "tkinter", "requests"],
    "excludes": [],
    "include_files": [
        ("api/bin/ffmpeg.exe", "bin/ffmpeg.exe"),
        ("api/bin/ffprobe.exe", "bin/ffprobe.exe"),
    ],
}

executables = [
    Executable(
        script="api/main.py",
        target_name="DownHubService.exe",
        icon="assets/icon_service.ico",
        base="win32gui",
    ),
    Executable(
        script="api/gui.py",
        target_name="DownHubGUI.exe",
        icon="assets/icon_gui.ico",
        base="win32gui",
    )
]

setup(
    name="DownHubTools",
    version="0.0.3",
    description="DownHub video download service",
    options={"build_exe": build_options},
    executables=executables,
)
