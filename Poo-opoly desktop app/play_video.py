import os
import subprocess
import sys

def play(file_path):
    if sys.platform.startswith("darwin"):  # macOS
        subprocess.call(["open", file_path])
    elif os.name == "nt":  # Windows
        os.startfile(file_path)
    elif os.name == "posix":  # Linux
        subprocess.call(["xdg-open", file_path])

