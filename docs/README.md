# VLC Streamer Chrome Extension - Technical Documentation

This document provides comprehensive technical information about the **VLC Streamer Chrome Extension** project, including its architecture, implementation details, and customization options. This documentation is intended for developers and advanced users who want to understand the inner workings of the project.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Technical Components](#technical-components)
3. [Installation Process](#installation-process)
4. [Native Messaging Protocol](#native-messaging-protocol)
5. [Chrome Extension Implementation](#chrome-extension-implementation)
6. [Python Host Implementation](#python-host-implementation)
7. [Registry Configuration](#registry-configuration)
8. [Customization Guide](#customization-guide)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)

---

## Architecture Overview

The VLC Streamer Chrome Extension uses Chrome's native messaging API to establish communication between the browser extension and the local VLC Media Player application. The system consists of three main components:

1. **Chrome Extension**: A browser extension that adds a context menu item for opening media links in VLC.
2. **Native Messaging Host**: A Python script that receives messages from Chrome and launches VLC.
3. **Installer Application**: A GUI application that sets up all necessary components and configurations.

The communication flow is as follows:
User → Chrome Extension → Native Messaging Host → VLC Media Player

---

## Technical Components

### 1. Chrome Extension
- **Manifest Version**: 3
- **Permissions**: contextMenus, nativeMessaging
- **Background Service Worker**: Handles context menu creation and message passing
- **Icons**: 16px, 48px, and 128px VLC icons

### 2. Native Messaging Host
- **Language**: Python 3.9+
- **Communication Protocol**: Chrome Native Messaging (binary message format)
- **Wrapper**: Batch file that launches the Python script

### 3. Installer Application
- **Language**: Python with Tkinter GUI
- **Packaging**: PyInstaller for creating standalone executable
- **System Integration**: Windows Registry modification for native messaging host registration

---

## Installation Process

The installer performs the following steps:

1. **System Check**:
   - Verifies VLC Media Player installation
   - Checks for Google Chrome installation
   - Confirms Python 3.9+ availability

2. **File Creation**:
   - Creates directory structure in `%LOCALAPPDATA%\VLCOpener\`
   - Generates Chrome extension files (manifest.json, background.js)
   - Creates Python native messaging host script
   - Downloads VLC icons from the official repository

3. **Registry Configuration**:
   - Adds registry entry for the native messaging host at:
     `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener`

4. **Extension Setup**:
   - Guides user to load the unpacked extension in Chrome
   - Prompts for Extension ID to complete configuration
   - Updates native messaging host manifest with the Extension ID

---

## Native Messaging Protocol

The communication between Chrome and the native messaging host follows the [Chrome Native Messaging Protocol](https://developer.chrome.com/docs/apps/nativeMessaging/#native-messaging-host-protocol):

1. **Message Format**:
   - Each message is serialized using JSON
   - Messages are preceded by a 32-bit length prefix (little-endian)
   - Messages are sent and received through standard input/output streams

2. **Message Structure**:
   - From Chrome to host: `{"url": "https://example.com/video.mp4"}`
   - From host to Chrome: `{"success": true}` or `{"success": false, "error": "Error message"}`

3. **Implementation Details**:
   ```python
   # Reading messages
   raw_length = sys.stdin.buffer.read(4)
   message_length = struct.unpack('=I', raw_length)[0]
   message = sys.stdin.buffer.read(message_length).decode('utf-8')
   
   # Sending messages
   encoded_message = json.dumps(message).encode('utf-8')
   encoded_length = struct.pack('=I', len(encoded_message))
   sys.stdout.buffer.write(encoded_length)
   sys.stdout.buffer.write(encoded_message)
   ```

---

## Chrome Extension Implementation
The Chrome extension consists of the following key files:

### 1. manifest.json
   ```json
   {
   "name": "VLC Streamer",
   "version": "1.0",
   "description": "Open media links in VLC Media Player",
   "background": {
      "service_worker": "background.js"
   },
   "icons": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
   },
   "permissions": ["contextMenus", "nativeMessaging"],
   "manifest_version": 3
   }
   ```

### 2. background.js
   ```javascript
   chrome.contextMenus.create({
   id: "openInVLC",
   title: "Open in VLC",
   contexts: ["link", "video", "audio"]
   });

   chrome.contextMenus.onClicked.addListener((info, tab) => {
   if (info.menuItemId === "openInVLC") {
      chrome.runtime.sendNativeMessage("com.vlc.opener", {
         url: info.linkUrl || info.srcUrl
      }, (response) => {
         console.log("Response:", response);
      });
   }
   });
   ```

---

## Python Host Implementation
The native messaging host is implemented as a Python script that:

1. Reads messages from Chrome using the native messaging protocol
2. Extracts the URL from the message
3. Launches VLC with the URL as an argument
4. Sends a response back to Chrome
Key implementation details:
   ```python
   import sys
   import json
   import struct
   import subprocess

   def get_message():
      raw_length = sys.stdin.buffer.read(4)
      if len(raw_length) == 0:
         sys.exit(0)
      message_length = struct.unpack('=I', raw_length)[0]
      message = sys.stdin.buffer.read(message_length).decode('utf-8')
      return json.loads(message)

   def send_message(message):
      encoded_content = json.dumps(message).encode('utf-8')
      encoded_length = struct.pack('=I', len(encoded_content))
      sys.stdout.buffer.write(encoded_length)
      sys.stdout.buffer.write(encoded_content)
      sys.stdout.buffer.flush()

   def main():
      message = get_message()
      url = message.get("url")
      
      if url:
         try:
               subprocess.Popen([VLC_PATH, url])
               send_message({"success": True})
         except Exception as e:
               send_message({"success": False, "error": str(e)})
      else:
         send_message({"success": False, "error": "No URL provided"})
   ```

---

## Registry Configuration
The native messaging host is registered in the Windows Registry to allow Chrome to locate and launch it:

1. Registry Key : HKCU\Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener
2. Value : Path to the native messaging host manifest file ( %LOCALAPPDATA%\VLCOpener\native_host\com.vlc.opener.json )
The manifest file specifies:
   ```json
   {
   "name": "com.vlc.opener",
   "description": "Open media in VLC",
   "path": "C:\\Users\\[Username]\\AppData\\Local\\VLCOpener\\scripts\\vlc_opener.bat",
   "type": "stdio",
   "allowed_origins": ["chrome-extension://[EXTENSION_ID]/"]
   }
```

---

## Customization Guide
### Modifying the Chrome Extension
1. Change Context Menu Text :
   Edit the title property in the chrome.contextMenus.create() call in background.js .
2. Add Support for More Contexts :
   Modify the contexts array in background.js to include additional contexts like page , selection , etc.
3. Custom Icons :
   Replace the icon files in the icons directory with your own icons, maintaining the same filenames and dimensions.
### Modifying the Native Messaging Host
1. Custom VLC Arguments :
   Edit the subprocess.Popen() call in vlc_opener.py to add additional command-line arguments to VLC.
2. Add Logging :
   Implement logging to a file by adding code like:
   ```python
   import logging
   logging.basicConfig(filename='%LOCALAPPDATA%\\VLCOpener\\logs\\vlc_opener.log', level=logging.INFO)
   logging.info(f"Opening URL: {url}")
   ```
3. Support for Additional Media Players :
   Modify the script to support other media players based on file extension or user preference.

---

## Troubleshooting
### Common Issues and Solutions
1. "Native host has exited" Error :
   - Cause : Python script is not executing properly.
   - Solution : Check that Python is installed and in PATH, verify script permissions.

2. "Cannot establish connection with native application" Error :
   - Cause : Registry entry or manifest file is incorrect.
   - Solution : Verify registry entry points to the correct manifest file, check manifest format.

3. VLC Launches But No Media Plays :
   - Cause : URL format or network access issues.
   - Solution : Test the URL directly in VLC, check network connectivity.

4. Extension ID Issues :
   - Cause : Incorrect Extension ID in the native messaging host manifest
   - Solution : Re-run the setup_extension.bat script with the correct Extension ID

### Diagnostic Steps
1. Check Registry Entry :
   ```plaintext
   reg query "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener" /ve
    ```

2. Test Native Messaging Host :
   Create a test JSON file and pipe it to the Python script:
   
   ```plaintext
   echo {"url":"https://example.com/video.mp4"} | python %LOCALAPPDATA%\VLCOpener\scripts\vlc_opener.py
    ```

3. Check Chrome Extension Logs :
   Open Chrome DevTools for the background page (chrome://extensions → Developer mode → background page)

## Development Guide
### Setting Up Development Environment
1. Clone the Repository :
   ```plaintext
   git clone https://github.com/yourusername/VLC-Streamer-Chrome-Extension.git
   cd VLC-Streamer-Chrome-Extension
    ```
2. Install Dependencies :
   
   ```plaintext
   pip install pywin32 pyinstaller
    ```
3. Build the Installer :
   
   ```plaintext
   pyinstaller vlc_streamer_installer.spec
    ```

### Making Changes
1. Modify the Installer :
   Edit vlc_streamer_installer.py to change the installation process or GUI.
2. Update Extension Files :
   Modify the extension files generated in the create_files() function.
3. Test Your Changes :
   Run the installer in development mode:

   ```plaintext
   python vlc_streamer_installer.py
    ```
### Building for Distribution
1. Update Version Number :
   Edit the version number in both the installer and the extension manifest.
2. Build with PyInstaller :
   ```plaintext
   pyinstaller --onefile --windowed --icon=icon.ico vlc_streamer_installer.py
    ```
3. Test the Executable :
   Test the generated executable on a clean system to ensure all dependencies are included.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- VLC Media Player : For providing an excellent open-source media player.
- Google Chrome : For supporting native messaging and extensions.
- Python : For providing a robust platform for the native messaging host.
This documentation is maintained by the VLC Streamer Chrome Extension development team.

---

## Special Thanks

Special thanks to [CyberUni.ir](https://cyberuni.ir) for their support and resources. The developer of this extension is a proud member of the CyberUni.ir community, which provides valuable educational resources and support for developers.