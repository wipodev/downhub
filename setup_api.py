from cx_Freeze import setup, Executable
import os

main_script = "api/main.py"

build_options = {
    "packages": ["os", "sys", "fastapi", "yt_dlp", "uvicorn"],
    "excludes": ["tkinter"],
    "include_files": [],
}

executables = [
    Executable(
        main_script,
        target_name="DownloadService.exe",
        base=None,
    )
]

setup(
    name="DownloadService",
    version="0.0.2",
    description="YouTube video download service",
    options={"build_exe": build_options},
    executables=executables,
)
