correct_answer = False

print("Welcome to os_installer")
print("***********************")
print("What do you like to do?")
print("***********************")

# while not loop to ensure correct answer
while not correct_answer:
    print("New install                  [1]")
    print("Edit installation Template   [2]")
    print("***********************")
    print("Please type your choice:")
    
    chose = input()

    print("***********************")
    print(f'You chose "{chose}". Is that correct? (yes/no)')
    
    user_input = input()

    # anny answer starts with y is correct
    if user_input.lower().startswith('y'):
        correct_answer = True
    else:
        print(f'Your choice "{chose}" was not confirmed. Let\'s try again.')
        print("***********************\n")

print("***********************")

if chose == "1":
    correct_answer = False
    while not correct_answer:

        print("New install")
        print("Install on local machine?    [1]")
        print("Install on remote machine?   [2]")
        print("***********************")
        print("Please type your choice:")
    
        chose_machine = input()

        print("***********************")
        print(f'You chose "{chose_machine}". Is that correct? (yes/no)')
    
        user_input = input()

        # anny answer starts with y is correct
        if user_input.lower().startswith('y'):
            correct_answer = True
        else:
            print(f'Your choice "{chose_machine}" was not confirmed. Let\'s try again.')
            print("***********************\n")
    if chose_machine == "1":
        print("Install on local machine")
        print("Feature yet to be implemented")
    elif chose_machine == "2":
        print("Install on remote machine")
        print("Feature yet to be implemented")
    else: 
        print(f'You chose "{chose_machine}". Feature yet to be implemented')

elif chose == "2":
    print("Edit installation Template")
    print("***********************")
    print("Feature yet to be implemented")

else: 
    print(f'You chose "{chose}". Feature yet to be implemented')
#########