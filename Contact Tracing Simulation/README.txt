-This is a uni project. It simulates contact tracing using rabbitmq
-You can create people and add them to the board. You can visualise the board and watch them move around
-See the jpeg for a better idea of what is happening

Instructions for using:

1. run the docker command from the assignment brief:
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

2. make sure python is updated to the latest version (3.14.3)

3. run the following commands in a terminal to get dependencies:
	pip install dearpygui
	pip install pika

4. run command in working dir to create the tracker
	python tracker.py
   follow the prompts to create board size. board can be as big as you want

5. run command "python gui.py" to open the gui

6. run command "python person.py" and follow the prompts to make a person. do this as many times as you want

7. Using the GUI:
	-if board is big, use 'find player' window to locate a player by name
	-query a players collisions. the output appears in the gui terminal
	-use the offset window to move the board around if the board is big
	-enter values manually and jump to a position on the board

8. Cleanup:
	-delete rabbit queues and exchanges in web client on local host. this will prevent erroring if you run the 
	 program again due to messages being stuck in queues. 
	 If the program errors after closing everything, it is because of old messages. Just start the procedure again
	 and it will be fine :)   	