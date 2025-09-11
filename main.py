import curses
import os
from utils import ui
from modules import disk_analysis, partitioning, encryption, lvm

# Define the path to our template directory for easy access
TEMPLATE_DIR = "Templates/default_template"


def main_loop(stdscr: 'curses._CursesWindow'):
    """Main application loop running within a curses screen."""
    # This dictionary should be defined inside the loop's scope.
    main_menu_options = {
        "1": "Disk Analysis",
        "2": "Partitioning",
        "3": "Disk Encryption",
        "4": "Logical Volumes (LVM)",
        "5": "Write Filesystem",
        "6": "Exit"
    }

    while True:
        # Assuming get_menu_choice returns the *value* (e.g., "Disk Analysis")
        # and that it's the intended curses-based menu function.
        choice = ui.get_menu_choice(stdscr, "What do you like to do?", main_menu_options)

        if choice == "Disk Analysis":
            disk_analysis.run_disk_analysis(stdscr)
        elif choice == "Partitioning":
            ui.display_text_viewer(stdscr, "Info", ["This module is not yet converted to curses."])
        elif choice == "Disk Encryption":
            ui.display_text_viewer(stdscr, "Info", ["This module is not yet converted to curses."])
        elif choice == "Logical Volumes (LVM)":
            ui.display_text_viewer(stdscr, "Info", ["This module is not yet converted to curses."])
        elif choice == "Write Filesystem":
            stdscr.clear()
            stdscr.addstr(0, 0, "Feature yet to be implemented. Press any key to continue.")
            stdscr.getch()
        elif choice == "Exit" or choice is None:
            stdscr.clear()
            stdscr.addstr(0, 0, "Exiting. Goodbye!")
            stdscr.refresh()
            curses.napms(1000)
            break
        
        # Efter att en modul har körts, rita om skärmen för nästa meny-loop
        stdscr.clear()
        stdscr.refresh()

if __name__ == "__main__":
    # The curses.wrapper function initializes curses, and restores the
    # terminal to its original state after the program has finished.
    curses.wrapper(main_loop)
