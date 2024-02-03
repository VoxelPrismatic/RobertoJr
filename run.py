import os
import hashlib
import subprocess
import signal
import time

hashes = {}
PWD = os.environ["PWD"] + "/"

def compare_hashes():
    global hashes
    changed = False
    for dir_name, dir_listing, file_listing in os.walk(PWD):
        for file_name in file_listing:
            if not file_name.endswith(".py"):
                continue
            path = dir_name + "/" + file_name
            text = open(path, "rb").read()
            checksum = hashlib.sha512(text).hexdigest()
            if path not in hashes or hashes[path] != checksum:
                hashes[path] = checksum
                changed = True
    return changed

compare_hashes()

while True:
    open(PWD + "stderr", "w+").write("")
    open(PWD + "stdout", "w+").write("")

    proc = subprocess.Popen(["python3", "."], stdout = open(PWD + "stdout", "w"), stderr = open(PWD + "stderr", "w"))

    while proc.poll() is None or compare_hashes() is None:
        time.sleep(5)

    if proc.poll() is None:
        proc.terminate()
        print("\x1b[94;1mCODE CHANGED\x1b[0m")
    else:
        print("\x1b[93;1mBOT DIED\x1b[0m")
