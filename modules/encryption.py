import os
import sys
import subprocess

from utils.disk_ops import select_partition_device

TEMPLATE_DIR = "Templates/default_template"

def run_encryption_menu() -> None:
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
