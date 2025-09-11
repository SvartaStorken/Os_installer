from utils import ui
from utils import disk_ops

def run_disk_analysis(stdscr) -> None:
    """Handles the menu for displaying disk information."""
    disk_data = disk_ops.get_disk_info()
    if not disk_data:
        stdscr.addstr(2, 2, "Could not retrieve disk info. Press any key to return.")
        stdscr.getch()
        return

    menu_options = {
        "1": "Full output of lsblk",
        "2": "Show devices only",
        "3": "Back to main menu"
    }

    while True:
        stdscr.clear()
        choice = ui.get_menu_choice(stdscr, "Disk Analysis", menu_options)

        if choice == "Full output of lsblk":
            lines = []
            for device in disk_data.get('blockdevices', []):
                if device.get('type') == 'disk':
                    lines.append(f"[Disk] /dev/{device.get('name', 'N/A')} (Size: {device.get('size', 'N/A')})")
                    for part in device.get('children', []):
                        lines.append(f"  └─ [Part] /dev/{part.get('name', 'N/A')} ({part.get('size', 'N/A')}) | FS: {part.get('fstype', 'n/a')} | Mount: {part.get('mountpoint', 'n/a')}")
            ui.display_text_viewer(stdscr, "Full Disk and Partition Info", lines)
        elif choice == "Show devices only":
            lines = [f"/dev/{dev.get('name', 'N/A')} ({dev.get('size', 'N/A')})" for dev in disk_data.get('blockdevices', []) if dev.get('type') == 'disk']
            ui.display_text_viewer(stdscr, "Disk Devices", lines)
        elif choice == "Back to main menu" or choice is None:
            break

        # After viewing, ask to inspect a device
        stdscr.clear()
        if ui.get_confirmation(stdscr, "Do you want to select a device for detailed inspection?"):
            selected_device = disk_ops.select_disk_device_curses(stdscr, "Select a device to inspect:")
            if selected_device:
                # inspect_device now exits curses, so we need to handle that
                success, output_lines = disk_ops.inspect_device(selected_device)
                # After returning, re-initialize curses screen for the next loop
                stdscr.refresh()
