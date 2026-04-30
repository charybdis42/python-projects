import dearpygui.dearpygui as dpg
import threading
import pika
import rabbitmq_logic
import json
import queue #these are thread safe for safe board updates

#------------------------------------------------------------------------------------
#region Visual Variables

#colour palate
red = (229,169,169)
yellow = (234,231,170)
green = (178,214,170)
blue = (172,179,234)
purple = (212,186,219)
white = (238,238,210)
black = (0,0,0,255)
text_red = (255,0,0,255)
light_grey = (224,224,224,255)

#sizes of stuff in gui
viewport_width= 1920   #1080p resolution
viewport_height= 1080

#window sizes
scroll_bar_width = 0
window_head_thickness = 30
chess_window_height = viewport_height * 0.9 + window_head_thickness
chess_window_width = chess_window_height + scroll_bar_width

#chess board sizes
chess_sqaure_length = 90                                     #size of sqaures 
text_padding = 5
max_board_view = 10
#endregion 
#------------------------------------------------------------------------------------------
#region classes

#chess board object to be used in gui. has a dict of players that gets updated for drawing
class Gameboard():
    def __init__(self, size, _offset):
        self.board_size = size
        self.draw_size = 10 if self.board_size > 10 else self.board_size #cap the drawing size of board to 10 at most 
        self.offset_x, self.offset_y = _offset                           #offset is a tuple. can only be positive numbers 
        self.players = {}
    
    def draw_players(self):
        for name, coords in self.players.items():
            #coords player is at
            i = coords[0] 
            j= coords[1]

            #check player is on board, else don't draw anything 
            if self.offset_x > i or i >= self.offset_x + self.board_size:
                continue
            if self.offset_y > j or j >= self.offset_y + self.board_size:
                continue

            start = ((i - self.offset_x ) * chess_sqaure_length, (j - self.offset_y) * chess_sqaure_length + chess_sqaure_length / 2 )                                           
            dpg.draw_text(start, name, color=text_red, size = 30, parent="board_drawlist")

    #the logic that colours the chess board
    def get_colour(self, coord_sum):
        match coord_sum % 10:
            case 1:
                return red
            case 3:
                return yellow
            case 5:
                return green
            case 7:
                return blue
            case 9:
                return purple


    def draw_board(self):
        #nested for loop to draw sqaures
        for i in range(self.draw_size):
            for j in range(self.draw_size):
                #these coords are used for logic 
                x_coord = i + self.offset_x
                y_coord = j + self.offset_y
                coord_sum = i + j + self.offset_x + self.offset_y  

                sqaure_colour = white if (coord_sum)%2 == 0 else self.get_colour(coord_sum)                  #test for even numbers to get square colour
                start = (i * chess_sqaure_length, j * chess_sqaure_length)                                           #topleft corner
                end = (i * chess_sqaure_length + chess_sqaure_length, j * chess_sqaure_length + chess_sqaure_length) #bottomright corner
                #draw the chess sqaure
                dpg.draw_rectangle(
                    start,                                             
                    end, 
                    color=black,                     #border color
                    fill=sqaure_colour,              #fill color
                    thickness=1,
                    parent="board_drawlist")         #tell it where to draw to
                #draw the coords
                text = str(x_coord) +","+ str(y_coord)
                text_pos = (start[0] + text_padding, start[1])
                dpg.draw_text(text_pos, text, color=black, size = 15, parent="board_drawlist")
#endregion
#-----------------------------------------------------------------------------------------------

#region Gui fn's

    #go to new board pos
def move_to_pos(x, y):
    #change the offset values to move the position of the board around
    board.offset_x = x
    board.offset_y = y 


def is_out_of_bounds(new_offset_x, new_offset_y):
    #return if out of bounds
    if new_offset_x < 0 or new_offset_x + max_board_view > board.board_size: #bounds checks. confusing but can be understood if you think hard
        return True
    if new_offset_y < 0 or new_offset_y + max_board_view > board.board_size:
        return True

def on_click_offset_changed(sender, app_data, user_data): 
    #calculate projected offset
    new_offset_x = board.offset_x + user_data[0]
    new_offset_y = board.offset_y + user_data[1]
    
    #if the projected offset is out of bounds, don't offset the board
    if is_out_of_bounds(new_offset_x, new_offset_y):
        return
    
    #move board and update input fields
    move_to_pos(new_offset_x, new_offset_y)
    update_gui_offset()

#jump to position button logic
def on_jump_to_position(sender, app_data, user_data):
    new_x_offset =dpg.get_value(user_data[0]) #retrieve the values from the text fields that were inputted
    new_y_offset= dpg.get_value(user_data[1])

    try:
        new_x_offset = int(new_x_offset)
        new_y_offset = int(new_y_offset)
    except:
        print("strings in int field")
        return

    if is_out_of_bounds(new_x_offset, new_y_offset):
        print("out of bounds")
    else:
        move_to_pos(new_x_offset, new_y_offset)

 #update the input fields
def update_gui_offset():
    dpg.set_value("x_input", board.offset_x)
    dpg.set_value("y_input", board.offset_y)

def player_exists(p):
    return p in board.players

#send query to tracker here
def on_click_query_collisions(sender, app_data, user_data):
    query = dpg.get_value(user_data)
    if not player_exists(query):
        dpg.set_value("query_player_collisions", "Player not found")
    else:
        send = query
        collision_pub.publish("query.get_collisions", send.encode())


#locate player
def on_click_find_player(sender, app_data, user_data):
    print("Players: ")
    print(board.players)
    query = dpg.get_value(user_data)
    if not player_exists(query):
        dpg.set_value("find_player_text", "Player not found")
        return
    
    #we try to jump to player pos. If it's out of bounds, we move (-1,-1) until it's not out of bounds
    player_pos = board.players[query]
    while is_out_of_bounds(player_pos[0], player_pos[1]):
        player_pos = [player_pos[0] - 1, player_pos[1] - 1]
    move_to_pos(player_pos[0], player_pos[1])


#endregion
#----------------------------------------------------------------------------------------------
#region Gui setup

dpg.create_context()

#load the font
with dpg.font_registry():
    futuristic_font = dpg.add_font("assets/font.ttf", 30)
dpg.bind_font(futuristic_font)

#configure theme for visual appearance
with dpg.theme() as window_theme:
    #force window colours
    with dpg.theme_component(dpg.mvWindowAppItem):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (242,240,239,255)) #inactive title bar
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (242,240,239,255)) #active title bar
        
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text,(0, 0, 0, 255)) #black text
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, light_grey) #grey windows
        
        #button stuff
        dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 150, 250, 255)) #blue buttons
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 170, 255, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (250, 197, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (0, 60, 180, 255))

    #text input theme
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0,0,0,255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255,255,255,255), category=dpg.mvThemeCat_Core) #white text


#create the main window
dpg.create_viewport(title="Task 3 Visualiser", width=viewport_width, height=viewport_height)
dpg.setup_dearpygui()
dpg.show_viewport()
#endregion
#------------------------------------------------------------------------------------------
#region listen to rabbit for board size and create board object

#use a set because it's mutable. Could also use a global variable
bs = set()

#wait for board size message
def get_board_size(ch, method, properties, body):
    
    #get the board size then close the connection and continue the script
    if method.routing_key == "query_response.board_size":
        bs.add(int(body.decode())) 
        bs_sub.end()

bs_sub = rabbitmq_logic.Subscriber()
bs_sub.subscribe_to_queue("query_response_queue", get_board_size)

#this line blocks. will continue running when it has received the board size
bs_sub.start_listening()         

#when the message has been recieved, create the object
board = Gameboard(bs.pop(), (0,0))     #0,0 is no offset 


#endregion
#------------------------------------------------------------------------------------------
#region create gui windows

#add stuff into the inner window
#the chess board
with dpg.window(label="Live Board", tag= "live_board"):
    with dpg.drawlist(tag = "board_drawlist", width=chess_window_width, height=chess_window_height):
        pass    #don't draw anything yet

#the offset control pannel and find player pannel. make it if board is big
if board.board_size > max_board_view:
    
    #offset
    with dpg.window(label="Board Offset", tag = "board_offset"):
        with dpg.group(horizontal=True):
            dpg.add_button(label="-", tag="decrease_x", callback=on_click_offset_changed, user_data=(-1,0)) #send the offset data into the callback
            dpg.add_text("X")
            dpg.add_button(label="+", tag="increase_x", callback=on_click_offset_changed, user_data=(1,0))
            dpg.add_input_text(tag = "x_input", width = 139, default_value=board.offset_x)
        with dpg.group(horizontal=True):
            dpg.add_button(label="-", tag="decrease_y", callback=on_click_offset_changed, user_data=(0,-1))  #y is flipped because canvas draws from top of screen
            dpg.add_text("Y")
            dpg.add_button(label="+", tag = "increase_y", callback=on_click_offset_changed, user_data=(0,1))
            dpg.add_input_text(tag = "y_input", width = 139, default_value=board.offset_y)
        dpg.add_button(label = "Jump to Position", tag="jump_to_pos", callback=on_jump_to_position, user_data=("x_input", "y_input")) #send the text input values to fn
    dpg.bind_item_theme("board_offset", window_theme)

    #find player
    with dpg.window(label= "Find Player", tag = "find_player"):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag = "find_player_text", default_value= "Enter Player Name")
            dpg.add_button(label="Find", callback=on_click_find_player, user_data="find_player_text")
    dpg.bind_item_theme("find_player", window_theme)
    

#the collisions query pannel
with dpg.window(label="Query Collisions",  tag = "query_collisions"):
    with dpg.group(horizontal=True):
        dpg.add_input_text(tag="query_player_collisions", default_value= "Enter Player Name")
        dpg.add_button(label="Query", callback=on_click_query_collisions, user_data="query_player_collisions")
    

#bind the windows to my theme
dpg.bind_item_theme("live_board", window_theme)
dpg.bind_item_theme("query_collisions", window_theme)


#endregion   
#---------------------------------------------------------------------------------------------
#region render loop and rabbit thread

#make the update queue for rabbit to write updates into
update_queue = queue.Queue()


#subscriber responses here
def respond_to_queries(ch, method, properties, body):
    #rewrite all the people in the board when an update comes in
    global board_update
    if method.routing_key == "query_response.board_state":
        data = body.decode()
        data = json.loads(data)
        update_queue.put(data)
    
    if method.routing_key == "query_response.collisions":
        dpg.set_value("query_player_collisions", "Response in Terminal")
        data = body.decode()
        data = json.loads(data)
        name = data[0]
        collisions = data[1] #collisions is a list
        
        print(name, ": Collisions (reverse chronological order):")
        for col in collisions:
            print(col)
      

#main rabbit fn
def rabbit_thread_logic():
    sub = rabbitmq_logic.Subscriber()          #publish and subscribe
    sub.publisher = rabbitmq_logic.Publisher()
    
    sub.subscribe_to_queue("query_response_queue", respond_to_queries) #listen to query-response for incoming collision queries
    sub.start_listening() #blocks here. It's ok though because it's in another thread

#start the rabbit thread here
threading.Thread(target=rabbit_thread_logic, daemon=True).start()

#we also need to make another publisher to send collision queries from the main thread
collision_pub = rabbitmq_logic.Publisher()

#the imgui loop (like a gameloop)
while dpg.is_dearpygui_running():
    #delete the previous canvas
    dpg.delete_item("board_drawlist", children_only=True)

    #first update the board with the thread safe queue
    while not update_queue.empty():
        update = update_queue.get()
        board.players = update

    # Draw fresh frame
    board.draw_board()
    board.draw_players()

    dpg.render_dearpygui_frame()

dpg.destroy_context() #clean up
collision_pub.end()
#endregion