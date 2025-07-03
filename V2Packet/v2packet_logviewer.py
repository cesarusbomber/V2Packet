import time
import os
from colorama import init, Fore

init(autoreset=True)

LOG_FILE = "v2packet_logs.tmp"

def tail_f(logfile):
    with open(logfile, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)  # Move to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2) # <-- remove this spam machine, we get it the first time.
                continue
            print(Fore.GREEN + line.strip())

if __name__ == "__main__": # <-- who the fuck made this?
    print(Fore.CYAN + "==== LIVE PACKET LOGS ====\n")
    # Wait until the log file exists
    while not os.path.exists(LOG_FILE):
        print(Fore.YELLOW + f"Waiting for log file to be created: {LOG_FILE}")
        time.sleep(1)

    tail_f(LOG_FILE)

# Hey buddy! This doesn't work. It will be planned to be rescripted.
