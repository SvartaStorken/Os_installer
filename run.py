import subprocess
# 'sys' behövs inte om du inte använder det, så vi kan ta bort den importen.

def run_disk_tools():
    """Kör disk_tools.py och hanterar eventuella fel."""
    print("Starting disk utility...")
    try:
        subprocess.run(["python3", "disk_tools.py"], check=True)
        print("Disk utility finished successfully.")
    except FileNotFoundError:
        print("ERROR: Could not find the script 'disk_tools.py'.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: The disk utility script failed with return code {e.returncode}.")

def get_confirmed_choice(title, options):
    """
    Visar en meny, ber användaren göra ett val och bekräfta det.
    Returnerar det bekräftade valet.
    """
    while True: # En evighetsloop som vi bryter oss ur med 'return'
        print(title)
        for key, value in options.items():
            # Justerar texten så att [key] hamnar på samma plats
            print(f"{value:<29}[{key}]")
        print("***********************")
        print("Please type your choice:")
        
        choice = input()
        
        # Se till att valet är giltigt innan vi fortsätter
        if choice not in options:
            print(f'"{choice}" is not a valid option. Please try again.\n')
            continue

        print("***********************")
        print(f'You chose "{options[choice]}". Is that correct? (yes/no)')
        
        user_input = input()

        if user_input.lower().startswith('y'):
            return choice # Bryter loopen och returnerar det bekräftade valet
        else:
            print("OK, let's try again.\n")

# ----- HUVUDPROGRAMMET BÖRJAR HÄR -----

print("Welcome to os_installer")
print("***********************")

# Definiera alternativen för den första menyn
main_menu_options = {
    "1": "New install",
    "2": "Edit installation Template"
}
main_choice = get_confirmed_choice("What do you like to do?", main_menu_options)

print("***********************")

if main_choice == "1":
    # Definiera alternativen för den andra menyn
    machine_menu_options = {
        "1": "Install on local machine",
        "2": "Install on remote machine"
    }
    machine_choice = get_confirmed_choice("New install", machine_menu_options)
    
    if machine_choice == "1":
        print("Preparing to install on local machine...")
        run_disk_tools()
    elif machine_choice == "2":
        print("Feature yet to be implemented")
        
elif main_choice == "2":
    print("Edit installation Template")
    print("***********************")
    print("Feature yet to be implemented")

else: 
    print(f'You chose "{main_choice}". Feature yet to be implemented')