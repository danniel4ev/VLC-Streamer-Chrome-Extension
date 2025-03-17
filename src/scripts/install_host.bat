@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

if "!SCRIPT_DIR:~-1!" == "\" set SCRIPT_DIR=!SCRIPT_DIR:~0,-1!

set MANIFEST_PATH=%SCRIPT_DIR%\com.vlc.opener-win.json

if not exist "%MANIFEST_PATH%" (
    echo Error: Native messaging host manifest not found at:
    echo %MANIFEST_PATH%
    goto :error
)

set TEMP_MANIFEST=%TEMP%\com.vlc.opener-win.json
type "%MANIFEST_PATH%" > "%TEMP_MANIFEST%"

powershell -Command "(Get-Content '%TEMP_MANIFEST%') -replace 'PATH_TO_BE_REPLACED', '%SCRIPT_DIR:\=\\%' | Set-Content '%TEMP_MANIFEST%'"

echo Installing native messaging host for Chrome...
REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener" /ve /t REG_SZ /d "%TEMP_MANIFEST%" /f
if %ERRORLEVEL% NEQ 0 (
    echo Failed to add registry key for Chrome.
    goto :error
)

reg query "HKCU\Software\Microsoft\Edge" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Installing native messaging host for Microsoft Edge...
    REG ADD "HKCU\Software\Microsoft\Edge\NativeMessagingHosts\com.vlc.opener" /ve /t REG_SZ /d "%TEMP_MANIFEST%" /f
)

echo Native messaging host installed successfully!
goto :end

:error
echo Installation failed.
exit /b 1

:end
echo.
echo You can now use the "Open in VLC" Chrome extension.
echo To test it, right-click on any media link and select "Open in VLC".
echo.
pause