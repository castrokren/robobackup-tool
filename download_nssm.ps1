# Download NSSM for easy service installation
param(
    [string]$DownloadPath = ".",
    [switch]$Force
)

$NSSMUrl = "https://nssm.cc/release/nssm-2.24.zip"
$ZipFile = Join-Path $DownloadPath "nssm-2.24.zip"
$ExtractPath = Join-Path $DownloadPath "nssm"
$NSSMExe = Join-Path $DownloadPath "nssm.exe"

Write-Host "RoboBackup NSSM Download Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if NSSM already exists
if ((Test-Path $NSSMExe) -and -not $Force) {
    Write-Host "NSSM already exists at: $NSSMExe" -ForegroundColor Green
    Write-Host "Use -Force to re-download" -ForegroundColor Yellow
    exit 0
}

try {
    Write-Host "Downloading NSSM from: $NSSMUrl" -ForegroundColor Yellow
    
    # Download NSSM
    Invoke-WebRequest -Uri $NSSMUrl -OutFile $ZipFile -UseBasicParsing
    Write-Host "Downloaded: $ZipFile" -ForegroundColor Green
    
    # Extract ZIP
    Write-Host "Extracting NSSM..." -ForegroundColor Yellow
    if (Test-Path $ExtractPath) {
        Remove-Item $ExtractPath -Recurse -Force
    }
    Expand-Archive -Path $ZipFile -DestinationPath $ExtractPath -Force
    
    # Copy appropriate architecture NSSM
    $Architecture = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
    $SourceNSSM = Join-Path (Join-Path $ExtractPath "nssm-2.24") $Architecture "nssm.exe"
    
    if (Test-Path $SourceNSSM) {
        Copy-Item $SourceNSSM $NSSMExe -Force
        Write-Host "NSSM copied to: $NSSMExe" -ForegroundColor Green
        
        # Cleanup
        Remove-Item $ZipFile -Force
        Remove-Item $ExtractPath -Recurse -Force
        
        Write-Host "`nNSSM installation complete!" -ForegroundColor Green
        Write-Host "You can now run: install_nssm_service.bat" -ForegroundColor Cyan
        
    } else {
        throw "Could not find NSSM executable in downloaded package"
    }
    
} catch {
    Write-Error "Failed to download/install NSSM: $_"
    exit 1
}
