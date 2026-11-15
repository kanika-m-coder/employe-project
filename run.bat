@echo off
setlocal enabledelayedexpansion
title AttendPay - Employee Payroll System

echo ========================================================
echo   Starting AttendPay - Employee Payroll System
echo ========================================================

:: Configure environment paths
if exist "%LOCALAPPDATA%\Programs\Java\jdk-17.0.21.0.2+1" (
    set "JAVA_HOME=%LOCALAPPDATA%\Programs\Java\jdk-17.0.21.0.2+1"
    set "PATH=!JAVA_HOME!\bin;!PATH!"
)
if exist "%LOCALAPPDATA%\Programs\MySQL\mariadb-10.11.10-winx64" (
    set "MYSQL_DIR=%LOCALAPPDATA%\Programs\MySQL\mariadb-10.11.10-winx64"
    set "PATH=!MYSQL_DIR!\bin;!PATH!"
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311" (
    set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python311"
    set "PATH=!PYTHON_DIR!;!PYTHON_DIR!\Scripts;!PATH!"
)

:: 1. Verify / Start MariaDB database on port 3307
echo [1/4] Checking Database Server (Port 3307)...
netstat -ano | findstr /R /C:":3307 .*LISTENING" >nul
if errorlevel 1 (
    echo       Starting MariaDB database server on port 3307...
    if defined MYSQL_DIR (
        start /B "" "!MYSQL_DIR!\bin\mysqld.exe" --datadir="!MYSQL_DIR!\data" --port=3307
    ) else (
        start /B "" mysqld --port=3307
    )
    timeout /t 3 /nobreak >nul
) else (
    echo       MariaDB server is already active on port 3307.
)

:: 2. Auto-initialize Database and Sample Data if needed
echo [2/4] Verifying database schema and tables...
mysql -u root -P 3307 -e "USE payroll_db; SELECT 1 FROM employees LIMIT 1;" >nul 2>&1
if errorlevel 1 (
    echo       Initializing payroll_db schema and sample records...
    mysql -u root -P 3307 < database\schema.sql
    mysql -u root -P 3307 < database\sample_data.sql
    echo       Database initialized successfully.
) else (
    echo       Database 'payroll_db' is verified and ready.
)

:: 3. Launch Default Browser to http://localhost:8080
echo [3/4] Opening Web Application in Browser...
start http://localhost:8080

:: 4. Start Java Server on port 8080
echo [4/4] Starting Java Web Server on port 8080...
echo.
echo ========================================================
echo   AttendPay is Live at: http://localhost:8080
echo   Press Ctrl+C in this terminal to stop anytime.
echo ========================================================
echo.
java -cp "lib/*" src/Main.java
pause
