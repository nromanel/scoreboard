from flask import Flask, Response, request
from flask import render_template 
from pathlib import Path
from pprint import pprint
import RPi.GPIO as GPIO
import json
import os

GPIO.setmode(GPIO.BOARD)
# Setup RPi TPIC6B595N
            # VCC 5V - Pin 2
DATAIN = 37 # SERIN - Pin 3
            # Number Outputs - Pin 4-7
            # SRCLR - Pin 8 - Always High - Give 5v
            # OE - Pin 9 - Always Low - go to ground
            # Ground - Pin 10/11
LATCH = 33  # RCK - Pin 12
CLOCK = 31  # SRCK - Pin 13
            # Number Outputs - Pin 14-17
            # SEROUT - Pin 18

GPIO.setup(DATAIN, GPIO.OUT)
GPIO.setup(CLOCK, GPIO.OUT)
GPIO.setup(LATCH, GPIO.OUT)

GPIO.output(LATCH, False)    # Latch is used to output the saved data
GPIO.output(CLOCK, False)    # Used to shift the value of DATAIN to the register
GPIO.output(DATAIN, False)   # Databit to be shifted into the register
BOARD = {}
FILEPATH = "/tmp/scoreboard"
PORT = 5000

numbers = [
    "00111111",  # 0
    "00000110",  # 1
    "01011011",  # 2
    "01001111",  # 3
    "01100110",  # 4
    "01101101",  # 5
    "01111101",  # 6
    "00000111",  # 7
    "01111111",  # 8
    "01101111",  # 9
]

def print_to_leds(board_data):
    
    #Order of Chips
    #1 - Home Score Ten's
    #2 - Home Score One's
    #3 - Away Score Ten's
    #4 - Away Score One's
    #5 - Inning
    
    #6 - Counts (Strikes - Outs - Balls)
    ##### Output wiring for Counts:
    ##### Strikes: 1,2
    ##### Outs: 3,4
    ##### Balls: 5,6,7
    
    # Data has to be sent backwards (6->1)
    
    #Extract home score
    ht, ho = divmod(board_data["home"], 10)

    #extract away score
    at, ao = divmod(board_data["away"], 10)
    
    inning = board_data["inning"]
    
    #build Binary string for count
    count_string = ""
    
    #Formula X^2-x+1 will appropriately translate the integer to the needed binary value. But I might forget how that worked!
    #for i in [ board_data["balls"], board_data["outs"], board_data["strikes"]]:
    #    count_string = count_string + '{0:03b}'.format(((i*i)-i)+1)
    
    if board_data["strike"] == 0:
        count_string = "00"
    elif board_data["strike"] == 1:
        count_string = "01"
    elif board_data["strike"] == 2:
        count_string = "11"
        
    if board_data["outs"] == 0:
        count_string = "00" + count_string
    elif board_data["outs"] == 1:
        count_string == "01" + count_string
    elif board_data["outs"] == 2:
        count_string == "11" + count_string
        
    if board_data["balls"] == 0:
        count_string == "0000" + count_string
    elif board_data["balls"] == 1:
        count_string == "0001" + count_string
    elif board_data["balls"] == 2:
        count_string == "0011" + count_string
    elif board_data["balls"] == 3:
        count_string == "0111" +count_string
        

    #set Latch low to start sending data
    GPIO.output(LATCH, False)
    
    #Send the count data first (its last) - since it doesnt leverage the lookup
    for i in count_string:
        #send data
        GPIO.output(DATAIN, False if i == "0" else True)
        #pulse clock line
        GPIO.output(CLOCK, True)
        GPIO.output(CLOCK, False)
        
    #Send the score data in order
    count = 1
    for data_to_send in [ inning, ao, at, ho, ht]:
    
        for i in numbers[data_to_send]:
            
            #Hacky way of not prepending a 0 when the score is less then 10
            if data_to_send == 0 and (count == 2 or count == 4):
                GPIO.output(DATAIN, False)
            else:    
            #send data
                GPIO.output(DATAIN, False if i == "0" else True)
                
            #pulse clock line
            GPIO.output(CLOCK, True)
            GPIO.output(CLOCK, False)
        count = count + 1
   
    #set Latch high to finish data transfer
    GPIO.output(LATCH, True)


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/board',methods=['GET','POST'])
def handle_data():
    if request.method == 'GET':
        return Response(json.dumps(BOARD, indent=4), mimetype='application/json')
        
    elif request.method == 'POST':
        
        data = request.get_json()
        if all(key in data for key in ("inning", "home", "away", "strikes", "balls", "outs")):
            result = update_board(data)
            return Response(json.dumps({ "success" : True }, indent=4), mimetype='application/json')
        else:
           return Response(json.dumps({ "success" : False, "message" : "Data Incomplete" }, indent=4), mimetype='application/json')
            
        #except:
        #    return Response(json.dumps({ "success" : False, "message" : "Unable to Parse Data" }, indent=4), mimetype='application/json')
        
        
        
def update_board(board_data):
    global BOARD
    BOARD=board_data
    print_to_leds(board_data)
    with open(FILEPATH, 'w') as f:
        json.dump(board_data, f)
    pprint(board_data)
    return True
    
    
if __name__ == "__main__": 
    
    scoreboard_file = Path(FILEPATH)
    if scoreboard_file.is_file():
        try:
            f = open(FILEPATH)
            BOARD = json.load(f)
            f.close()
        except:
            pass
    else:
        BOARD = {   "inning" : 1,
                    "home" : 0,
                    "away" : 0,
                    "strikes" : 0,
                    "outs" : 0,
                    "balls" : 0 }
    
    #Setup the scoreboard
    update_board(BOARD)       
    
    #If running as root run it on port 80
    if os.geteuid() == 0:
        PORT = 80
        
    try:
        app.run(host='0.0.0.0',port=PORT)
    except KeyboardInterrupt:
        GPIO.cleanup()
    
