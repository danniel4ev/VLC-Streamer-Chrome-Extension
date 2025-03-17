import os
import sys
import ctypes
import subprocess
import winreg
import shutil
import urllib.request
import json
import tempfile
import webbrowser
from pathlib import Path
import winshell
from win32com.client import Dispatch
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading

APP_NAME = "VLC Streamer Chrome Extension"
APP_DIR = os.path.join(os.environ["LOCALAPPDATA"], "VLCOpener")
EXTENSION_DIR = os.path.join(APP_DIR, "extension")
NATIVE_HOST_DIR = os.path.join(APP_DIR, "native_host")
SCRIPTS_DIR = os.path.join(APP_DIR, "scripts")
TEMP_DIR = tempfile.gettempdir()
PYTHON_MIN_VERSION = (3, 9)

ICONS_DIR = os.path.join(APP_DIR, "icons")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def check_vlc():
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    ]
    
    for path in vlc_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_chrome():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\Application\chrome.exe")
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_python():
    if sys.version_info >= PYTHON_MIN_VERSION:
        return sys.executable
    
    return None

def install_python():
    python_url = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    python_installer = os.path.join(TEMP_DIR, "python_installer.exe")
    
    try:
        urllib.request.urlretrieve(python_url, python_installer)
        
        subprocess.run([python_installer, "/quiet", "InstallAllUsers=0", "PrependPath=1"], 
                      check=True, capture_output=True)
        
        return True
    except Exception as e:
        print(f"Error installing Python: {e}")
        return False

def create_files(vlc_path):
    os.makedirs(EXTENSION_DIR, exist_ok=True)
    os.makedirs(os.path.join(EXTENSION_DIR, "icons"), exist_ok=True)
    os.makedirs(NATIVE_HOST_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)
    
    manifest = {
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
    
    with open(os.path.join(EXTENSION_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Create background.js
    background_js = """
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
    """
    
    with open(os.path.join(EXTENSION_DIR, "background.js"), "w") as f:
        f.write(background_js)
    
    icon_urls = {
        "icon16.png": "https://raw.githubusercontent.com/videolan/vlc/master/share/icons/16x16/vlc.png",
        "icon48.png": "https://raw.githubusercontent.com/videolan/vlc/master/share/icons/48x48/vlc.png",
        "icon128.png": "https://raw.githubusercontent.com/videolan/vlc/master/share/icons/128x128/vlc.png"
    }

    for icon_name, url in icon_urls.items():
        try:
            urllib.request.urlretrieve(url, os.path.join(ICONS_DIR, icon_name))
        except Exception as e:
            print(f"Failed to download icon {icon_name}: {e}")
            with open(os.path.join(ICONS_DIR, icon_name), "wb") as f:
                f.write(b'')
    
    os.makedirs(os.path.join(EXTENSION_DIR, "icons"), exist_ok=True)
    for icon_name in icon_urls.keys():
        src_path = os.path.join(ICONS_DIR, icon_name)
        dst_path = os.path.join(EXTENSION_DIR, "icons", icon_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
    
    native_host_manifest = {
        "name": "com.vlc.opener",
        "description": "Open media in VLC",
        "path": os.path.join(SCRIPTS_DIR, "vlc_opener.bat").replace("\\", "\\\\"),
        "type": "stdio",
        "allowed_origins": ["chrome-extension://EXTENSION_ID/"]
    }
    
    with open(os.path.join(NATIVE_HOST_DIR, "com.vlc.opener.json"), "w") as f:
        json.dump(native_host_manifest, f, indent=2)
    
    vlc_opener_py = f"""
import sys
import json
import struct
import subprocess
import os

VLC_PATH = r"{vlc_path}"

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
            send_message({{"success": True}})
        except Exception as e:
            send_message({{"success": False, "error": str(e)}})
    else:
        send_message({{"success": False, "error": "No URL provided"}})

if __name__ == "__main__":
    main()
    """
    
    with open(os.path.join(SCRIPTS_DIR, "vlc_opener.py"), "w") as f:
        f.write(vlc_opener_py)
    
    vlc_opener_bat = f"""
@echo off
"{sys.executable}" "{os.path.join(SCRIPTS_DIR, 'vlc_opener.py')}"
    """
    
    with open(os.path.join(SCRIPTS_DIR, "vlc_opener.bat"), "w") as f:
        f.write(vlc_opener_bat)
    
    setup_extension_bat = """
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
    """
    
    with open(os.path.join(APP_DIR, "setup_extension.bat"), "w") as f:
        f.write(setup_extension_bat)
    
    uninstall_bat = """
@echo off
echo Uninstalling VLC Streamer Chrome Extension...
REG DELETE "HKCU\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.vlc.opener" /f
rmdir /s /q "%LOCALAPPDATA%\\VLCOpener"
echo Uninstallation complete. Please remove the extension from Chrome manually.
pause
    """
    
    with open(os.path.join(APP_DIR, "uninstall.bat"), "w") as f:
        f.write(uninstall_bat)

def create_uninstall_shortcut():
    try:
        import pythoncom
        pythoncom.CoInitialize()
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Uninstall VLC Streamer.lnk")
        target = os.path.join(APP_DIR, "uninstall.bat")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = APP_DIR
        shortcut.IconLocation = "shell32.dll,131"
        shortcut.save()
        
        pythoncom.CoUninitialize()
        
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} Installer")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        self.center_window()
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#0078D7")
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 11))
        self.style.configure("Body.TLabel", font=("Segoe UI", 10))
        
        self.main_frame = ttk.Frame(root, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.main_frame, text=f"Welcome to {APP_NAME} Installer", style="Header.TLabel").pack(pady=(0, 20))
        
        self.status_frame = ttk.LabelFrame(self.main_frame, text="System Check", padding="10 10 10 10")
        self.status_frame.pack(fill=tk.X, expand=False, pady=(0, 20))
        
        self.vlc_var = tk.StringVar(value="Checking...")
        self.chrome_var = tk.StringVar(value="Checking...")
        self.python_var = tk.StringVar(value="Checking...")
        
        ttk.Label(self.status_frame, text="VLC Media Player:", style="Body.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(self.status_frame, text="Google Chrome:", style="Body.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(self.status_frame, text="Python 3.9+:", style="Body.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(self.status_frame, textvariable=self.vlc_var, style="Body.TLabel").grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(self.status_frame, textvariable=self.chrome_var, style="Body.TLabel").grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(self.status_frame, textvariable=self.python_var, style="Body.TLabel").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        self.vlc_button = ttk.Button(self.status_frame, text="Browse", command=self.browse_vlc)
        self.python_button = ttk.Button(self.status_frame, text="Install", command=self.install_python)
        
        info_text = "This installer will set up the VLC Streamer Chrome Extension,\nwhich allows you to open media links directly in VLC from Chrome."
        ttk.Label(self.main_frame, text=info_text, style="Body.TLabel").pack(fill=tk.X, expand=False, pady=(0, 20))
        
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, expand=False, pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, expand=True)
        
        self.status_text = tk.StringVar(value="Ready to install")
        ttk.Label(self.progress_frame, textvariable=self.status_text, style="Body.TLabel").pack(anchor=tk.W, pady=(5, 0))
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, expand=False)
        
        self.install_button = ttk.Button(self.button_frame, text="Install", command=self.start_installation)
        self.install_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.root.destroy)
        self.cancel_button.pack(side=tk.RIGHT)
        
        self.check_system()
    
    def center_window(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        x = (width - 600) // 2
        y = (height - 450) // 2
        self.root.geometry(f"600x450+{x}+{y}")
    
    def check_system(self):
        vlc_path = check_vlc()
        if vlc_path:
            self.vlc_var.set(f"Found: {vlc_path}")
            self.vlc_status = True
            self.vlc_path = vlc_path
        else:
            self.vlc_var.set("Not found")
            self.vlc_status = False
            self.vlc_button.grid(row=0, column=2, padx=10)
        
        chrome_path = check_chrome()
        if chrome_path:
            self.chrome_var.set(f"Found: {chrome_path}")
            self.chrome_status = True
            self.chrome_path = chrome_path
        else:
            self.chrome_var.set("Not found - Please install Chrome")
            self.chrome_status = False
        
        python_path = check_python()
        if python_path:
            self.python_var.set(f"Found: Python {sys.version_info.major}.{sys.version_info.minor}")
            self.python_status = True
        else:
            self.python_var.set("Python 3.9+ not found")
            self.python_status = False
            self.python_button.grid(row=2, column=2, padx=10)
        
        self.update_install_button()
    
    def browse_vlc(self):
        vlc_path = filedialog.askopenfilename(
            title="Locate VLC Executable",
            filetypes=[("Executable files", "*.exe")],
            initialdir="C:\\Program Files\\VideoLAN\\VLC"
        )
        
        if vlc_path and os.path.exists(vlc_path) and os.path.basename(vlc_path).lower() == "vlc.exe":
            self.vlc_path = vlc_path
            self.vlc_var.set(f"Found: {vlc_path}")
            self.vlc_status = True
            self.vlc_button.grid_forget()
            self.update_install_button()
        elif vlc_path:
            messagebox.showerror("Invalid Selection", "Please select the VLC executable (vlc.exe)")
    
    def install_python(self):
        self.status_text.set("Installing Python 3.11...")
        self.progress_var.set(10)
        self.root.update()
        
        def do_install():
            success = install_python()
            if success:
                self.python_var.set("Python 3.11 installed")
                self.python_status = True
                self.python_button.grid_forget()
            else:
                self.python_var.set("Failed to install Python")
                messagebox.showerror("Installation Error", 
                                    "Failed to install Python. Please install Python 3.9 or higher manually.")
            
            self.status_text.set("Ready to install")
            self.progress_var.set(0)
            self.update_install_button()
        
        threading.Thread(target=do_install).start()
    
    def update_install_button(self):
        if not self.vlc_status or not self.chrome_status:
            self.install_button["state"] = "disabled"
        else:
            self.install_button["state"] = "normal"
    
    def start_installation(self):
        self.install_button["state"] = "disabled"
        self.cancel_button["state"] = "disabled"
        
        if hasattr(self, 'vlc_button') and self.vlc_button.winfo_ismapped():
            self.vlc_button["state"] = "disabled"
        
        if hasattr(self, 'python_button') and self.python_button.winfo_ismapped():
            self.python_button["state"] = "disabled"
        
        threading.Thread(target=self.perform_installation).start()
    
    def perform_installation(self):
        try:
            self.status_text.set("Creating directories...")
            self.progress_var.set(15)
            self.root.update()
            
            # Create all necessary files
            create_files(self.vlc_path)
            
            self.status_text.set("Registering native messaging host...")
            self.progress_var.set(50)
            self.root.update()
            
            # Register in Windows registry
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                 r"Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener")
            winreg.SetValue(key, "", winreg.REG_SZ, 
                          os.path.join(NATIVE_HOST_DIR, "com.vlc.opener.json"))
            winreg.CloseKey(key)
            
            self.status_text.set("Creating shortcuts...")
            self.progress_var.set(75)
            self.root.update()
            
            create_uninstall_shortcut()
            
            self.status_text.set("Installation complete!")
            self.progress_var.set(100)
            
            self.root.after(500, self.show_completion_dialog)
            
        except Exception as e:
            self.status_text.set(f"Error: {str(e)}")
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n{str(e)}")
            
            self.install_button["state"] = "normal"
            self.cancel_button["state"] = "normal"
    
    def show_completion_dialog(self):
        result = messagebox.askyesno("Installation Complete", 
                        f"VLC Streamer has been installed successfully!\n\n"
                        f"Would you like to complete the setup now? This will:\n"
                        f"1. Open Chrome extensions page\n"
                        f"2. Open the extension folder for you to load\n"
                        f"3. Guide you through entering the Extension ID")
        
        if result:
            subprocess.Popen([self.chrome_path, "chrome://extensions/"])
            
            os.startfile(EXTENSION_DIR)
            
            messagebox.showinfo("Load Extension", 
                            "In Chrome:\n"
                            "1. Enable Developer Mode (toggle in top right)\n"
                            "2. Click 'Load unpacked'\n"
                            "3. Select the folder that just opened\n\n"
                            "Click OK when you've loaded the extension.")
            
            self.prompt_for_extension_id()
        else:
            os.startfile(APP_DIR)
            self.root.destroy()

    def prompt_for_extension_id(self):
        id_dialog = tk.Toplevel(self.root)
        id_dialog.title("Enter Extension ID")
        id_dialog.geometry("500x250")
        id_dialog.resizable(False, False)
        
        width = id_dialog.winfo_screenwidth()
        height = id_dialog.winfo_screenheight()
        x = (width - 500) // 2
        y = (height - 250) // 2
        id_dialog.geometry(f"500x250+{x}+{y}")
        
        id_dialog.transient(self.root)
        id_dialog.grab_set()
        
        frame = ttk.Frame(id_dialog, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Enter Chrome Extension ID", style="Header.TLabel").pack(pady=(0, 10))
        
        ttk.Label(frame, text="Find the ID in Chrome extensions page under the extension name.\nIt looks like: 'abcdefghijklmnopqrstuvwxyzabcdef'", 
                 style="Body.TLabel").pack(pady=(0, 15))
        
        extension_id = tk.StringVar()
        id_entry = ttk.Entry(frame, textvariable=extension_id, width=50)
        id_entry.pack(pady=(0, 20))
        id_entry.focus()
        
        def apply_extension_id():
            ext_id = extension_id.get().strip()
            if not ext_id:
                messagebox.showerror("Error", "Please enter the Extension ID")
                return
                
            try:
                manifest_path = os.path.join(NATIVE_HOST_DIR, "com.vlc.opener.json")
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                manifest["allowed_origins"] = [f"chrome-extension://{ext_id}/"]
                
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
                
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                     r"Software\Google\Chrome\NativeMessagingHosts\com.vlc.opener")
                winreg.SetValue(key, "", winreg.REG_SZ, 
                              os.path.join(NATIVE_HOST_DIR, "com.vlc.opener.json"))
                winreg.CloseKey(key)
                
                messagebox.showinfo("Setup Complete", 
                                  "The VLC Streamer extension is now fully configured!\n\n"
                                  "You can now right-click on media links in Chrome and select 'Open in VLC'.")
                id_dialog.destroy()
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update Extension ID: {str(e)}")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, expand=False)
        
        ttk.Button(button_frame, text="Apply", command=apply_extension_id).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=lambda: [id_dialog.destroy(), self.root.destroy()]).pack(side=tk.RIGHT)

def main():
    if not is_admin():
        restart_as_admin()
    
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()