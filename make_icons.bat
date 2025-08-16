@echo off
setlocal enabledelayedexpansion
set ASSETS=assets

REM Lista de subcarpetas que contienen los PNG
for %%D in (icon_gui icon_service icon_installer favicon) do (
    echo === Procesando %%D ===
    set FILES=
    for %%S in (16 32 48 128 256) do (
        set FILES=!FILES! "%ASSETS%\%%D\%%D-%%S.png"
    )

    REM Generar el .ico en assets/
    magick !FILES! "%ASSETS%\%%D.ico"
    if exist "%ASSETS%\%%D.ico" (
        echo Generado: %ASSETS%\%%D.ico
    ) else (
        echo Error generando %ASSETS%\%%D.ico
    )
)

echo.
echo 🚀 Conversión completada.
pause
