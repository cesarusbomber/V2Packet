from scapy.all import *
from colorama import init, Fore, Style
import time
import datetime
import winsound
import subprocess
import os
import random
import platform
import socket
import sys
import requests
import json
import threading

init(autoreset=True)

LOG_FILE = "v2packet_logs.tmp"

# ============ CONFIG ===============

QUOTES = [
    "With great power comes great responsibility.",
    "Don’t become the monster you’re fighting.",
    "Knowledge is power… and power can get you jailed.",
    "Packets never lie.",
    "Stay safe, stay ethical.",
    "Your WiFi hates you right now.",
    "Hack the planet!",
    "One packet at a time.",
    "Are you sure you want to do this?",
    "The logs remember everything.",
    "Don’t be a skid.",
    "Your mom uses Wireshark.",
    "TCP loves you… sometimes.",
    "UDP: Unreliable but fast.",
    "ICMP says hello.",
    "Remember the legal disclaimers.",
    "Don’t poke the bear.",
    "Beware the digital paper trail.",
    "Everything is traceable.",
    "The FBI is watching.",
]

DANGER_PACKET_SIZE = 10000       # bytes
DANGER_PACKET_COUNT = 500        # packets

SAFETY_REMINDER_INTERVAL = 600   # 10 minutes (seconds)

# ============ FUNCTIONS ===============

def typing(text, speed=0.03):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(speed)
    print()

def play_sound(style="normal"):
    try:
        if style == "normal":
            winsound.Beep(1000, 300)
        elif style == "laser":
            for freq in range(800, 1400, 100):
                winsound.Beep(freq, 50)
        elif style == "buzz":
            winsound.Beep(200, 700)
    except:
        print(Fore.YELLOW + "Beep not supported on this system.")

def safe_confirm(msg):
    confirm = input(Fore.YELLOW + f"{msg} Proceed? (Y/N): ").strip().lower()
    return confirm == "y"

def log_packet(packet_size, message, target_ip, source_ip):
    message = clean_payload(message)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] | {packet_size} bytes | {message} | → {target_ip} | ← {source_ip}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

def clean_payload(payload):
    words_to_remove = ["gmail.com", "hotmail", "facebook", "192.168.", "127.0.0.1"]
    for word in words_to_remove:
        payload = payload.replace(word, "[CENSORED]")
    return payload

def random_quote():
    print(Fore.YELLOW + random.choice(QUOTES))

def silly_progress(current, total):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "▓" * filled + "░" * (bar_len - filled)
    percent = (current / total) * 100
    print(f"{Fore.MAGENTA}[{bar}] {percent:.1f}% ({current}/{total} packets sent)")

def packet_preview(protocol, targets, payload, ports=None, flags=None):
    print(Fore.CYAN + "\nPacket Preview:")
    sample_ip = targets[0] if targets else "0.0.0.0"
    if protocol == "ICMP":
        packet = IP(dst=sample_ip)/ICMP()/payload
    elif protocol == "UDP":
        packet = IP(dst=sample_ip)/UDP(dport=ports["dport"], sport=ports["sport"])/payload
    elif protocol == "TCP":
        packet = IP(dst=sample_ip)/TCP(dport=ports["dport"], sport=ports["sport"], flags=flags)/payload
    elif protocol == "ARP":
        packet = ARP(pdst=sample_ip)
    elif protocol == "DNS":
        packet = IP(dst=sample_ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="example.com"))
    else:
        print(Fore.RED + "Unsupported protocol for preview.")
        return

    packet.show()
    print()

def send_packets(protocol, targets, payload, count, ports=None, flags=None, sound_style="normal"):
    total_packets = len(targets) * count
    sent = 0
    total_bytes = 0
    start_time = time.time()

    for ip in targets:
        for i in range(count):
            if protocol == "ICMP":
                packet = IP(dst=ip)/ICMP()/payload
            elif protocol == "UDP":
                packet = IP(dst=ip)/UDP(dport=ports["dport"], sport=ports["sport"])/payload
            elif protocol == "TCP":
                packet = IP(dst=ip)/TCP(dport=ports["dport"], sport=ports["sport"], flags=flags)/payload
            elif protocol == "ARP":
                packet = ARP(pdst=ip)
            elif protocol == "DNS":
                packet = IP(dst=ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname="example.com"))
            else:
                print(Fore.RED + f"Unsupported protocol: {protocol}")
                return

            send(packet, verbose=False)

            silly_progress(sent + 1, total_packets)
            log_packet(len(payload), payload.decode(errors='ignore'), ip, packet[IP].src if IP in packet else "N/A")

            total_bytes += len(payload)
            sent += 1

            random_quote()
            time.sleep(0.05)

    duration = time.time() - start_time
    avg_time = duration / total_packets if total_packets > 0 else 0

    print(Fore.GREEN + f"\nSession Summary:")
    print(Fore.GREEN + f"✅ Total packets sent: {total_packets}")
    print(Fore.GREEN + f"✅ Total bytes sent: {total_bytes} bytes")
    print(Fore.GREEN + f"✅ Different targets: {len(set(targets))}")
    print(Fore.GREEN + f"✅ Total time: {duration:.2f} seconds")
    print(Fore.GREEN + f"✅ Avg time per packet: {avg_time:.4f} seconds")

    play_sound(sound_style)

def noise_mode():
    typing(Fore.YELLOW + "Entering Noise Mode... sending random harmless ICMP packets on your network.", 0.02)
    for i in range(20):
        target = f"192.168.1.{random.randint(2, 254)}"
        payload = b"noise_test"
        send(IP(dst=target)/ICMP()/payload, verbose=False)
        print(Fore.BLUE + f"Sent noise packet to {target}")
        time.sleep(0.2)
    print(Fore.GREEN + "Noise Mode complete.")

def view_logs():
    if not os.path.exists(LOG_FILE):
        print(Fore.YELLOW + "No logs yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            print(Fore.YELLOW + "Log file empty.")
            return

        print(Fore.CYAN + "\n===== Logs =====")
        for line in lines:
            print(Fore.GREEN + line.strip())
        print(Fore.CYAN + "================\n")

def system_info():
    typing(Fore.MAGENTA + f"PC Name: {platform.node()}")
    typing(Fore.MAGENTA + f"OS: {platform.system()} {platform.release()}")
    typing(Fore.MAGENTA + f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    typing(Fore.MAGENTA + f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")

    try:
        result = subprocess.check_output("netsh wlan show interfaces", shell=True, encoding="utf-8")
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                typing(Fore.MAGENTA + f"Wi-Fi SSID: {line.split(':')[1].strip()}")
    except:
        typing(Fore.MAGENTA + "Wi-Fi SSID: [Unavailable]")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        typing(Fore.MAGENTA + f"Your local IPv4: {ip}")
        s.close()
    except:
        typing(Fore.MAGENTA + f"Your local IPv4: Unknown")

    # Public IP, ISP, Location
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        typing(Fore.MAGENTA + f"Public IP: {data.get('ip', '[Unknown]')}")
        typing(Fore.MAGENTA + f"ISP: {data.get('org', '[Unknown]')}")
        typing(Fore.MAGENTA + f"Location: {data.get('city', '[Unknown]')}, {data.get('country', '[Unknown]')}")
    except:
        typing(Fore.MAGENTA + "Public IP, ISP, Location: [Unavailable]")

def safety_reminder():
    while True:
        time.sleep(SAFETY_REMINDER_INTERVAL)
        print(Fore.RED + "\n⚠️ Reminder: Use this tool ethically and legally! Unauthorized use can have consequences. ⚠️\n")

def fake_ddos_attack(target_ip):
    typing(Fore.RED + "Launching DDoS attack... JUST KIDDING! FUCK YOU RETARD", 0.03)
    time.sleep(1)

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
            # Also send a fake packet (mustord)
            packet = IP(dst=target_ip)/UDP(dport=12345, sport=54321)/b"mustord"
            send(packet, verbose=False)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        if os.path.exists(batch_path):
            os.remove(batch_path)

# ============ MAIN ===============

if __name__ == "__main__":
    # AGREEMENT PROMPT
    print(Fore.RED + """
============================================================
░█▀▀█ ░█▀▀▀ ░█─▄▀ ░█▀▀▀█ ░█▀▀█ ░█▀▀█ ░█▀▀▀ ░█▀▀█ ░█▀▄▀█ 
░█─── ░█▀▀▀ ░█▀▄─ ░█──░█ ░█─── ░█─── ░█▀▀▀ ░█─── ░█░█░█ 
░█▄▄█ ░█▄▄▄ ░█─░█ ░█▄▄▄█ ░█▄▄█ ░█▄▄█ ░█▄▄▄ ░█▄▄█ ░█──░█ 
============================================================
""")
  
    typing(Fore.YELLOW + "⚠️  You must agree to the terms of this tool. Using it without permission is illegal.", 0.02)
    agree = input(Fore.YELLOW + "Do you agree? (Y/N): ").strip().lower()

    if agree != "y":
        # Gather scary info
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "[unknown]"

        pc_name = platform.node()

        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            country = response.json().get("country", "[Unavailable]")
        except:
            country = "[Unavailable]"

        print(Fore.RED + f"\nYou refused the agreement.")
        print(Fore.RED + f"Your local IP: {local_ip}")
        print(Fore.RED + f"Your PC name: {pc_name}")
        print(Fore.RED + f"Your country: {country}")
        print(Fore.RED + "The script will now log you and SWAT you..")
        time.sleep(5)
        sys.exit(0)

    # Remove old logs
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    # Start safety reminder thread
    reminder_thread = threading.Thread(target=safety_reminder, daemon=True)
    reminder_thread.start()

    # LANGUAGE
    lang = input(Fore.CYAN + "Select Language / Sélectionner la langue (EN/FR): ").strip().lower()
    if lang == "fr":
        print(Fore.YELLOW + "→ Bonjour! Bienvenue dans V2Packet.")
    else:
        lang = "en"
        print(Fore.YELLOW + "→ Hello! Welcome to V2Packet.")

    # SOUND THEME
    print(Fore.CYAN + "Choose your sound style:")
    print("1. Normal beep")
    print("2. Laser beep")
    print("3. Buzz error sound")
    choice_sound = input("Choice (1-3): ").strip()
    sound_style = "normal"
    if choice_sound == "2":
        sound_style = "laser"
    elif choice_sound == "3":
        sound_style = "buzz"

    while True:
        typing(Fore.CYAN + "\nChoose an option:", 0.02)
        print("1. Custom Packet Sender [CPS]")
        print("2. Debugging Packet Sender [DPS]")
        print("3. RST Packet Sender [RSTPS]")
        print("4. Noise Mode")
        print("5. View Logs")
        print("6. Show System Info")
        print("7. DDOS (Fake)")
        print("8. Exit\n")

        choice = input(Fore.CYAN + "Enter choice (1-8): ").strip().lower()

        # SECRET MUSTARD OPTION
        if choice == "mustard":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                user_ip = s.getsockname()[0]
                s.close()
            except:
                user_ip = None

            if user_ip:
                typing(Fore.RED + "Aww mustard! Come on man, now don’t put no mustard on that you need to put a little season on that thing! WHAT! Man come on get that pepper off there! Come on somebody come get this man! Come on now, come on get that pepper off there, that’s just too much doggone pepper. I dont wanna see this no more", 0.03)
                # Send 69 packets with payload "mustord" to user IP
                count = 69
                payload = b"mustord"
                protocol = "UDP"
                ports = {"dport":12345, "sport":54321}
                send_packets(protocol, [user_ip], payload, count, ports, None, sound_style)
            else:
                print(Fore.RED + "Cannot determine your IP for the mustard prank.")
            continue

        if choice == "8":
            print(Fore.GREEN + "Goodbye!")
            break

        if choice == "5":
            view_logs()
            continue

        if choice == "4":
            noise_mode()
            continue

        if choice == "6":
            system_info()
            continue

        if choice == "7":
            # fake ddos attack to user IP
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
                print(Fore.RED + "Cannot determine your IP for the fake DDoS prank.")
            continue

        targets_input = input(Fore.CYAN + "Enter target IP(s), separated by commas: ").strip()
        targets = [ip.strip() for ip in targets_input.split(",") if ip.strip()]

        print(Fore.CYAN + "\nSelect protocol:")
        print("1. ICMP")
        print("2. UDP")
        print("3. TCP")
        print("4. ARP (fake)")
        print("5. DNS (fake)")
        proto_choice = input(Fore.CYAN + "Enter choice (1-5): ").strip()

        if proto_choice == "1":
            protocol = "ICMP"
        elif proto_choice == "2":
            protocol = "UDP"
        elif proto_choice == "3":
            protocol = "TCP"
        elif proto_choice == "4":
            protocol = "ARP"
        elif proto_choice == "5":
            protocol = "DNS"
        else:
            print(Fore.RED + "Invalid protocol. Returning to main menu.")
            continue

        size_input = input(Fore.CYAN + "Payload size in bytes (enter 0 for auto size): ").strip()
        try:
            size = int(size_input)
        except:
            print(Fore.RED + "Invalid size.")
            continue

        msg = input(Fore.CYAN + "Enter message content: ").strip()
        if size == 0:
            size = len(msg.encode())
        else:
            msg = (msg * ((size // len(msg)) + 1))[:size]

        payload = msg.encode()

        if size >= DANGER_PACKET_SIZE:
            print(Fore.RED + "⚠ Payload size is very large. This could be suspicious.")

        ports = None
        flags = None
        if protocol in ["UDP", "TCP"]:
            try:
                dport = int(input(Fore.CYAN + "Enter destination port: ").strip())
                sport = int(input(Fore.CYAN + "Enter source port: ").strip())
            except:
                print(Fore.RED + "Invalid ports.")
                continue
            ports = {"dport": dport, "sport": sport}

        if choice == "3" or (protocol == "TCP" and choice in ["1", "2"]):
            flags = "R"

        # Packet preview before sending
        packet_preview(protocol, targets, payload, ports, flags)
        if not safe_confirm("Send these packets?"):
            print(Fore.YELLOW + "Operation cancelled.\n")
            continue

        try:
            count = int(input(Fore.CYAN + "How many packets to send? (max 888): ").strip())
            if count < 1 or count > 888:
                print(Fore.RED + "Out of range.")
                continue
        except:
            print(Fore.RED + "Invalid number.")
            continue

        if count > DANGER_PACKET_COUNT:
            print(Fore.RED + "⚠ High packet count detected. Are you sure you want to proceed?")
            if not safe_confirm("Confirm high packet count"):
                print(Fore.YELLOW + "Operation cancelled.\n")
                continue

        confirm_msg = f"You are about to send {len(targets)*count} packets using {protocol}."
        if not safe_confirm(confirm_msg):
            print(Fore.YELLOW + "Operation cancelled.\n")
            continue

        send_packets(protocol, targets, payload, count, ports, flags, sound_style)
