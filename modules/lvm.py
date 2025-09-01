import os
import sys
import subprocess

from utils.disk_ops import select_partition_device

TEMPLATE_DIR = "Templates/default_template"

def select_multiple_partitions(prompt: str="Select partitions to use.") -> list:
    """
    Allows the user to select one or more partitions from a list.
    Returns a list of selected partition paths.
    """
    selected_partitions = []
    print(f"\n{prompt}")

    while True:
        # Use the existing function to display the menu and get a selection
        # We adapt the prompt to show what is already selected
        current_selection_str = f" (Selected: {', '.join(selected_partitions)})" if selected_partitions else ""
        device = select_partition_device(f"Select a partition to add{current_selection_str}.\nChoose 'Cancel' when you are done.")

        if not device:  # The user chose 'Cancel', which means they are done
            break

        if device in selected_partitions:
            print(f"{device} is already selected. Please choose another.")
        else:
            selected_partitions.append(device)
            print(f"Added {device}.")

    return selected_partitions

def create_lvm_setup() -> None:
    """Guides the user through creating PV, VG, and LVs and saves the commands."""
    all_commands = []
    script_path = os.path.join(TEMPLATE_DIR, "5_logical_volumes.sh")

    # --- Step 1: pvcreate ---
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

    # --- Step 2: vgcreate ---
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

    # --- Step 3: lvcreate (loop) ---
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

    # --- Save to script ---
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

def run_lvm_menu() -> None:
    """Handles the menu for LVM operations."""
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
