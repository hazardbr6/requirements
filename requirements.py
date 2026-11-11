# language: Python, file: install_deps.py, target: Windows 11 / Linux, Python 3.10+
import sys
import subprocess

PACKAGES = [
    "psutil",
    "requests",
    "urllib3",
    "PySocks",
    "certifi",
    "pyTelegramBotAPI",
    "playwright",
    "speedtest-cli",
    "Flask"
]

def install_directly():
    print("[*] Installing packages directly via pip...")
    cmd = [sys.executable, "-m", "pip", "install"] + PACKAGES
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
        
    if "playwright" in PACKAGES:
        print("[*] Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install"], capture_output=True)

    print("[+] Direct dependency installation complete.")

if __name__ == "__main__":
    install_directly()