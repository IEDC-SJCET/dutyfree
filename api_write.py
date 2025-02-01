import json

api=input("Enter your API key : ")
temp_dict={"api":api}

with open("api.json", "w") as file:
        json.dump(temp_dict, file, indent=4)