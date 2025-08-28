from utils import ui
from modules import disk_analysis, partitioning, encryption, lvm

# Definiera sökvägen till vår mallkatalog för enkel åtkomst
TEMPLATE_DIR = "Templates/default_template"

def main():
    """Main function to run the application."""
    main_menu_options = {
        "1": "Disk Analysis",
        "2": "Partitioning",
        "3": "Disk Encryption",
        "4": "Logical Volumes (LVM)",
        "5": "Write Filesystem",
        "6": "Exit"
    }

    while True:
        choice = ui.get_confirmed_choice("What do you like to do?", main_menu_options)

        if choice == "1":
            disk_analysis.run_disk_analysis()
        elif choice == "2":
            partitioning.run_partitioning()
        elif choice == "3":
            encryption.run_encryption_menu()
        elif choice == "4":
            lvm.run_lvm_menu()
        elif choice == "5":
            print("Feature yet to be implemented")
        elif choice == "6":
            print("Exiting. Goodbye!")
            break

        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()
