import FreeSimpleGUI as gui
from r_w_user_data import write_user_data, read_user_data
from list_manipulation import alphabetise_list

def update_mylists_table():
    window["-TABLE-"].update(values=[[k] for k in my_lists.keys()]) #convert dict keys to list

def error_popup(window_name, message):
    layout = [
    [gui.Text(message)],          ]
    window = gui.Window(window_name, layout, modal=True)
    event, values = window.read()

def edit_list_popup(name, list_items):
    global my_lists
    list_string = ", ".join(list_items)

    layout =[
        [gui.Text("List Name: "), gui.Input(default_text= name, key="-NAME-")],
        [gui.Text("Items:"), gui.Multiline(default_text = list_string, size=(40, 10), key="-LISTTERMS-")],
        [gui.Button("Done"), gui.Button("Cancel")]
    ]
    
    window = gui.Window("Edit List", layout, modal=True)
    selected = []
    while True:
        event, values = window.read() #we need values because of gui.Input() in the layout                              
        if event == gui.WIN_CLOSED: 
            break   
        elif event == "Cancel":
            break
        elif event == "Done": 
            if values["-NAME-"] and values["-LISTTERMS-"]: #true if there's user input for both fields
                #todo add name check
                del my_lists[name]
                add_list = values["-LISTTERMS-"].lower().split(", ")
                add_list = sorted(add_list)
                list_name = values["-NAME-"].lower()
                my_lists[list_name] = add_list
                update_mylists_table()
                write_user_data("userlists", my_lists)
                break
        

    window.close()
        
def view_lists_popup(): 
    global window
    global my_lists
    selected = []
    my_lists = read_user_data("userlists")
    headings = ["My Lists"]
    layout = [
     [gui.Table(
            #values=my_lists.keys(),
            values=[[k] for k in my_lists.keys()], #convert dict keys to list
            headings=headings,
            key="-TABLE-",
            enable_events=True,
            auto_size_columns=False,
            col_widths=[60, 10, 10],
            display_row_numbers=False,
            justification="left",
            row_height=25,
            expand_x = True,
            expand_y= True,
            alternating_row_color="grey" 
    )],
    [gui.Button("Add List"), gui.Button("Edit/View List"), gui.Button("Delete List")]
    ]
    
    window = gui.Window("My Lists", layout, modal=True) #modal disables other windows until popup is dealt with
    selected = []
    while True:
        event, values = window.read()                               
        if event == "-TABLE-":
            selected = values["-TABLE-"]  # list of selected row indices
        elif event == "Add List":
            add_list_popup()
        elif event =="Edit/View List":
            if selected:
                row_index = selected[0]            #int value
                list_names = list(my_lists.keys()) #the list names is a list of dict keys
                key = list_names[row_index]        
                edit_list_popup(key, my_lists[key])
            else:
                error_popup("Error", "No list selected ")
        elif event == "Delete List":
            if selected:
                if are_you_sure_popup():
                    row_index = selected[0]            #int value
                    list_names = list(my_lists.keys()) #the list names is a list of dict keys
                    key = list_names[row_index]        
                    del my_lists[key]
                    write_user_data("userlists", my_lists) 
                    update_mylists_table()
            else: 
                error_popup("Error", "No list selected")
        
        
        elif event == gui.WIN_CLOSED:
            break
    window.close()

def add_list_popup():
    global my_lists
    layout =[
        [gui.Text("List Name:"), gui.Input(key="-NAME-")],
        [gui.Text("Items:"), gui.Multiline(size=(40, 10), key="-LISTTERMS-")],
        [gui.Text("Example: 'berries', 'chocolate', 'yogurt'"), gui.Button("Done")]
    ]
    
    window = gui.Window("Add List", layout, modal=True)
    while True:
        event, values = window.read() #we need values because of gui.Input() in the layout                              
        if event == gui.WIN_CLOSED:
            break
        
        elif event == "Add Item":
            print("item added")
        
        elif event == "Done": 
            if values["-NAME-"] and values["-LISTTERMS-"]: #true if there's user input for both fields
                #todo add name check
                add_list = values["-LISTTERMS-"].lower().split(", ")
                add_list = sorted(add_list)
                list_name = values["-NAME-"].lower()
                my_lists[list_name] = add_list
                update_mylists_table()
                write_user_data("userlists", my_lists)
                break

            else:
                error_popup("Error", "Please enter a name and search items")

    window.close()

def are_you_sure_popup():
    global my_lists
    layout =[
        [gui.Text("Are you sure?: "), gui.Button("Yes")],
    ]
    window = gui.Window("Are you sure?", layout, modal=True)
    while True:
        event, values = window.read()                               
        if event == gui.WIN_CLOSED:
            break  
        elif event == "Yes":
            window.close()
            return True
    window.close()