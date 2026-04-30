import pika
import rabbitmq_logic
import json
import time
import random
#------------------------------------------------------------------------------------
#chess logic fns

people = {}                  #dictionary is suitable because all we need is name and position
collisions = {}              #collisions is also a dictionary of name (key), collided with list (value) 
is_stationary = {}           #this is a dict of people (key) and a bool isStationary = true if they are standing still
publish_board_state = True   #bool for debugging 

#initialise person
def create_person(name, starting_pos):
    name = name.lower()             #transform to lower case
    people[name] = starting_pos     #add to dict
    collisions[name] = []           #create a list of collisions inside the dict for the new person
    is_stationary[name] = False     #they aren't standing still at first
    print("person added to the board: ", name)

def person_exists(name):
    print(collisions)
    if name in collisions:
        return True
    else:
        print("Couldn't find "+name+" in tracker.py")
        return False

#get a random position for the created person
def get_random_pos(board_size):
    x = random.randint(0, board_size-1)
    y = random.randint(0, board_size-1)
    return [x, y]

#check for valid move, and if valid, move them
def move_person(person, move):
    old_pos = people[person]
    new_pos = [old_pos[0] + move[0], old_pos[1] + move[1]] #calculate the new move coords

    #if the move is valid, do the move, othewise do nothing
    if new_pos[0] >= 0 and new_pos[0] <= board_size-1 and new_pos[1] >= 0 and new_pos[1] <= board_size-1:      #check bounds of x and y     
        people[person]= new_pos
        print(person, " moved. Board state: ", people)
        is_stationary[person] = False                 #they moved so they're not stationary
    else:
        print(person, "tried to move off the board")
        #is_stationary[person] = True                  #they are now standing still

    #every time someone gets moved, send the boardstate to query-response for the GUI to update
    message = json.dumps(people)
    if publish_board_state:
        sub.publisher.publish("query_response.board_state", message.encode())

#update the dict object to be sent to other services when queried
def update_collisions(person1, person2): 
    #insert the people into the start of each others collision list
    collisions[person1].insert(0, person2)         
    collisions[person2].insert(0, person1)
    print("collisions: ", collisions)

def check_for_collisions(input_name):
    for name, coords in people.items():
        if name != input_name and coords == people[input_name]:
            
            #if they are both standing still, then don't register the collision, because they are both trying to move off the board and colliding
            if is_stationary[input_name] and is_stationary[name]:
                print("collision didn't register because both people are stationary")
                return
            
            print("collision!")
            update_collisions(input_name, name) #these are the people that collided
            
            #because they have collided, they are now both stationary and cannot collide with eachother
            #the only way to set this back to false is by moving to a new sqaure
            is_stationary[input_name]=True
            is_stationary[name]=True

#check the board size input is valid
def get_board_size():
    while True:
        try:
            n = int(input("Please enter board size (int): "))
            if n>0:
                return n
            else: 
                print("please enter board size greater than 0")
                return get_board_size()
        except ValueError:
            print("Please enter a valid integer")
#-------------------------------------------------------------------------------
#callback fns for receiving messages

#receives input from person service
def process_positions(ch, method, properties, body):
    if method.routing_key == "position.create_person":
        data = body.decode()
        name = json.loads(data)                  #decode json and assign a name. if name is the same. handle name duplication
        initial_pos = get_random_pos(board_size)
        create_person(name, initial_pos)  
      
    elif method.routing_key == "position.update_person":
        data = body.decode()
        data = json.loads(data)
        #decode again
        name = data[0]
        move = data[1]

        #we move the person if valid, then check if they collided, then update dict if they collided
        move_person(name, move)
        check_for_collisions(name) #after they have moved, check whether they are in the same square as anyone else 

#receives input from query service
def process_query(ch, method, properties, body):
    if method.routing_key == "query.get_collisions":
        #body is just the query name
        query_name = body.decode()
        print("recieved query: ",  query_name)

        #send the collsions of the person from the dict
        if person_exists(query_name):
            send = [query_name, collisions[query_name]]  #send a list with key name and value collisions 
            send = json.dumps(send)
            sub.publisher.publish("query_response.collisions", send.encode()) #send the collisions dict back

#--------------------------------------------------------------------------------
#Entry point
#create the pub and sub, connecting to middleware
sub = rabbitmq_logic.Subscriber()
sub.publisher = rabbitmq_logic.Publisher()

#get the board size from input and send it to the gui
board_size = get_board_size()
sub.publisher.publish("query_response.board_size", str(board_size).encode())

#declare queues for pub to publish to and for GUI/query app to use
sub.declare_queue("query_queue")
sub.bind_queue("query_queue", "query.get_collisions")

sub.declare_queue("query_response_queue")
sub.bind_queue("query_response_queue", "query_response.collisions")
sub.bind_queue("query_response_queue", "query_response.board_state")
sub.bind_queue("query_response_queue", "query_response.board_size")
    
#declare the queues it will listen to
sub.declare_queue("position_queue")
sub.declare_queue("query_queue")
sub.subscribe_to_queue("position_queue", process_positions) #declare fns to run when it replies
sub.subscribe_to_queue("query_queue", process_query)

 #this line blocks
sub.start_listening()                                      


















# # we can run this fn when a message comes in from the queue we are subscried to
# def my_callback_fn(ch, method, properties, body): #our callback NEEDS 4 inputs because the message provides us with 4
#     print("messaged recieved:", body.decode())

# #this is the same code from the publisher script. RabbitMQ doesn't care if we run it again to be safe
# connection, channel = rabbitmq_logic.connect_to_middleware()
# channel.queue_declare(queue='example_queue', durable=True)
# _routing_key = "example_routing_key"
# rabbitmq_logic.bind_queue(channel, 'example_queue', _routing_key)

# #subscribe to a queue
# rabbitmq_logic.subscribe_to_queue(channel, 'example_queue', my_callback_fn) #run the callback when messag recieved

# #start receiving messages from our subscriptions 
# channel.start_consuming() #this line blocks the execution of the lines below

# connection.close()