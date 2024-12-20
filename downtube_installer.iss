[Setup]
AppName=DownloadService
AppVersion=0.0.1
DefaultDirName={autopf}\DownloadService
DefaultGroupName=DownloadService
OutputDir=Output
OutputBaseFilename=DownloadServiceInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Copia el ejecutable a la carpeta de inicio del usuario actual
Source: "backend\dist\DownloadService.exe"; DestDir: "{userstartup}"; Flags: ignoreversion

; Copia el archivo CRX a una carpeta en Archivos de Programa
Source: "extension\DownTube.crx"; DestDir: "{userdesktop}"; Flags: ignoreversion; AfterInstall: extensionInstall

[Run]
; Ejecuta el servicio automáticamente después de la instalación
Filename: "{userstartup}\DownloadService.exe"; Flags: nowait postinstall skipifsilent

[Code]
procedure extensionInstall();
begin
  MsgBox('Para instalar la extensión en Google Chrome:' + #13#10 +
         '1. Abra Google Chrome.' + #13#10 +
         '2. Escriba "chrome://extensions" en la barra de direcciones y presione Enter.' + #13#10 +
         '3. Arrastre el archivo DownTube.crx desde su escritorio a la ventana de extensiones.', 
         mbInformation, MB_OK);
end;