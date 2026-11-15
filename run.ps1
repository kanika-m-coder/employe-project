# AttendPay One-Command Launcher for PowerShell
$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting AttendPay - Employee Payroll System" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Set Environment Paths
$LocalApp = $env:LOCALAPPDATA
$JavaPath = "$LocalApp\Programs\Java\jdk-17.0.21.0.2+1\bin"
$MysqlPath = "$LocalApp\Programs\MySQL\mariadb-10.11.10-winx64\bin"
$PythonPath = "$LocalApp\Programs\Python\Python311"
$PythonScripts = "$LocalApp\Programs\Python\Python311\Scripts"

if (Test-Path $JavaPath) { $env:PATH = "$JavaPath;$env:PATH" }
if (Test-Path $MysqlPath) { $env:PATH = "$MysqlPath;$env:PATH" }
if (Test-Path $PythonPath) { $env:PATH = "$PythonPath;$PythonScripts;$env:PATH" }

# 1. Check Port 3307
Write-Host "[1/4] Checking Database Server (Port 3307)..." -ForegroundColor Yellow
$dbActive = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
if (-not $dbActive) {
    Write-Host "      Starting MariaDB on port 3307..." -ForegroundColor Gray
    $mysqldExe = "$LocalApp\Programs\MySQL\mariadb-10.11.10-winx64\bin\mysqld.exe"
    $dataDir = "$LocalApp\Programs\MySQL\mariadb-10.11.10-winx64\data"
    if (Test-Path $mysqldExe) {
        Start-Process -FilePath $mysqldExe -ArgumentList "--datadir=`"$dataDir`" --port=3307" -WindowStyle Hidden
    } else {
        Start-Process mysqld -ArgumentList "--port=3307" -WindowStyle Hidden
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "      Database server is already active on port 3307." -ForegroundColor Green
}

# 2. Check Database Schema
Write-Host "[2/4] Verifying database schema and records..." -ForegroundColor Yellow
$checkDb = mysql -u root -P 3307 -e "USE payroll_db; SELECT 1 FROM employees LIMIT 1;" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Initializing schema and sample data..." -ForegroundColor Gray
    Get-Content database\schema.sql | mysql -u root -P 3307
    Get-Content database\sample_data.sql | mysql -u root -P 3307
    Write-Host "      Database initialized successfully." -ForegroundColor Green
} else {
    Write-Host "      Database 'payroll_db' is ready." -ForegroundColor Green
}

# 3. Open Browser
Write-Host "[3/4] Opening browser at http://localhost:8080..." -ForegroundColor Yellow
Start-Process "http://localhost:8080"

# 4. Start Java Server
Write-Host "[4/4] Starting AttendPay Java Web Server on port 8080..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  AttendPay is Live at: http://localhost:8080" -ForegroundColor Green
Write-Host "  Press Ctrl+C in this terminal to stop the server anytime." -ForegroundColor Gray
Write-Host "========================================================" -ForegroundColor Cyan

java -cp "lib/*" src/Main.java
