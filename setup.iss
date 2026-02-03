[Setup]
AppName=DownHub
AppVersion=1.0.0
AppPublisher=WipoDev
AppPublisherURL=https://github.com/wipodev/downhub
AppSupportURL=https://github.com/wipodev/downhub/issues
AppUpdatesURL=https://github.com/wipodev/downhub/release
VersionInfoCompany=WipoDev
VersionInfoCopyright=© 2026 WipoDev. Apache 2.0 License.
VersionInfoDescription=Instalador de DownHub
VersionInfoProductName=DownHub
VersionInfoProductVersion=1.0.0.0
VersionInfoTextVersion=1.0.0.0
VersionInfoVersion=1.0.0.0
DefaultDirName={localappdata}\DownHub
DefaultGroupName=DownHub
PrivilegesRequired=lowest
SetupIconFile=assets\icon_installer.ico
UninstallDisplayIcon={app}\DownHubService.exe
Compression=lzma
LicenseFile=LICENSE
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=DownHub_Installer
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\DownHubService.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "net.wipodev.downhub.json"; DestDir: "{app}"; Flags: ignoreversion;
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs
Source: "extension\*"; DestDir: "{app}\extension"; Flags: ignoreversion recursesubdirs

[Registry]
Root: HKCU; Subkey: "Software\Google\Chrome\NativeMessagingHosts\net.wipodev.downhub"; ValueType: string; ValueName: ""; ValueData: "{app}\net.wipodev.downhub.json"; Flags: uninsdeletekey


[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Para instalar la extensión en Google Chrome:' + #13#10 +
          '1. Abra Google Chrome.' + #13#10 +
          '2. Escriba "chrome://extensions" en la barra de direcciones y presione Enter.' + #13#10 +
          '3. Active el modo desarrollador.' + #13#10 +
          '4. Haz clic en "Cargar extension sin empaquetar".' + #13#10 +
          '5. Selecciona la carpeta de la extensión en "' + ExpandConstant('{app}') + '\extension" y haz clic en "Cargar".',
          mbInformation, MB_OK);
  end;
end;