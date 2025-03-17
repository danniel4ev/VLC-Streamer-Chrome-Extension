@echo off
echo Uninstalling VLC Streamer Chrome Extension...
REG DELETE "HKCU\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.vlc.opener" /f
rmdir /s /q "%LOCALAPPDATA%\\VLCOpener"
echo Uninstallation complete. Please remove the extension from Chrome manually.
pause