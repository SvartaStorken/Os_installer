import os
import sys
import subprocess

from utils.disk_ops import get_free_space_info, select_disk_device, inspect_device

TEMPLATE_DIR = "Templates/default_template"



def create_partition_fullscreen(device_path: str) -> None:
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


def run_partitioning() -> None:
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
