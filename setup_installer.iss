[Setup]
AppName=DownloadService
AppVersion=0.0.2
DefaultDirName={autopf}\DownloadService
DefaultGroupName=DownloadService
OutputDir=Output
OutputBaseFilename=DownloadServiceInstaller
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\icon.ico

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "build\exe.win-amd64-3.11\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "extension\*"; DestDir: "{app}\extension"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; AfterInstall: extensionInstall
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commonstartup}\DownloadService"; Filename: "{app}\DownloadService.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\DownloadService.exe"; Description: "Run DownloadService"; Flags: nowait postinstall skipifsilent

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