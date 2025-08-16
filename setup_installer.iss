[Setup]
AppName=DownHubService
AppVersion=0.0.3
DefaultDirName={autopf}\DownHubService
DefaultGroupName=DownHubService
OutputDir=dist
OutputBaseFilename=DownHubServiceInstaller
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\icon.ico

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Copia todos los archivos de la compilación cx_Freeze
Source: "build\exe.win-amd64-3.11\*"; DestDir: "{app}"; Flags: onlyifdoesntexist recursesubdirs createallsubdirs
; API
Source: "build\exe.win-amd64-3.11\DownHubService.exe"; DestDir: "{app}"; Flags: ignoreversion
; GUI
Source: "build\exe.win-amd64-3.11\DownHubGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "extension\*"; DestDir: "{app}\extension"; Flags: comparetimestamp recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: extensionInstall

[Icons]
; Servicio API en carpeta de inicio
Name: "{commonstartup}\DownHubService"; Filename: "{app}\DownHubService.exe"; WorkingDir: "{app}"
; GUI en escritorio
Name: "{commondesktop}\DownHubGUI"; Filename: "{app}\DownHubGUI.exe"; WorkingDir: "{app}"

[Run]
; 1. Durante instalación: detener cualquier DownHubService previo antes de copiar archivos
Filename: "taskkill"; Parameters: "/F /IM DownHubService.exe"; Flags: runhidden; StatusMsg: "Finalizando DownHubService en ejecución..."
; 2. Después de instalar, lanzar el servicio
Filename: "{app}\DownHubService.exe"; Description: "Run DownHubService"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Durante desinstalación: cerrar el servicio antes de borrar archivos
Filename: "taskkill"; Parameters: "/F /IM DownHubService.exe"; Flags: runhidden; RunOnceId: "KillDownHubService"

[Code]
procedure extensionInstall();
begin
  MsgBox('Para instalar la extensión en Google Chrome:' + #13#10 +
         '1. Abra Google Chrome.' + #13#10 +
         '2. Escriba "chrome://extensions" en la barra de direcciones y presione Enter.' + #13#10 +
         '3. Active el modo desarrollador.' + #13#10 +
         '4. Haz clic en "Cargar extension sin empaquetar".' + #13#10 +
         '5. Selecciona la carpeta de la extensión en "' + ExpandConstant('{app}') + '\extension" y haz clic en "Cargar".',
         mbInformation, MB_OK);
end;