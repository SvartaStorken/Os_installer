import curses
def get_confirmed_choice(title: str, options: dict) -> str | None:
    """
    Shows a menu, asks the user to make a choice and confirm it.
    Returns the confirmed choice.
    """
    while True: # An infinite loop that we break out of with 'return'
        print(title)
        for key, value in options.items():
            # Adjusts the text so that [key] is aligned
            print(f"{value:<29}[{key}]")
        print("***********************")
        print("Please type your choice:")

        choice = input()

        # Make sure the choice is valid before continuing
        if choice not in options:
            print(f'"{choice}" is not a valid option. Please try again.\n')
            continue

        print("***********************")
        print(f'You chose "{options[choice]}". Is that correct? (yes/no)')

        user_input = input()

        if user_input.lower().startswith('y'):
            return choice # Breaks the loop and returns the confirmed choice
        else:
            print("OK, let's try again.\n")

def display_disk_info(data: dict) -> None:
    """
    Receives disk information and prints it in a hierarchical format.
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

def display_disk_devs(data: dict) -> None:
    """Show a list of disk devices"""
    print("****-List of Disk Devices-****")
    if not data or 'blockdevices' not in data:
        print("****-No disk devices found-****")
        return

    for device in data['blockdevices']:
        if device.get('type') == 'disk':
            print(f"/dev/{device.get('name', 'N/A')} (Size: {device.get('size', 'N/A')})")
    print("\n-------------------------------------------")

def get_menu_choice(stdscr: 'curses._CursesWindow', title: str, options: dict) -> str | None:
    """
    Displays a curses-based menu and returns the selected option's value.
    Allows navigation with arrow keys and selection with Enter.
    """
    # --- Curses setup ---
    curses.curs_set(0)  # Hide the cursor
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlighted item
    
    # --- Menu state ---
    current_row_idx = 0
    # We will display the values from the dictionary
    option_values = list(options.values())

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # --- Render title ---
        stdscr.addstr(1, 2, title)
        stdscr.addstr(2, 2, "=" * (len(title)))

        # --- Render menu options ---
        for idx, row in enumerate(option_values):
            x = 2
            y = 4 + idx
            if idx == current_row_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, f"> {row}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, f"  {row}")

        stdscr.refresh()

        # --- Handle input ---
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row_idx > 0:
            current_row_idx -= 1
        elif key == curses.KEY_DOWN and current_row_idx < len(option_values) - 1:
            current_row_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return option_values[current_row_idx]
