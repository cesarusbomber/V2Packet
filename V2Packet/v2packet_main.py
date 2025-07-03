from scapy.all import *
from colorama import init, Fore
import time
import datetime
import subprocess
import os
import random
import platform
import socket
import sys
import requests
import json
import threading
import ipaddress

from youshallnotpass.youshallnotpass_writer import write_creepy_file

init(autoreset=True)

# -------------------------------
# Localization
# -------------------------------

def load_localisation(lang="en"):
    path = f"localisation/{lang}.json"
    if not os.path.exists(path):
        path = "localisation/en.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# -------------------------------
# IP Validation
# -------------------------------

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# -------------------------------
# Country Lookup
# -------------------------------

def lookup_country(ip):
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = resp.json()
        return data.get("country", "[Unknown]")
    except:
        return "[Unknown]"

# -------------------------------
# Logging
# -------------------------------

def log_packet(packet_size, message, target_ip, source_ip, lang, localisation):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    country = lookup_country(target_ip)
    log_line = f"[{timestamp}] | {packet_size} bytes | {message} | → {target_ip} | ← {source_ip} | Country: {country}\n"

    os.makedirs("packetlogs", exist_ok=True)
    with open("packetlogs/session.log", "a", encoding="utf-8") as f:
        f.write(log_line)

    os.makedirs("iplogged", exist_ok=True)
    with open(f"iplogged/{target_ip}.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

# -------------------------------
# Progress Bar
# -------------------------------

def silly_progress(current, total):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "▓" * filled + "░" * (bar_len - filled)
    percent = (current / total) * 100
    print(f"{Fore.MAGENTA}[{bar}] {percent:.1f}% ({current}/{total} packets sent)")

# -------------------------------
# Send Packets
# -------------------------------

def send_packets(protocol, targets, payload, count, ports=None, flags=None, lang="en", localisation={}):
    total_packets = len(targets) * count
    sent = 0

    for ip in targets:
        for i in range(count):
            if protocol == "ICMP":
                packet = IP(dst=ip)/ICMP()/payload
            elif protocol == "UDP":
                packet = IP(dst=ip)/UDP(dport=ports["dport"], sport=ports["sport"])/payload
            elif protocol == "TCP":
                packet = IP(dst=ip)/TCP(dport=ports["dport"], sport=ports["sport"], flags=flags)/payload
            else:
                print(Fore.RED + localisation["invalid_option"])
                return

            send(packet, verbose=False)
            silly_progress(sent+1, total_packets)
            log_packet(len(payload), payload.decode(errors='ignore'), ip, packet[IP].src, lang, localisation)
            sent += 1

            time.sleep(0.05)

    print(Fore.GREEN + localisation["sending_packets"])

# -------------------------------
# Safety Reminder
# -------------------------------

def safety_reminder(localisation):
    while True:
        time.sleep(600)
        print(Fore.RED + "\n⚠️ " + localisation["operation_cancelled"] + " ⚠️\n")

# -------------------------------
# Mustard Easter Egg
# -------------------------------

def mustard_easter_egg(user_ip, localisation, lang):
    print(Fore.RED + localisation["mustard_text"])
    payload = b"mustord"
    send_packets("UDP", [user_ip], payload, 69,
                 ports={"dport": 12345, "sport": 54321},
                 lang=lang,
                 localisation=localisation)

# -------------------------------
# Fake DDOS
# -------------------------------

def fake_ddos_attack(target_ip):
    print(Fore.RED + "Launching DDoS attack... JUST KIDDING! FUCK YOU RETARD")

    batch_content = r"""
@echo off
:loop
echo YOU GOT OWNED BY THE REAL MVP!
timeout /t 2 >nul
goto loop
"""
    batch_path = "troll.bat"
    with open(batch_path, "w") as f:
        f.write(batch_content)

    try:
        for _ in range(69):
            subprocess.Popen(['cmd.exe', '/k', batch_path])
            packet = IP(dst=target_ip)/UDP(dport=12345, sport=54321)/b"mustord"
            send(packet, verbose=False)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        if os.path.exists(batch_path):
            os.remove(batch_path)

# -------------------------------
# Noise Mode
# -------------------------------

def noise_mode():
    print(Fore.YELLOW + "Entering Noise Mode...")
    for i in range(5):
        target = f"192.168.1.{random.randint(2, 254)}"
        send(IP(dst=target)/ICMP()/"noise", verbose=False)
        print(f"Sent noise packet to {target}")
        time.sleep(0.2)
    print(Fore.GREEN + "Noise Mode complete.")

# -------------------------------
# System Info
# -------------------------------

def system_info():
    print(Fore.MAGENTA + f"PC Name: {platform.node()}")
    print(Fore.MAGENTA + f"OS: {platform.system()} {platform.release()}")
    print(Fore.MAGENTA + f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(Fore.MAGENTA + f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")

    try:
        result = subprocess.check_output("netsh wlan show interfaces", shell=True, encoding="utf-8")
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                print(Fore.MAGENTA + f"Wi-Fi SSID: {line.split(':')[1].strip()}")
    except:
        print(Fore.MAGENTA + "Wi-Fi SSID: [Unavailable]")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        print(Fore.MAGENTA + f"Local IPv4: {ip}")
        s.close()
    except:
        print(Fore.MAGENTA + f"Local IPv4: Unknown")

    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        data = resp.json()
        print(Fore.MAGENTA + f"Public IP: {data.get('ip', '[Unknown]')}")
        print(Fore.MAGENTA + f"ISP: {data.get('org', '[Unknown]')}")
        print(Fore.MAGENTA + f"Location: {data.get('city', '[Unknown]')}, {data.get('country', '[Unknown]')}")
    except:
        print(Fore.MAGENTA + "Public IP, ISP, Location: [Unavailable]")

# -------------------------------
# MAIN PROGRAM
# -------------------------------

# Creepy file on startup
write_creepy_file()

# Language
lang = input("Select Language / Sélectionner la langue (EN/FR): ").strip().lower()
if lang not in ["en", "fr"]:
    lang = "en"

localisation = load_localisation(lang)
print(Fore.YELLOW + localisation["welcome"])

# Agreement
print(Fore.YELLOW + localisation["agree_prompt"])
agree = input(Fore.YELLOW + localisation["agree_question"]).strip().lower()
if agree != "y":
    print(Fore.RED + localisation["refused"])
    sys.exit(0)

# Safety reminder thread
reminder_thread = threading.Thread(target=safety_reminder, args=(localisation,), daemon=True)
reminder_thread.start()

while True:
    print(Fore.CYAN + "\nChoose an option:")
    print("1. Custom Packet Sender [CPS]")
    print("2. Noise Mode")
    print("3. View Logs")
    print("4. System Info")
    print("5. Mustard Easter Egg")
    print("6. Fake DDOS Prank")
    print("7. Exit")

    choice = input(Fore.CYAN + "Enter choice: ").strip().lower()

    if choice == "7":
        print(Fore.YELLOW + localisation["goodbye_final"])
        break

    if choice == "3":
        if os.path.exists("packetlogs/session.log"):
            with open("packetlogs/session.log", encoding="utf-8") as f:
                print(Fore.GREEN + f.read())
        else:
            print(Fore.YELLOW + localisation["logs_empty"])
        continue

    if choice == "4":
        system_info()
        continue

    if choice == "5":
        # Mustard
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            user_ip = s.getsockname()[0]
            s.close()
        except:
            user_ip = None

        if user_ip:
            mustard_easter_egg(user_ip, localisation, lang)
        else:
            print(Fore.RED + "Cannot determine your IP for mustard prank.")
        continue

    if choice == "6":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            target_ip = s.getsockname()[0]
            s.close()
        except:
            target_ip = None

        if target_ip:
            fake_ddos_attack(target_ip)
        else:
            print(Fore.RED + "Cannot determine your IP for fake DDOS.")
        continue

    if choice == "2":
        noise_mode()
        continue

    if choice == "1":
        targets_input = input(Fore.CYAN + "Enter target IP(s), separated by commas: ")
        targets = [ip.strip() for ip in targets_input.split(",")]
        targets = [ip for ip in targets if validate_ip(ip)]

        if not targets:
            print(Fore.RED + localisation["no_valid_ip"])
            continue

        print(Fore.CYAN + "Select protocol:")
        print("1. ICMP")
        print("2. UDP")
        print("3. TCP")
        proto_choice = input("Choice: ").strip()
        protocol = "ICMP" if proto_choice == "1" else "UDP" if proto_choice == "2" else "TCP"

        msg = input("Enter payload text: ").strip()
        payload = msg.encode()

        if len(payload) > 10000:
            print(Fore.RED + localisation["payload_large"])

        ports = None
        flags = None
        if protocol in ["UDP", "TCP"]:
            dport = int(input("Destination port: "))
            sport = int(input("Source port: "))
            ports = {"dport": dport, "sport": sport}
        if protocol == "TCP":
            flags = "R"

        count = int(input("How many packets to send? "))
        send_packets(protocol, targets, payload, count, ports, flags, lang, localisation)
