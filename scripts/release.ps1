param(
    [string]$Version,
    [switch]$RequireSignature,
    [switch]$CreateInstaller,
    [switch]$CreateGitTag
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$VersionFile = Join-Path $ProjectRoot "VERSION"
if ($Version) {
    if ($Version -notmatch '^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$') { throw "Invalid SemVer: $Version" }
    [IO.File]::WriteAllText($VersionFile, "$Version`n", [Text.UTF8Encoding]::new($false))
} else { $Version = (Get-Content $VersionFile -Raw).Trim() }

Push-Location $ProjectRoot
try {
    python -m pytest
    if ($LASTEXITCODE) { throw "Tests failed." }
    python -m PyInstaller --noconfirm --clean "packaging\ITSupportToolSuite.spec"
    if ($LASTEXITCODE) { throw "PyInstaller failed." }

    $Exe = Join-Path $ProjectRoot "dist\ITSupportToolSuite-v$Version.exe"
    if (-not (Test-Path $Exe)) { throw "Missing release executable: $Exe" }
    $SignTool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
    if ($env:SIGN_CERT_PATH) {
        if (-not $SignTool) { throw "signtool.exe was not found." }
        $args = @('sign','/fd','SHA256','/td','SHA256','/tr','http://timestamp.digicert.com','/f',$env:SIGN_CERT_PATH)
        if ($env:SIGN_CERT_PASSWORD) { $args += @('/p',$env:SIGN_CERT_PASSWORD) }
        $args += $Exe
        & $SignTool @args
        if ($LASTEXITCODE) { throw "Authenticode signing failed." }
        & $SignTool verify /pa /all $Exe
        if ($LASTEXITCODE) { throw "Authenticode verification failed." }
    } elseif ($RequireSignature) {
        throw "SIGN_CERT_PATH is required for a commercial release."
    }

    $Artifacts = @($Exe)
    if ($CreateInstaller) {
        $Iscc = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
        if (-not $Iscc) { throw "Inno Setup ISCC.exe was not found." }
        & $Iscc "/DAppVersion=$Version" "/DSourceExe=$Exe" "packaging\installer.iss"
        if ($LASTEXITCODE) { throw "Installer build failed." }
        $Installer = Join-Path $ProjectRoot "packaging\Output\ITSupportToolSuite-Setup-v$Version.exe"
        if ($env:SIGN_CERT_PATH) {
            & $SignTool sign /fd SHA256 /td SHA256 /tr http://timestamp.digicert.com /f $env:SIGN_CERT_PATH /p $env:SIGN_CERT_PASSWORD $Installer
            & $SignTool verify /pa /all $Installer
        }
        $Artifacts += $Installer
    }

    $ChecksumFile = Join-Path $ProjectRoot "dist\SHA256SUMS-v$Version.txt"
    $lines = foreach ($artifact in $Artifacts) {
        $hash = (Get-FileHash $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $([IO.Path]::GetFileName($artifact))"
    }
    [IO.File]::WriteAllLines($ChecksumFile, $lines, [Text.UTF8Encoding]::new($false))

    if ($CreateGitTag) {
        git diff --quiet
        if ($LASTEXITCODE) { throw "Working tree must be clean before tagging." }
        git tag -s "v$Version" -m "IT Support Tool Suite v$Version"
    }
    Write-Host "Release artifacts verified. Checksums: $ChecksumFile"
} finally { Pop-Location }
