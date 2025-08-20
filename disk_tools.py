#!/usr/bin/env python3

import subprocess
import json
import sys

def get_disk_info():
    """
    Kör kommandot 'lsblk' för att hämta information om alla block-enheter.
    Använder --json-flaggan för att få strukturerad och pålitlig output.
    Returnerar informationen som ett Python-objekt (dictionary).
    """
    try:
        # Kommando för att lista enheter med specifik information i JSON-format
        command = [
            "lsblk",
            "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT",
            "--json"
        ]
        
        # Kör kommandot
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True, # Kraschar om lsblk returnerar en felkod
            encoding='utf-8'
        )
        
        # Konvertera JSON-strängen från stdout till en Python dictionary
        return json.loads(result.stdout)

    except FileNotFoundError:
        print("Fel: Kommandot 'lsblk' hittades inte. Se till att du kör på Linux.", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Fel vid körning av lsblk: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print("Fel: Kunde inte tolka JSON-output från lsblk.", file=sys.stderr)
        return None

def display_disk_info(data):
    """
    Tar emot disk-information som ett Python-objekt och skriver ut det
    i ett lättläst, hierarkiskt format.
    """
    print("--- Tillgängliga diskar och partitioner ---")
    if not data or 'blockdevices' not in data:
        print("Ingen information om diskenheter hittades.")
        return

    for device in data['blockdevices']:
        # Vi är oftast bara intresserade av faktiska diskar, inte loop-enheter etc.
        if device.get('type') == 'disk':
            print(f"\n[Disk] /dev/{device.get('name', 'N/A')} (Storlek: {device.get('size', 'N/A')})")
            
            # Kolla om disken har partitioner ("children")
            if 'children' in device:
                for partition in device['children']:
                    fstype = partition.get('fstype', 'inget')
                    mountpoint = partition.get('mountpoint', 'ej monterad')
                    
                    print(f"  └─ [Part] /dev/{partition.get('name', 'N/A')} "
                          f"({partition.get('size', 'N/A')}) "
                          f"| Filsystem: {fstype} "
                          f"| Monterad på: {mountpoint}")
    print("\n-------------------------------------------")

def display_disk_devs(data):
    print("****-List of Disk Devices-****")
    if not data or 'blockdevices' not in data:
        print("****-No disk devices found-****")
        return
    
    for device in data['blockdevices']:
        if device.get('type') == 'disk':
            print(f"/dev/{device.get('name', 'N/A')} (Size: {device.get('size', 'N/A')})")
            if 'children' in device:
                pass # This block was empty, so we add a 'pass' to make it syntactically correct.
    print("\n-------------------------------------------")

def Disk_info():
    """
    Huvudfunktionen för skriptet.
    """
    disk_data = get_disk_info()
    
    if disk_data:
        print("Disk-information hämtad framgångsrikt.")
        print("***********************")
        
        main_menu_options = {
            "1": "Full output of lsblk?",
            "2": "Show devices only"
        }
        
        # --- HÄR ÄR ÄNDRINGARNA ---
        
        # 1. VISA MENYN för användaren
        print("Please choose an option:")
        for key, value in main_menu_options.items():
            print(f"[{key}] {value}")
        
        # 2. HÄMTA INPUT från användaren och spara i en ny variabel
        choice = input("Your choice: ")
        
        # 3. JÄMFÖR ANVÄNDARENS SVAR (variabeln 'choice')
        if choice == "1":
            display_disk_info(disk_data)
        elif choice == "2":
            display_disk_devs(disk_data)
        else:
            print(f'"{choice}" is not a valid option.')

        
    print("\nDo you want to select a device for inspection? (yes/no)")
    user_input = input()

    if user_input.lower().startswith('y'):
        # Skapa en lista över tillgängliga diskar
        available_disks = [
            dev for dev in disk_data['blockdevices'] if dev.get('type') == 'disk'
        ]
        
        if not available_disks:
            print("No disks found to inspect.")
            return

        # Bygg en meny dynamiskt från listan
        disk_menu_options = {
            str(i + 1): f"/dev/{disk['name']}" for i, disk in enumerate(available_disks)
        }

        # Använd din befintliga meny-funktion för att låta användaren välja
        # Notera: Vi behöver inte bekräfta detta val, så vi skriver en enklare loop.
        print("\nPlease select a device:")
        for key, value in disk_menu_options.items():
            print(f"[{key}] {value}")
        
        device_choice = input("Your choice: ")

        if device_choice in disk_menu_options:
            selected_device_path = disk_menu_options[device_choice]
            print(f"Device selected: {selected_device_path}")
            inspect_device(selected_device_path)
        else:
            print(f'"{device_choice}" is not a valid option.')
def get_confirmed_choice(title, options):
    """
    Visar en meny, ber användaren göra ett val och bekräfta det.
    Returnerar det bekräftade valet.
    """
    while True: # En evighetsloop som vi bryter oss ur med 'return'
        print(title)
        for key, value in options.items():
            # Justerar texten så att [key] hamnar på samma plats
            print(f"{value:<29}[{key}]")
        print("***********************")
        print("Please type your choice:")
        
        choice = input()
        
        # Se till att valet är giltigt innan vi fortsätter
        if choice not in options:
            print(f'"{choice}" is not a valid option. Please try again.\n')
            continue

        print("***********************")
        print(f'You chose "{options[choice]}". Is that correct? (yes/no)')
        
        user_input = input()

        if user_input.lower().startswith('y'):
            return choice # Bryter loopen och returnerar det bekräftade valet
        else:
            print("OK, let's try again.\n")

def inspect_device(device_path):
    """
    Kör 'sudo fdisk -l' på en specifik enhet för att få detaljerad
    information om partitionstabellen.
    """
    print(f"\n--- Detaljerad information för {device_path} ---")
    # VARNING: fdisk kräver ofta sudo för att läsa all information korrekt.
    command = ["sudo", "parted", device_path, "print", "free"]
    try:
        # Vi använder subprocess.run utan att fånga output,
        # så att fdisk kan skriva direkt till terminalen.
        # Detta hanterar även eventuella lösenordsprompter från sudo.
        subprocess.run(command, check=True)
        print("-------------------------------------------")
        return True
    except FileNotFoundError:
        print("Fel: Kommandot 'fdisk' eller 'sudo' hittades inte.", file=sys.stderr)
        return False
    except subprocess.CalledProcessError:
        print(f"Fel: Kommandot misslyckades. Kontrollera dina rättigheter.", file=sys.stderr)
        return False

main_menu_options = {
    "1": "Disk Analys",
    "2": "Partitioning",
    "3": "Disk Encryption",
    "4": "Logick Volumes",
    "5": "Wright File system"
}

main_choice = get_confirmed_choice("What do you like to do?", main_menu_options)

print("***********************")

if main_choice == "1":
 Disk_info()

elif main_choice == "2":
    print("Feature yet to be implemented")