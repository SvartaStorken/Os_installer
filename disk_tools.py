#!/usr/bin/env python3

import subprocess
import json
import sys
import os

# Definiera sökvägen till vår mallkatalog för enkel åtkomst
TEMPLATE_DIR = "Templates/default_template"

def get_disk_info():
    """
    Kör kommandot 'lsblk' för att hämta information om alla block-enheter.
    Använder --json-flaggan för att få strukturerad och pålitlig output.
    Returnerar informationen som ett Python-objekt (dictionary).
    """
    try:
        command = ["lsblk", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT", "--json"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error getting disk info: {e}", file=sys.stderr)
        return None

def display_disk_info(data):
    """
    Tar emot disk-information och skriver ut den i ett hierarkiskt format.
    """
    print("--- Tillgängliga diskar och partitioner ---")
    if not data or 'blockdevices' not in data:
        print("Ingen information om diskenheter hittades.")
        return

    for device in data['blockdevices']:
        if device.get('type') == 'disk':
            print(f"\n[Disk] /dev/{device.get('name', 'N/A')} (Storlek: {device.get('size', 'N/A')})")
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
    """Visar enbart en lista över diskenheter."""
    print("****-List of Disk Devices-****")
    if not data or 'blockdevices' not in data:
        print("****-No disk devices found-****")
        return
    
    for device in data['blockdevices']:
        if device.get('type') == 'disk':
            print(f"/dev/{device.get('name', 'N/A')} (Size: {device.get('size', 'N/A')})")
    print("\n-------------------------------------------")

def select_disk_device(prompt="Please select a device:"):
    """
    Visar en meny med diskar och låter användaren välja en.
    Returnerar den valda enhetens sökväg (t.ex. /dev/sda).
    """
    disk_data = get_disk_info()
    if not disk_data:
        return None

    available_disks = [dev for dev in disk_data['blockdevices'] if dev.get('type') == 'disk']
    if not available_disks:
        print("No disks found.")
        return None

    disk_menu_options = {
        str(i + 1): f"/dev/{disk['name']} ({disk['size']})" for i, disk in enumerate(available_disks)
    }
    cancel_option = str(len(disk_menu_options) + 1)
    disk_menu_options[cancel_option] = "Cancel"

    while True:
        print(f"\n{prompt}")
        for key, value in disk_menu_options.items():
            print(f"[{key}] {value}")
        
        choice = input("Your choice: ")
        if choice == cancel_option:
            return None
        elif choice in disk_menu_options:
            return disk_menu_options[choice].split()[0]
        else:
            print(f'"{choice}" is not a valid option. Please try again.')

def select_partition_device(prompt="Please select a partition:"):
    """
    Visar en meny med partitioner och låter användaren välja en.
    Returnerar den valda partitionens sökväg (t.ex. /dev/sda1).
    """
    disk_data = get_disk_info()
    if not disk_data:
        return None

    available_partitions = []
    for device in disk_data['blockdevices']:
        if device.get('type') == 'disk' and 'children' in device:
            for partition in device['children']:
                available_partitions.append(partition)

    if not available_partitions:
        print("No partitions found.")
        return None

    partition_menu_options = {
        str(i + 1): f"/dev/{part['name']} ({part['size']})" for i, part in enumerate(available_partitions)
    }
    cancel_option = str(len(partition_menu_options) + 1)
    partition_menu_options[cancel_option] = "Cancel"

    while True:
        print(f"\n{prompt}")
        for key, value in partition_menu_options.items():
            print(f"[{key}] {value}")
        
        choice = input("Your choice: ")
        if choice == cancel_option:
            return None
        elif choice in partition_menu_options:
            return partition_menu_options[choice].split()[0]
        else:
            print(f'"{choice}" is not a valid option. Please try again.')

def inspect_device(device_path):
    """
    Kör 'sudo parted ... print free' för att visa detaljerad partitionsinformation.
    """
    print(f"\n--- Detailed information for {device_path} ---")
    command = ["sudo", "parted", device_path, "print", "free"]
    try:
        subprocess.run(command, check=True)
        print("-------------------------------------------------")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error inspecting device: {e}", file=sys.stderr)
        return False

def get_free_space_info(device_path):
    """
    Använder parted i maskinläsbart läge för att hitta startsektorn för ledigt utrymme.
    Returnerar startsektorn som en sträng (t.ex. '12345s') eller None vid fel.
    """
    command = ["sudo", "parted", "--script", device_path, "--machine", "unit", "s", "print", "free"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        # Den sista raden som beskriver en "partition" är det fria utrymmet
        free_space_line = lines[-1]
        
        if free_space_line:
            parts = free_space_line.split(':')
            # parts[1] är startsektorn, redan med enhet 's'
            return parts[1]
        return None
    except (subprocess.CalledProcessError, IndexError) as e:
        print(f"Error parsing free space for {device_path}: {e}", file=sys.stderr)
        return None

def create_partition_fullscreen(device_path):
    """
    Skapar en ny partition som använder 100% av det tillgängliga fria utrymmet.
    """
    print("\n--- Create Partition (100% of free space) ---")
    start_sector = get_free_space_info(device_path)
    if not start_sector:
        print("Could not find free space to create a partition.")
        return

    print(f"Detected free space starting at sector {start_sector.replace('s', '')}.")
    fs_type = input("Enter partition type ID (e.g., ext4, linux-lvm, linux-swap) [default: ext4]: ")
    if not fs_type:
        fs_type = "ext4"

    command_str = f"sudo parted --script {device_path} mkpart primary {fs_type} {start_sector} 100%"
    
    print("\nThe following command will be generated:")
    print(f"  {command_str}")
    
    # Skapa sökvägen till skriptfilen
    script_path = os.path.join(TEMPLATE_DIR, "3_create_partition.sh")
    
    print(f"\nThis command will be saved to '{script_path}' and then executed.")
    confirm = input("Do you want to proceed? (yes/no): ")

    if confirm.lower().startswith('y'):
        try:
            # 1. Skapa katalogen om den inte finns
            os.makedirs(TEMPLATE_DIR, exist_ok=True)
            print(f"Directory '{TEMPLATE_DIR}' ensured.")

            # 2. Skriv till templat-filen
            with open(script_path, "a") as f:
                f.write(f"#!/bin/bash\n\n")
                f.write(f"# Command to create a new partition on {device_path}\n")
                f.write(f"{command_str}\n\n")
            print(f"Command appended to '{script_path}'.")

            # 3. Gör skriptet körbart
            os.chmod(script_path, 0o755) # 0o755 motsvarar rwxr-xr-x
            print(f"Made script '{script_path}' executable.")

            # 4. Kör kommandot för att verifiera
            print("Executing command to verify...")
            subprocess.run(command_str.split(), check=True)
            print("\nPartition created successfully!")

        except IOError as e:
            print(f"Error writing to template file: {e}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error creating partition: {getattr(e, 'stderr', 'Unknown error')}", file=sys.stderr)
    else:
        print("Partition creation cancelled.")

def Disk_info():
    """Hanterar menyn för att visa diskinformation."""
    disk_data = get_disk_info()
    if not disk_data:
        return

    print("Disk-information hämtad framgångsrikt.")
    print("***********************")
    
    menu_options = {"1": "Full output of lsblk?", "2": "Show devices only"}
    print("Please choose an option:")
    for key, value in menu_options.items():
        print(f"[{key}] {value}")
    choice = input("Your choice: ")

    if choice == "1":
        display_disk_info(disk_data)
    elif choice == "2":
        display_disk_devs(disk_data)
    else:
        print(f'"{choice}" is not a valid option.')
        return

    print("\nDo you want to select a device for inspection? (yes/no)")
    if input().lower().startswith('y'):
        selected_device = select_disk_device("Select a device to inspect:")
        if selected_device:
            inspect_device(selected_device)

def partition_disk():
    """Hanterar arbetsflödet för att partitionera en disk."""
    device_path = select_disk_device("Select a disk to partition:")
    if not device_path:
        print("Partitioning cancelled.")
        return

    while True:
        print(f"\n--- Actions for {device_path} ---")
        inspect_device(device_path)

        action_menu = {
            "1": "Create a new partition",
            "2": "Delete an existing partition",
            "3": "Create new GPT partition table (ERASES ALL DATA)",
            "4": "Return to main menu"
        }
        print("\nWhat would you like to do on this disk?")
        for key, value in action_menu.items():
            print(f"[{key}] {value}")
        action_choice = input("Your choice: ")

        if action_choice == "1":
            print("\n--- Create Partition Menu ---")
            partition_menu = {
                "1": "Use 100% of free space",
                "2": "Use MiB",
                "3": "Use GiB",
                "4": "Use % of free space",
                "5": "Cancel"
            }
            for key, value in partition_menu.items():
                print(f"[{key}] {value}")
            
            create_choice = input("Your choice: ")
            
            if create_choice == "1":
                create_partition_fullscreen(device_path)
            elif create_choice in ["2", "3", "4"]:
                print("Feature yet to be implemented.")
            elif create_choice == "5":
                print("Cancelled partition creation.")
            else:
                print(f'"{create_choice}" is not a valid option.')
                
        elif action_choice == "2":
            print("Feature yet to be implemented")
        elif action_choice == "3":
            print("\n" + "="*60 + "\n!!! EXTREME WARNING !!!")
            print(f"This will IRREVERSIBLY ERASE ALL DATA on {device_path}.")
            print("="*60)
            confirm = input(f"To confirm, please type the device name ('{device_path}'): ")
            if confirm == device_path:
                command = ["sudo", "parted", "--script", device_path, "mklabel", "gpt"]
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    print("GPT partition table created successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error creating partition table: {e.stderr}", file=sys.stderr)
            else:
                print("Confirmation failed. Action cancelled.")
        elif action_choice == "4":
            break
        else:
            print(f'"{action_choice}" is not a valid option.')

def disk_encryption_menu():
    """Hanterar menyn och arbetsflödet för LUKS-diskkryptering."""
    encryption_menu = {
        "1": "Format a partition with LUKS (ERASES DATA)",
        "2": "Open a LUKS-encrypted partition",
        "3": "Add a new key to a LUKS partition",
        "4": "Return to main menu"
    }

    while True:
        print("\n--- Disk Encryption Menu ---")
        for key, value in encryption_menu.items():
            print(f"[{key}] {value}")
        
        choice = input("Your choice: ")

        if choice == "1":
            # Format with LUKS
            device = select_partition_device("Select a partition to format with LUKS:")
            if not device:
                print("Operation cancelled.")
                continue

            print("\n" + "="*60 + "\n!!! EXTREME WARNING !!!")
            print(f"This will IRREVERSIBLY ERASE ALL DATA on {device}.")
            print("You will be asked to create a new passphrase.")
            print("="*60)
            confirm = input(f"To confirm, please type the device name ('{device}'): ")

            if confirm == device:
                command = ["sudo", "cryptsetup", "luksFormat", device]
                command_str = ' '.join(command)
                script_path = os.path.join(TEMPLATE_DIR, "4_encrypt_device.sh")

                try:
                    # 1. Skapa katalogen om den inte finns
                    os.makedirs(TEMPLATE_DIR, exist_ok=True)

                    # 2. Skriv till templat-filen (använder 'w' för att skriva över)
                    with open(script_path, "w") as f:
                        f.write("#!/bin/bash\n\n")
                        f.write("# Detta skript kräver interaktion för att mata in lösenfras.\n")
                        f.write(f"# Kommando för att formatera {device} med LUKS-kryptering.\n")
                        f.write(f"{command_str}\n")
                    print(f"Kommando sparat till '{script_path}'.")

                    # 3. Gör skriptet körbart
                    os.chmod(script_path, 0o755)
                    print(f"Gjorde skriptet '{script_path}' körbart.")

                    # 4. Kör kommandot
                    print(f"\nKör kommando: {command_str}")
                    print("Please follow the prompts to set your passphrase.")
                    subprocess.run(command, check=True)
                    print(f"\nSuccessfully formatted {device} with LUKS.")

                    # Fråga om att öppna den nya volymen
                    open_now = input("\nDo you want to open (unlock) the new encrypted volume now? (yes/no): ")
                    if open_now.lower().startswith('y'):
                        mapper_name = input("Enter a name for the mapped device (e.g., 'crypted_root'): ")
                        if not mapper_name.strip():
                            print("Mapper name cannot be empty. Skipping open operation.")
                        else:
                            open_command = ["sudo", "cryptsetup", "open", device, mapper_name]
                            open_command_str = ' '.join(open_command)

                            print(f"\nRunning command: {open_command_str}")
                            print("Please enter your passphrase to unlock.")
                            subprocess.run(open_command, check=True)
                            print(f"\nSuccessfully opened {device} as /dev/mapper/{mapper_name}")

                            # Lägg till open-kommandot i skriptet
                            with open(script_path, "a") as f:
                                f.write("\n# Kommando för att öppna den krypterade partitionen.\n")
                                f.write(f"{open_command_str}\n")
                            print(f"Open command appended to '{script_path}'.")
                except (IOError, subprocess.CalledProcessError) as e:
                    print(f"An error occurred during encryption or opening the device: {e}", file=sys.stderr)
            else:
                print("Confirmation failed. Action cancelled.")

        elif choice == "2":
            # Open LUKS device
            device = select_partition_device("Select a LUKS-encrypted partition to open:")
            if not device:
                print("Operation cancelled.")
                continue
            
            mapper_name = input("Enter a name for the mapped device (e.g., 'crypted_data'): ")
            if not mapper_name.strip():
                print("Mapper name cannot be empty. Operation cancelled.")
                continue

            command = ["sudo", "cryptsetup", "open", device, mapper_name]
            try:
                print(f"\nRunning command: {' '.join(command)}")
                print("Please enter your passphrase when prompted.")
                subprocess.run(command, check=True)
                print(f"\nSuccessfully opened {device} as /dev/mapper/{mapper_name}")
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"Error opening device: {e}", file=sys.stderr)

        elif choice == "3":
            print("Feature yet to be implemented")

        elif choice == "4":
            break
        else:
            print(f'"{choice}" is not a valid option.')

def select_multiple_partitions(prompt="Select partitions to use."):
    """
    Låter användaren välja en eller flera partitioner från en lista.
    Returnerar en lista med valda partitionssökvägar.
    """
    selected_partitions = []
    print(f"\n{prompt}")
    
    while True:
        # Använd den befintliga funktionen för att visa menyn och få ett val
        # Vi anpassar prompten för att visa vad som redan är valt
        current_selection_str = f" (Selected: {', '.join(selected_partitions)})" if selected_partitions else ""
        device = select_partition_device(f"Select a partition to add{current_selection_str}.\nChoose 'Cancel' when you are done.")
        
        if not device:  # Användaren valde 'Cancel', vilket betyder att de är klara
            break
            
        if device in selected_partitions:
            print(f"{device} is already selected. Please choose another.")
        else:
            selected_partitions.append(device)
            print(f"Added {device}.")
            
    return selected_partitions

def create_lvm_setup():
    """Guidar användaren genom att skapa PV, VG och LVs och sparar kommandona."""
    all_commands = []
    script_path = os.path.join(TEMPLATE_DIR, "5_logical_volumes.sh")

    # --- Steg 1: pvcreate ---
    print("\n--- Step 1: Create Physical Volumes (PVs) ---")
    physical_volumes = select_multiple_partitions("Select partitions to initialize for LVM.")
    if not physical_volumes:
        print("No partitions selected. LVM setup cancelled.")
        return

    pv_command_str = f"sudo pvcreate {' '.join(physical_volumes)}"
    print(f"\nThe following command will be executed:\n  {pv_command_str}")
    if not input("Proceed? (yes/no): ").lower().startswith('y'):
        print("Operation cancelled.")
        return

    try:
        subprocess.run(pv_command_str.split(), check=True, capture_output=True, text=True)
        print("Physical Volumes created successfully.")
        all_commands.append(f"# Step 1: Create Physical Volumes\n{pv_command_str}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error creating Physical Volumes: {e.stderr}", file=sys.stderr)
        return

    # --- Steg 2: vgcreate ---
    print("\n--- Step 2: Create a Volume Group (VG) ---")
    vg_name = input("Enter a name for the new Volume Group (e.g., 'vg_main'): ")
    if not vg_name.strip():
        print("Volume Group name cannot be empty. Operation cancelled.")
        return

    vg_command_str = f"sudo vgcreate {vg_name} {' '.join(physical_volumes)}"
    print(f"\nThe following command will be executed:\n  {vg_command_str}")
    if not input("Proceed? (yes/no): ").lower().startswith('y'):
        print("Operation cancelled.")
        return

    try:
        subprocess.run(vg_command_str.split(), check=True, capture_output=True, text=True)
        print(f"Volume Group '{vg_name}' created successfully.")
        all_commands.append(f"# Step 2: Create Volume Group\n{vg_command_str}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error creating Volume Group: {e.stderr}", file=sys.stderr)
        return

    # --- Steg 3: lvcreate (loop) ---
    print("\n--- Step 3: Create Logical Volumes (LVs) ---")
    while True:
        if not input("Create a new Logical Volume? (yes/no): ").lower().startswith('y'):
            break

        lv_name = input("  Name for the new LV (e.g., 'lv_root'): ")
        lv_size = input("  Size for the LV (e.g., '20G', '100%FREE'): ")
        if not lv_name.strip() or not lv_size.strip():
            print("LV name and size cannot be empty. Skipping.")
            continue

        size_flag = "-L" if '%' not in lv_size else "-l"
        lv_command_str = f"sudo lvcreate {size_flag} {lv_size} -n {lv_name} {vg_name}"
        
        print(f"  Command: {lv_command_str}")
        if not input("  Proceed with this LV? (yes/no): ").lower().startswith('y'):
            print("  LV creation skipped.")
            continue

        try:
            subprocess.run(lv_command_str.split(), check=True, capture_output=True, text=True)
            print(f"  Logical Volume '{lv_name}' created successfully.")
            all_commands.append(f"# Step 3: Create Logical Volume '{lv_name}'\n{lv_command_str}\n")
        except subprocess.CalledProcessError as e:
            print(f"  Error creating Logical Volume: {e.stderr}", file=sys.stderr)

    # --- Spara till skript ---
    if all_commands:
        print(f"\nSaving LVM commands to '{script_path}'...")
        try:
            os.makedirs(TEMPLATE_DIR, exist_ok=True)
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n\n")
                f.write("# This script sets up LVM based on the steps performed.\n\n")
                f.writelines(all_commands)
            os.chmod(script_path, 0o755)
            print(f"Successfully saved and made '{script_path}' executable.")
        except IOError as e:
            print(f"Error writing to script file: {e}", file=sys.stderr)

def lvm_menu():
    """Hanterar menyn för LVM-operationer."""
    lvm_options = {
        "1": "Create volumes and group",
        "2": "Return to main menu"
    }
    while True:
        print("\n--- Logical Volume (LVM) Menu ---")
        for key, value in lvm_options.items():
            print(f"[{key}] {value}")
        choice = input("Your choice: ")

        if choice == "1":
            create_lvm_setup()
        elif choice == "2":
            break
        else:
            print(f'"{choice}" is not a valid option.')

def get_confirmed_choice(title, options):
    """Visar en meny och returnerar ett bekräftat val."""
    while True:
        print(title)
        for key, value in options.items():
            print(f"{value:<29}[{key}]")
        print("***********************")
        print("Please type your choice:")
        choice = input()
        
        if choice not in options:
            print(f'"{choice}" is not a valid option. Please try again.\n')
            continue

        print("***********************")
        print(f'You chose "{options[choice]}". Is that correct? (yes/no)')
        if input().lower().startswith('y'):
            return choice
        else:
            print("OK, let's try again.\n")

def main():
    """Huvudfunktion som visar menyn i en loop."""
    main_menu_options = {
        "1": "Disk Analysis",
        "2": "Partitioning",
        "3": "Disk Encryption",
        "4": "Logical Volumes (LVM)",
        "5": "Write Filesystem",
        "6": "Exit"
    }

    while True:
        main_choice = get_confirmed_choice("What do you like to do?", main_menu_options)
        print("***********************")

        if main_choice == "1":
            Disk_info()
        elif main_choice == "2":
            partition_disk()
        elif main_choice == "3":
            disk_encryption_menu()
        elif main_choice == "4":
            lvm_menu()
        elif main_choice == "5":
            print("Feature yet to be implemented")
        elif main_choice == "6":
            print("Exiting disk tools. Goodbye!")
            break

        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()