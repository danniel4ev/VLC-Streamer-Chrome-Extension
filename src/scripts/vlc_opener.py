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