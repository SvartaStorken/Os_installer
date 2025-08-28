from utils.ui import display_disk_info, display_disk_devs
from utils.disk_ops import get_disk_info, select_disk_device, inspect_device

def run_disk_analysis() -> None:
    """Handles the menu for displaying disk information."""
    disk_data = get_disk_info()
    if not disk_data:
        return

    print("Disk information retrieved successfully.")
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
