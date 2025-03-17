@echo off
echo VLC Streamer Extension Setup
echo ============================
echo.
echo Please enter your Chrome Extension ID
echo (Found on chrome://extensions after enabling Developer Mode)
echo.
set /p extid="Extension ID: "
echo.
echo Updating configuration with ID: %extid%

powershell -Command "(Get-Content '%LOCALAPPDATA%\\VLCOpener\\native_host\\com.vlc.opener.json') -replace 'EXTENSION_ID', '%extid%' | Set-Content '%LOCALAPPDATA%\\VLCOpener\\native_host\\com.vlc.opener.json'"

REG ADD "HKCU\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.vlc.opener" /ve /t REG_SZ /d "%LOCALAPPDATA%\\VLCOpener\\native_host\\com.vlc.opener.json" /f

echo.
echo Configuration complete!
echo You can now use the "Open in VLC" context menu item in Chrome.
echo.
pause