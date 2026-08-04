#define AppName "IT Support Tool Suite"
#ifndef AppVersion
  #error AppVersion must be supplied with /DAppVersion=x.y.z
#endif
#ifndef SourceExe
  #error SourceExe must be supplied with /DSourceExe=path
#endif

[Setup]
AppId={{D1A101B7-963E-4D64-A9DF-38D2838104A4}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=IT Support Tool Suite Publisher
DefaultDirName={autopf}\IT Support Tool Suite
DefaultGroupName={#AppName}
OutputBaseFilename=ITSupportToolSuite-Setup-v{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
WizardStyle=modern
UninstallDisplayIcon={app}\ITSupportToolSuite.exe
LicenseFile=..\docs\EULA.md

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "ITSupportToolSuite.exe"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\ITSupportToolSuite.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\ITSupportToolSuite.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\ITSupportToolSuite.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
