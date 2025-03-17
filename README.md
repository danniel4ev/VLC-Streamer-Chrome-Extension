# VLC Streamer Chrome Extension - Windows Installer

This repository contains a Windows GUI installer that automates the installation of the **VLC Streamer Chrome Extension**. This extension allows you to open media links directly in the VLC media player from your browser. The installer sets up the necessary files, registers the native messaging host, and provides an easy way to install and uninstall the extension.

---

# VLC Streamer Chrome Extension

![GitHub License](https://img.shields.io/github/license/danniel4ev/VLC-Streamer-Chrome-Extension)
![GitHub Issues](https://img.shields.io/github/issues/danniel4ev/VLC-Streamer-Chrome-Extension)

---

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Uninstallation](#uninstallation)
6. [How It Works](#how-it-works)
7. [File Structure](#file-structure)
8. [Contributing](#contributing)
9. [License](#license)

---

## Overview

The **VLC Streamer Chrome Extension** enhances your browsing experience by allowing you to open media links directly in VLC Media Player. This is particularly useful for streaming content or playing media files that are not natively supported by your browser.

The installer provides a user-friendly GUI that:
- Checks for VLC and Chrome installations
- Creates the necessary directories and files
- Registers the native messaging host with Chrome
- Guides you through the extension setup process
- Provides an easy way to uninstall the extension

---

## Features

- **User-Friendly GUI**: Simple interface for installing and configuring the extension
- **Automatic Detection**: Automatically detects VLC and Chrome installations
- **Cross-Platform Compatibility**: Works with both 32-bit and 64-bit versions of VLC
- **Uninstaller**: Includes a shortcut to cleanly remove the extension and associated files
- **Guided Setup**: Step-by-step guidance for installing the Chrome extension

---

## Prerequisites

Before running the installer, ensure you have the following:

1. **VLC Media Player**: Installed on your system. If not, download it from [VLC's official website](https://www.videolan.org/).
2. **Google Chrome**: The extension is designed for Chrome.
3. **Administrator Privileges**: The installer requires admin rights to modify system files and registry entries.

---

## Installation

### Step 1: Download the Installer
Download the `vlc_streamer_installer.exe` from this repository.

### Step 2: Run the Installer
1. Right-click the `VLC-stream-installer.exe` file and select **Run as Administrator**.
2. Follow the on-screen instructions:
   - The installer will check for VLC and Chrome installations
   - If VLC is not found automatically, you can browse to locate it
   - The installer will create all necessary files and directories
   - A desktop shortcut for uninstallation will be created

### Step 3: Install the Chrome Extension
1. After the installation completes, the installer will guide you through the Chrome extension setup:
   - Chrome extensions page will open automatically
   - The extension folder will open for you to load as an unpacked extension
   - You'll be prompted to enter the Extension ID to complete the configuration

2. After installation, you can right-click any media link and select **Open in VLC** to stream it directly in VLC.

---

## Uninstallation

To uninstall the VLC Streamer Chrome Extension and its associated files:

1. Double-click the **Uninstall VLC Opener** shortcut on your desktop.
2. Follow the on-screen instructions to remove the extension and native messaging host.
3. Manually remove the extension from Chrome by going to `chrome://extensions/` and clicking **Remove**.

---

## How It Works

### 1. **VLC and Chrome Detection**
The installer automatically checks for VLC and Chrome installations in the default locations. If VLC is not found, you can browse to locate it manually.

### 2. **Directory Structure**
The installer creates the following directory structure in `%LOCALAPPDATA%\VLCOpener`:
- `extension/`: Contains the Chrome extension files (`manifest.json`, `background.js`, and icons).
- `native_host/`: Contains the native messaging host manifest (`com.vlc.opener.json`).
- `scripts/`: Contains the Python script (`vlc_opener.py`) that handles communication between Chrome and VLC.

### 3. **Native Messaging Host**
The installer registers a native messaging host with Chrome, allowing the extension to communicate with VLC. The host is defined in `com.vlc.opener.json` and uses a Python script to handle the communication protocol.

### 4. **Extension Files**
The installer generates the following files:
- `manifest.json`: Defines the Chrome extension's metadata and permissions.
- `background.js`: Handles the context menu and communicates with the native messaging host.
- Icons: Downloaded from the VLC repository for the extension's icons.

### 5. **Uninstaller**
The installer creates an uninstaller that removes the native messaging host registry entry and deletes the installation directory.

---

## File Structure

```
VLCOpener/
├── extension
│   ├── manifest.json
│   ├── background.js
│   └── icons
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── native_host
│   └── com.vlc.opener.json
└── scripts
    └── vlc_opener.py
```

---

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **VLC Media Player**: For providing an excellent open-source media player.
- **Google Chrome**: For supporting native messaging and extensions.

---

## Special Thanks

We extend our heartfelt gratitude to the [CyberUni.ir](https://cyberuni.ir) community. As a platform dedicated to advancing technology education, CyberUni.ir has been instrumental in providing the knowledge, inspiration, and collaborative environment that made this project possible. The developer proudly represents the CyberUni.ir community and its commitment to open-source innovation and technical excellence.

---

Enjoy streaming your media directly in VLC! 🎥🎶

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)