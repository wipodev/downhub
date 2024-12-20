[Setup]
AppName=DownloadService
AppVersion=0.0.2
DefaultDirName={autopf}\DownloadService
DefaultGroupName=DownloadService
OutputDir=Output
OutputBaseFilename=DownloadServiceInstaller
Compression=lzma
SolidCompression=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "build\exe.win-amd64-3.11\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "dist\DownTube.crx"; DestDir: "{userdesktop}"; Flags: ignoreversion; AfterInstall: extensionInstall

[Icons]
Name: "{commonstartup}\DownloadService"; Filename: "{app}\DownloadService.exe"; WorkingDir: "{app}"

[Code]
var
  ErrorCode: Integer;
  ChromeProfile: String;

procedure extensionInstall();
begin
  MsgBox('Para instalar la extensión en Google Chrome:' + #13#10 +
         '1. Abra Google Chrome.' + #13#10 +
         '2. Escriba "chrome://extensions" en la barra de direcciones y presione Enter.' + #13#10 +
         '3. Arrastre el archivo DownTube.crx desde su escritorio a la ventana de extensiones.', 
         mbInformation, MB_OK);

  
  ChromeProfile := '--profile-directory="Default"';
  if not ShellExec('', 'chrome.exe', 'chrome://extensions' + ChromeProfile, '', SW_SHOWNORMAL, ewNoWait, ErrorCode) then
  begin
    MsgBox('Error al intentar abrir Chrome: ' + SysErrorMessage(ErrorCode), mbError, MB_OK);
  end;
end;