import subprocess
import json
import sys

def get_disk_info() -> dict | None:
    """
    Runs the 'lsblk' command to retrieve information about all block devices.
    Uses the --json flag to get structured and reliable output.
    Returns the information as a Python object (dictionary).
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

def select_disk_device(prompt: str="Please select a device:") -> str | None:
    """
    Displays a menu with disks and lets the user select one.
    Returns the selected device path (e.g. /dev/sda).
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

def select_partition_device(prompt: str="Please select a partition:") -> str | None:
    """
    Displays a menu with partitions and lets the user select one.
    Returns the selected partition path (e.g. /dev/sda1).
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

def inspect_device(device_path: str) -> bool:
    """
    Runs 'sudo parted ... print free' to show detailed partition information.
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

def get_free_space_info(device_path: str) -> str | None:
    """
    Uses parted in machine-readable mode to find the start sector of free space.
    Returns the start sector as a string (e.g. '12345s') or None on error.
    """
    command = ["sudo", "parted", "--script", device_path, "--machine", "unit", "s", "print", "free"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        # The last line describing a "partition" is the free space
        free_space_line = lines[-1]

        if free_space_line:
            parts = free_space_line.split(':')
            # parts[1] is the start sector, already with unit 's'
            return parts[1]
        return None
    except (subprocess.CalledProcessError, IndexError) as e:
        print(f"Error parsing free space for {device_path}: {e}", file=sys.stderr)
        return None
