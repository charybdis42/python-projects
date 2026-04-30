import pika             #the lib that uses AMQP to connect to rabbitmq
import rabbitmq_logic   #my script with rabbitmq pika fns
import json             #for sending messages
import random           #for position stuff
import time             #for sleep 

def get_name():
    print("Please enter name of person: ")
    name = input()
    if name == "":
        print("please enter a valid name")   
        return get_name()
    else:
        return name 

def get_speed():
    print("Please enter movement speed (slow/medium/fast): ")
    speed = input()
    if speed == "slow" or speed == "medium" or speed == "fast":
        return speed
    else:
        print("incorrect speed input, please try again")
        return get_speed()                                  #use recursion to run the fn again

def decode_speed(value):
    if value == "slow":
        return 2
    elif value == "medium":
        return 1
    elif value == "fast":
        return 0.5

#movement fns
def random_movement():
    values = [-1, 0, 1]
    x = random.choice(values)
    y = random.choice(values)
    if x == 0 and y == 0:         #if x and y are both 0, get a new move
        return random_movement()
    else:
        return [x, y]
#-------------------------------------------------------------------------------------------------

#make the publisher object
pub = rabbitmq_logic.Publisher()

#declare the queue and routing key the pub will use
pub.declare_queue("position_queue")
pub.bind_queue("position_queue", "position.create_person")
pub.bind_queue("position_queue", "position.update_person")

#main cli logic
print("Welcome to the person-creator service")    
#get inputs
name = get_name()
user_speed = get_speed()

#encode in json and send the name
data = name 
message = json.dumps(data)
pub.publish("position.create_person", message.encode()) #send to queue with first key

#continuously send board updates based on speed 
user_speed = decode_speed(user_speed)
while True:
    data = [name, random_movement()]
    message = json.dumps(data)
    pub.publish("position.update_person", message.encode()) #send to queue with second key
    time.sleep(user_speed)















