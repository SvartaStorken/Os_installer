correct_answer = False

print ("Welcome to os_installer")

print ("***********************")

print ("What do you like to do?")

print ("***********************")

while not correct_answer:

    print ("New install 1")

    print ("***********************")

    print ("Edit installation Template 2")

    print ("***********************")

    print ("Please type your choice")
    chose = input()

    print ("***********************")

    print ('You chose ' + chose + ' is that correct? yes/no')

    user_input = input()
    if user_input == "yes":
        correct_answer = True

print ("***********************")

print ("continuing process")