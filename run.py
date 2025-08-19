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
        print(f'Your chose "{chose}" was wrong. Try again.')
        print("***********************\n")

print("***********************")
print("Continuing process...")
