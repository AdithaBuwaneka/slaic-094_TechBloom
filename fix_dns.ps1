# Fix DNS Configuration for MongoDB Atlas
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DNS Fix Script - Transit Companion" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Get current DNS configuration
Write-Host "Current DNS Configuration:" -ForegroundColor Yellow
netsh interface ipv4 show dnsservers "Wi-Fi"
Write-Host ""

# Prompt for confirmation
$confirm = Read-Host "Do you want to change DNS to Google DNS (8.8.8.8, 8.8.4.4)? (Y/N)"

if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Changing DNS servers..." -ForegroundColor Cyan

# Set DNS servers
try {
    netsh interface ipv4 set dns name="Wi-Fi" static 8.8.8.8 primary
    netsh interface ipv4 add dns name="Wi-Fi" 8.8.4.4 index=2

    Write-Host "[OK] DNS servers changed successfully" -ForegroundColor Green
    Write-Host ""

    # Flush DNS cache
    Write-Host "Flushing DNS cache..." -ForegroundColor Cyan
    ipconfig /flushdns
    Write-Host "[OK] DNS cache flushed" -ForegroundColor Green
    Write-Host ""

    # Test DNS resolution
    Write-Host "Testing MongoDB Atlas DNS resolution..." -ForegroundColor Cyan
    $result = nslookup smarttransitcompanion.j3c5osf.mongodb.net 8.8.8.8 2>&1 | Out-String

    if ($result -match "Address") {
        Write-Host "[OK] DNS resolution working!" -ForegroundColor Green
        Write-Host ""
        Write-Host "MongoDB Atlas hostname resolved successfully." -ForegroundColor Green
    } else {
        Write-Host "[WARNING] DNS test returned unexpected result" -ForegroundColor Yellow
        Write-Host $result
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  DNS Fix Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Restart your backend server" -ForegroundColor White
    Write-Host "2. Restart your mobile app" -ForegroundColor White
    Write-Host "3. Test route planning functionality" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "[ERROR] Error changing DNS:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try the manual method in FIX_ALL_ISSUES.md" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
