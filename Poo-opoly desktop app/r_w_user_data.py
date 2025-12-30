import json

def write_user_data(variable_name, value):
    with open("user_data.json", "r", encoding="utf-8") as f:
        user_data = json.load(f)
    
    user_data[variable_name] = value
    
    with open("user_data.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def read_user_data(variable_name):
    with open("user_data.json", "r", encoding="utf-8") as f:
        user_data = json.load(f)
    return user_data[variable_name] 

