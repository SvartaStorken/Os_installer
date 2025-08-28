def get_confirmed_choice(title: str, options: dict) -> str | None:
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

def display_disk_info(data: dict) -> None:
    """
    Tar emot disk-information och skriver ut den i ett hierarkiskt format.
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
    """Visar enbart en lista över diskenheter."""
    print("****-List of Disk Devices-****")
    if not data or 'blockdevices' not in data:
        print("****-No disk devices found-****")
        return

    for device in data['blockdevices']:
        if device.get('type') == 'disk':
            print(f"/dev/{device.get('name', 'N/A')} (Size: {device.get('size', 'N/A')})")
    print("\n-------------------------------------------")
