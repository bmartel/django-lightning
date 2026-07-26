# Lightweight PowerShell installer for create-django-bolt Rust CLI binary on Windows (No Rust/Cargo required)
$ErrorActionPreference = "Stop"

$Repo = "bmartel/django-lightning"
$BinName = "create-django-bolt.exe"
$Asset = "create-django-bolt-windows-x86_64.zip"

$InstallDir = Join-Path $env:LocalAppData "create-django-bolt\bin"

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$Url = "https://github.com/$Repo/releases/latest/download/$Asset"
$TempZip = Join-Path $env:TEMP "create-django-bolt.zip"
$TempExtract = Join-Path $env:TEMP "create-django-bolt-extract"

Write-Host "⚡ Downloading create-django-bolt CLI from $Url..." -ForegroundColor Cyan

Invoke-WebRequest -Uri $Url -OutFile $TempZip -UseBasicParsing

if (Test-Path $TempExtract) {
    Remove-Item -Path $TempExtract -Recurse -Force
}

Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force

$ExtractedExe = Join-Path $TempExtract $BinName
$DestinationExe = Join-Path $InstallDir $BinName

if (Test-Path $ExtractedExe) {
    Copy-Item -Path $ExtractedExe -Destination $DestinationExe -Force
} else {
    Write-Error "Could not find $BinName inside release package."
    exit 1
}

# Cleanup temporary download files
Remove-Item -Path $TempZip -Force -ErrorAction SilentlyContinue
Remove-Item -Path $TempExtract -Recurse -Force -ErrorAction SilentlyContinue

# Ensure InstallDir is on User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ($UserPath -notlike "*$InstallDir*") {
    $NewPath = "$UserPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, [EnvironmentVariableTarget]::User)
    $env:Path = "$env:Path;$InstallDir"
    Write-Host "✨ Added $InstallDir to User PATH." -ForegroundColor Yellow
}

Write-Host "✨ Successfully installed $BinName to $DestinationExe!" -ForegroundColor Green
Write-Host "Run 'create-django-bolt new my-app' in your terminal to get started." -ForegroundColor Cyan
