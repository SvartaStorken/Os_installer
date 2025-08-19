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

def main():
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
            print("Feature yet to be implemented")
        else:
            print(f'"{choice}" is not a valid option.')

    else:
        # Om vi inte fick någon data, signalera ett fel.
        print("Kunde inte hämta disk-information. Avbryter.", file=sys.stderr)
        sys.exit(1) # Avsluta med en felkod != 0 för att signalera misslyckande

if __name__ == "__main__":
    main()