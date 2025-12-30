import FreeSimpleGUI as gui
import datetime
import woolies_scraping #will execute immediately if not using __name__ == "__main__" in woolies_scraping script
import coles_scraping
from r_w_user_data import read_user_data, write_user_data
from my_lists import error_popup
import play_video

woolies_last_updated = read_user_data("woolieslastupdated")
coles_last_updated = read_user_data("coleslastupdated")
woolies_cata_url = read_user_data("woolworthscatalink")

def update_catalogue_popup(): 
    global woolies_last_updated
    global coles_last_updated
    global woolies_cata_url
    
    layout = [
    [gui.Text("New specials begin on Wednesday. You only need to do this once a week.")], 
    [gui.HorizontalSeparator()],
    [gui.Text("Woolworths catalogue link: "), gui.Input(key = "wcataurl", default_text= woolies_cata_url), gui.Button("Update!", key = "-WOOLIES-"), gui.Button("Help", key ="woolhelp")],
    [gui.Text(f"Woolworhts catalogue last updated {woolies_last_updated}", key = "-WOOLIESDATE-")],
    [gui.HorizontalSeparator()],
    [gui.Text("Coles catalogue:      "), gui.Button("Update!", key = "-COLES-"), gui.Button("Help", key="coleshelp")],
    [gui.Text(f"Coles catalogue last updated      {coles_last_updated}", key = "-COLESDATE-")]
    ]
    
    window = gui.Window("Update Catalogue", layout, modal=True) #modal disables other windows until popup is dealt with
    while True:
        event, values = window.read()                               #read the popup window
        if event == "-WOOLIES-": #no while true needed
            if values["wcataurl"]:
                write_user_data("woolworthscatalink", values["wcataurl"]) 
                update_cata("Woolworths", window, values["wcataurl"])
            else:
                error_popup("No link provided", "Please provide a url!")
        
        elif event == "-COLES-":
            update_cata("Coles", window, None)

        elif event == "woolhelp":
            play_video.play("update_woolies_cata.mp4")
        elif event =="coleshelp":
            play_video.play("update_coles_cata.mp4")

        elif event == gui.WIN_CLOSED:
            break


def update_cata(supermarket_name, window, url):
    global result
    try:
        if(supermarket_name == "Woolworths"):
            result = woolies_scraping.scrape(url)
        elif(supermarket_name == "Coles"):
            result = coles_scraping.scrape()
            #result = new_coles_scraping.scrape()  
        
        if result == "success":
            error_popup("Success", f"{supermarket_name} catalogue successfully updated")   
        
    except Exception as e:
        error_popup("Error", f"{supermarket_name} update failed, please contact the Piggy")
    
    last_updated = f"{datetime.date.today().strftime('%d/%m/%Y')} {result}" 
    if(supermarket_name == "Woolworths"):
         write_user_data("woolieslastupdated", last_updated)
         window["-WOOLIESDATE-"].update(f"Woolworths catalogue last updated: {last_updated}")
    elif(supermarket_name == "Coles"):
         write_user_data("coleslastupdated", last_updated)
         window["-COLESDATE-"].update(f"Coles catalogue last updated: {last_updated}")