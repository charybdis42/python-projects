import FreeSimpleGUI as gui
import datetime
import json
import copy
import requests
from PIL import Image
import io
from update_catalogue import update_catalogue_popup
from my_lists import view_lists_popup
from list_manipulation import alphabetise_list, search_list, remove_duplicates, price_rank_list, remove_supermarket, discount_rank_list, sort_by_supermarket
from my_lists import error_popup
from r_w_user_data import read_user_data, write_user_data





gui.set_options(
    font=("Helvetica", 14),    # bigger font for all text/buttons/inputs
    #button_element_size=(12, 2),  # wider & taller buttons
    input_elements_background_color="white",
    element_padding=(5, 5)     # more spacing
)

def update_main_table():
    #window["-TABLE-"].update(values=input_data)
    window["-TABLE-"].update(main_table_data)

def read_woolies_and_coles_data():
    global cata_data
    with open("woolies_cata.json", "r") as f:
        cata_data = json.load(f)
    with open("coles_cata.json", "r") as f:
        coles_data = json.load(f)
        cata_data.extend(coles_data) #merge the lists

def convert_to_bytes(img_source, resize=None): #img_source can be a file path (str) or raw bytes.
    if isinstance(img_source, bytes):
        img = Image.open(io.BytesIO(img_source))
    else:
        img = Image.open(img_source)
    
    if resize:
        img.thumbnail(resize)  # keeps aspect ratio
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

def update_product_picture(window, url):
    window["-IMAGECONTAINER-"].update(filename="loading.png")
    try:
        response = requests.get(url)
        png = convert_to_bytes(response.content, resize=(200,200))
        window["-IMAGECONTAINER-"].update(data=png)                      #need a png for the gui. update the data not the filename
    except Exception as e:
        window["-IMAGECONTAINER-"].update(filename="no_image.png")
        print(e, "image retreival failed")


def main_window():
    headings = ["Product", "Price", "Quantifier", "Discount", "Supermarket"]

    layout = [
    [gui.Text("Search Catalogue:"), gui.Input(key="-SEARCH-"), gui.Button("Search"), gui.Text("or"), gui.Button("Search By List"), gui.Button("View Lists")], #use -THISNOTATION- for keys
    [gui.HorizontalSeparator()],
    [gui.Text("Sort By:"), gui.Button("Name"), gui.Button("Price"), gui.Button("Discount"), gui.Button("Supermarket"), gui.Push(), gui.Button("Delete Row")],
    [gui.Table(values=cata_data,
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
    [gui.Button("Update Catalogue"), gui.Button("Reload Catalouge"), gui.Button("Remove Woolworths Items"), gui.Button("Remove Coles Items"), gui.Push(), gui.Image(data=convert_to_bytes("black.png", resize=(200,200)), key ="-IMAGECONTAINER-")] #buttons need keys if some have the same text, or their text changes
     
    ]
    return gui.Window("Scrapey", layout, resizable=True, size =(1400, 800))

def select_list_popup():
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
    [gui.Button("Search!")]
    ]
    window = gui.Window("My Lists", layout, modal=True) #modal disables other windows until popup is dealt with
    selected = []
    while True:
        event, values = window.read()                               
        if event == "-TABLE-":
            selected = values["-TABLE-"]  # list of selected row indices
        elif event == "Search!":
            if selected:
                row_index = selected[0]            #int value
                list_names = list(my_lists.keys()) #the list names is a list of dict keys
                key = list_names[row_index] 
                window.close()
                return my_lists[key], key       
            else: 
                error_popup("Error", "No list selected")
        elif event == gui.WIN_CLOSED:
            return (None, None)
            break
    window.close()              

read_woolies_and_coles_data()
#main_table_data = cata_data
main_table_data = copy.deepcopy(cata_data)
window = main_window() 
main_table_data_alphabatised = False
main_table_data_priced = False
main_table_data_dicounted = False
main_table_data_supermarketed = False

selected = []
#-----------------------------Main Loop---------------------
while True: 
    event, values = window.read()
    if event == gui.WIN_CLOSED:
            break
    
    elif event == "-TABLE-":
        selected = values["-TABLE-"]
        if selected:  # list of row indicies selected in table
            row_index = selected[0]
            row = main_table_data[row_index]
            url = row[5]                         #the url in object
            update_product_picture(window, url)
    
    elif event == "Update Catalogue":
        update_catalogue_popup()
        read_woolies_and_coles_data()
        
        main_table_data = copy.deepcopy(cata_data) #same logic as reload
        window["-SEARCH-"].update("")
        update_main_table()

    elif event == "Remove Woolworths Items":
        main_table_data = remove_supermarket(main_table_data, "Woolworths")
        update_main_table()

    elif event == "Remove Coles Items":
        main_table_data = remove_supermarket(main_table_data, "Coles")
        update_main_table()
    
    elif event == "View Lists":
        view_lists_popup() 

    elif event == "Name": 
        main_table_data = alphabetise_list(main_table_data, main_table_data_alphabatised)
        main_table_data_alphabatised = not main_table_data_alphabatised
        window["-IMAGECONTAINER-"].update(filename="black.png")
        update_main_table()

    elif event =="Price":
        main_table_data = price_rank_list(main_table_data, main_table_data_priced)
        main_table_data_priced = not main_table_data_priced
        window["-IMAGECONTAINER-"].update(filename="black.png")
        update_main_table()

    elif event == "Discount":
        main_table_data = discount_rank_list(main_table_data, main_table_data_dicounted)
        main_table_data_dicounted = not main_table_data_dicounted
        window["-IMAGECONTAINER-"].update(filename="black.png")
        update_main_table()

    elif event == "Supermarket":
        main_table_data = sort_by_supermarket(main_table_data, main_table_data_supermarketed)
        main_table_data_supermarketed = not main_table_data_supermarketed
        window["-IMAGECONTAINER-"].update(filename="black.png")
        update_main_table()

    elif event == "Reload Catalouge":
         main_table_data = copy.deepcopy(cata_data) #deep copy copies nested lists
         window["-SEARCH-"].update("")
         update_main_table()

    elif event == "Search": 
         if values["-SEARCH-"]: #true if not an empty string 
            search_term = values["-SEARCH-"].lower()
            main_table_data = search_list(cata_data, search_term)
            window["-IMAGECONTAINER-"].update(filename="black.png")
            update_main_table()

    elif event == "Search By List":
        search_terms, list_name = select_list_popup()
        if search_terms and list_name:
            output_list = []
            for term in search_terms:
                output_list.append(search_list(cata_data, term))
            output_list = [item for group in output_list for item in group]   #have to unnest the lists
            output_list = remove_duplicates(output_list)
            main_table_data = output_list
            window["-SEARCH-"].update(f"My List: '{list_name}'")
            window["-IMAGECONTAINER-"].update(filename="black.png")        
            update_main_table()

            
    elif event == "Delete Row":
        
        if selected:
            row = selected[0]
            del main_table_data[row]
            update_main_table()
            
            if main_table_data: #delete the row if there are rows, otherwise don't select anything (because there is nothing to select)
                new_selection = row if row < len(main_table_data) else len(main_table_data)-1
                window["-TABLE-"].update(select_rows=[new_selection])
            else:
                window["-TABLE-"].update(select_rows=[])
        else:
            error_popup("Error", "No row selected!")
  
window.close()
