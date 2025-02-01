import json
import google.generativeai as genai
from datetime import date
import os 


def department():
    print("\n\n    Departments \n\n1- Artificial Intelligence & Data Science\n2- Civil Engineering\n3- Computer Science & Engineering")
    print("4- Computer Science & Engineering (Cyber Security)\n5- Computer Science & Engineering (Artificial Intelligence)\n6- Electronics & Communication Engineering")
    print("7- Electronics & Computer Engineering\n8- Electrical & Electronics Engineering\n9- Mechanical Engineering\n10- Computer Applications")
    print("11- Masters in Business Administration\n12- Science & Humanities Department\n\n")

    departments = {
        1: "Department of Artificial Intelligence & Data Science",
        2: "Department of Civil Engineering",
        3: "Department of Computer Science & Engineering",
        4: "Department of Computer Science & Engineering (Cyber Security)",
        5: "Department of Computer Science & Engineering (Artificial Intelligence)",
        6: "Department of Electronics & Communication Engineering",
        7: "Department of Electronics & Computer Engineering",
        8: "Department of Electrical & Electronics Engineering",
        9: "Department of Mechanical Engineering",
        10: "Department of Computer Applications",
        11: "Department of Masters in Business Administration",
        12: "Department of Science & Humanities",
    }

    while True:
        try:
            department_id = int(input("Enter Department Number: "))
            if department_id in departments:
                return departments[department_id]
            else:
                print("Invalid department ID. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def newuser():
    while True:
        filename = input("Enter a unique username to identifiy you: ")
        if os.path.exists(filename + ".json"):
            print("Error: Username already exists! Try a different username.")
        else:
            break
#created by Nekhal James
    f_name = input("Enter the First name: ")
    l_name = input("Enter the Last name: ")
    full_name = f_name + " " + l_name

    temp_dict = {
        "name": full_name,
        "department": department(),
        "roll_no": input("Enter Roll No.: "),
        "faculty": input("Enter the name of Faculty advisor: "),
        "leave_taken": int(input("Enter no. of leaves taken till date: ")),
    }
    print("\n\nVoila! A fresh face has joined the ranks. Welcome, new user!\n")

    filename += ".json"
    with open(filename, "w") as file:
        json.dump(temp_dict, file, indent=4)

    return filename


def gemini(qn):
    print("\nGenerating.....")
    response = model.generate_content(qn)
    print("\n" + response.text)


def geminir(qn):
    print("\nGenerating.....")
    response = model.generate_content(qn)
    return response.text.strip() if response.text else "Error generating response."





# Load API Key
try:
    with open("api.json", "r") as file:
        apikey = json.load(file)
except FileNotFoundError:
    print("Error: API key file (api.json) not found!")
    exit()

# Configure Gemini Model
genai.configure(api_key=apikey["api"])
model = genai.GenerativeModel("gemini-1.5-flash")

# Get User Data, date setting
today = date.today()
date_today = today.strftime("%d-%m-%Y")

#created by Nekhal James


new_user_req = input(
    "\n\nWelcome \n- Please enter your username to continue,\n- Or press 1 to embark on a new user adventure.\n\n:- "
)

if new_user_req == "1":
    filename = newuser()
else:
    filename = new_user_req + ".json"
    print("\nWelcome back!")

# Load User Data
try:
    with open(filename, "r") as file:
        user = json.load(file)
except FileNotFoundError:
    print("Error: User data file not found!")
    exit()


print("\n\n\nHi, how are you?\n")
hi = input(":- ")
cre_res = input("\nShould I create a reason for you? (y/n)\n\n:- ").strip().lower()


if cre_res in ["y", "yes"]:
    reason = geminir("create a simple reasons for taking a leave which is like feaver or educational events or family functions as a student")
    print("\nReasons =", reason, "\n")
    taken = "to take"
    print("\n\n-Type the reason that speaks to you most from above....\n")
    reason=input(":-")

else:
    print("\nlet me know the reason")
    reason = input("\n:- ")
    print("\nHas the leave already been taken? (y/n): ")
    taken = input(":- ").strip().lower()
    if taken in ["y", "yes"]:
        taken = "taken"
    else:
        taken = "to take"

print("\nWhen does your leave start ?")
start_date = input(":- ")

print("\n\nWhen does your leave end ?")
end_date = input(":- ")

print("\nDo you want a [1]-Leave Letter or [2]-Leave Form? \n:- ")
form = int(input())


if form == 1:
    letter = (
       f"Generate me a letter for the leave which I have  {taken } to the college faculty advisor Mr./Ms. { user["faculty"] }. Reason: {reason}, expand the reason. The leave starts on {start_date} and ends on"+
        f"{end_date}. College: SJCET Palai, Department: {user["department"]}. My name is  {user["name"]} and my roll number is {user["roll_no"]}. Set the letter date as {date_today}. no need to add locations to fill details, add full name in salutation"
    )
    print("\n")
    gemini(letter)
    print("\n\n")
else:
    print("\n\n")
    reason_exp = geminir("Expand the reason '" + reason + "' into a single sentence for a leave application.")
    form_text = (
        f"Name = {user['name']}\n"
        f"Date = {date_today}\n"
        f"Class & Branch = {user['department']}\n"
        f"Dates for which leave is applied = {start_date} to {end_date}\n"
        f"Reason for leave = {reason_exp}\n"
        f"No. of leaves applied = {user['leave_taken']}\n"
    )
    print(form_text)
    print("\n\n")

#increasing the no of leave taken
user["leave_taken"]+=1
with open(filename, "w") as file:
    json.dump(user, file, indent=4)

print("Created by Nekhal James\n")