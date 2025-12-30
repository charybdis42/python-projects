from math import sqrt
from os import close
from tabnanny import check
from tkinter import Entry

 
class Node:                              #the node class that stores all the info you need about the nodes
    def __init__(self, value, coords):   #when they are constructed, all they have is coords and a value       
        self.value = value
        self.coords = coords
        
    up = None     #the neighbour nodes
    right = None
    down = None
    left = None
    h = None     #the f = g+h values
    g = None
    f = None
    parent = None #its parent, to trace the solution path
    children = [] #its chilren, to be used later
    
def checkCoords(direction, coords):  #this function takes in coordinates and can check the index adjacent to it
    y, x = coords                    #it returns a value if the index it's checking isn't out of bounds
    
    returnX = None          #new values to return
    returnY = None
    
    if (direction == "up"): #set the new values based on the input string. The string isn't neccessary but I didn't realise this until later 
        if (y-1 >= 0):
            returnY = y-1
            returnX = x
    if (direction == "right"):
        if (x+1 <= len(maze[0]) -1):
            returnY = y
            returnX = x+1
    if (direction == "down"):
        if (y+1 <= len(maze) -1):
            returnY = y+1
            returnX = x
    if (direction == "left"):
        if (x-1 >= 0):
            returnY = y
            returnX = x-1
    
    if (returnX is not None):     #only return the values if the values have been successfully reset
        return returnY, returnX
    
def find_node(coords):           #this function gets a node using input coords
    y, x = coords
    
    for node in created_nodes:      #search the node list for it
        if node.coords == coords:
            return node
    return None
            
def find_value(value):           #this function finds a node based on a value. To be used to find the entrance and exit
    for node in created_nodes:
        if node.value == value:
            return node
    return None
    
def find_lowest_f(node_list):     #this function compares f values of nodes in a list
    lowest_f_node = None

    for node in node_list:
        if node.f is not None:
            if lowest_f_node is None or node.f < lowest_f_node.f:
                lowest_f_node = node

    return lowest_f_node      
        
        

maze = [                                           #here's the array in the assignment
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,-1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,1,1,0,0,9,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,1,0,0,0,1,0,1],
[1,0,1,1,1,1,1,1,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,0,1,0,0,0,1,0,1],
[1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
[1,0,0,0,1,0,1,1,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]


created_nodes = []

for y in range(len(maze)):          #nested for loop to cover every cell in the array
    for x in range(len(maze[y])):
        if maze[y][x] != 1:         #only create the node if it's not a wall
            node = Node(maze[y][x], (y,x))            #make the node 
            node.up = checkCoords("up", (y, x))       #the function will return the coords of neighbour cells if they exist
            node.right = checkCoords("right", (y, x))
            node.down = checkCoords("down", (y, x))
            node.left = checkCoords("left", (y, x))
            created_nodes.append(node)              #put the node in a list
            
# print(len(created_nodes))
# counter = 0        
# for y in range(len(maze)):
#     for x in range(len(maze[y])):
#         if maze[y][x] != 1:
#            counter += 1
# print(counter)


exit_node = find_value(9)   #find the entracne and exit nodes
entry_node = find_value(-1)

for node in created_nodes:
    y = node.coords[0]     #decode the coords for use
    x = node.coords[1]
    
    if node.up is not None:            #reset all the coord values to be actual nodes
        node.up = find_node((y-1, x))
    if node.right is not None:        
        node.right = find_node((y, x+1))    
    if node.down is not None:        
        node.down = find_node((y+1, x))
    if node.left is not None:        
        node.left = find_node((y, x-1))
    
    node.children = [c for c in [node.up, node.right, node.down, node.left] if c is not None]   #set the neighbours to be children for the actual algorithm
    node.h = sqrt( (exit_node.coords[1] - node.coords[1])**2 + (exit_node.coords[0] - node.coords[0])**2 ) #the distance formula for each node is calculated
    
    
# for node in created_nodes:
#     print(node.h)

entry_node.g = 0               #all of the intial conditions of the alg
entry_node.f = entry_node.h
open_list = [entry_node]
closed_list = []

while len(open_list) > 0 or exit_node:         #this is the A* alg. For more info, read the pseudo code or the essay
    lowest_f_node = find_lowest_f(open_list)

    for child in lowest_f_node.children:
        
        if child not in open_list and child not in closed_list:
            
            open_list.append(child)
            child.parent = lowest_f_node
            child.g = 1 + child.parent.g
            child.f = child.g + child.h
        
        else:
            check_new_g = 1 + lowest_f_node.g
            
            if check_new_g < child.g:
                child.g = check_new_g
                child.f = child.g + child.h
                child.parent = lowest_f_node
                
    open_list.remove(lowest_f_node)
    closed_list.append(lowest_f_node)
    
    if exit_node in open_list:
        break
            
path = []                        #this adds the solution path to a list by tracing back the parents of nodes
while exit_node is not None:
    path.append(exit_node)
    exit_node = exit_node.parent

path.reverse()             #reverse it cause it's backwards

for node in path:         #using dynamic types again in order to convert the nodes back into co ordinates
    node = node.coords
        
for i in range(len(path)-1):      #decoding the coordinates into instructions 
    result = ( path[i+1].coords[0] - path[i].coords[0], path[i+1].coords[1] - path[i].coords[1] ) 
    
    if result == (-1, 0):  #outputting a string based on the change between 2 co ordinates
        path[i] = "UP"
    elif result == (0, 1):
        path[i] = "RIGHT"
    elif result == (1, 0):
        path[i] = "DOWN"
    elif result == (0, -1):
        path[i] = "LEFT"

path.pop()  #get rid of the last value because we don't need it
        
for direction in path: #print the path
    print(direction)
            

    
       