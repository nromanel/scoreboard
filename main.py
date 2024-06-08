from flask import Flask, Response, request
from flask import render_template 
from pathlib import Path
from pprint import pprint
from time import sleep
import RPi.GPIO as GPIO
import json
import os

GPIO.setmode(GPIO.BOARD)
# Setup RPi TPIC6B595N

DATAIN = 37
DATA_HT = 15
DATA_HO = 13
DATA_INNING = 11
DATA_COUNT = 7
DATA_AT = 5
DATA_AO = 3

            # VCC 5V - Pin 2
#DATAIN = 37 # SERIN - Pin 3
            # Number Outputs - Pin 4-7
            # SRCLR - Pin 8 - Always High - Give 5v
            # OE - Pin 9 - Always Low - go to ground
            # Ground - Pin 10/11
LATCH = 33  # RCK - Pin 12
CLOCK = 31  # SRCK - Pin 13
            # Number Outputs - Pin 14-17
            # SEROUT - Pin 18

for i in [ DATA_IN, DATA_HT, DATA_HO, DATA_INNING, DATA_COUNT, DATA_AT, DATA_AO]:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, False)
    
GPIO.setup(CLOCK, GPIO.OUT)
GPIO.setup(LATCH, GPIO.OUT)

GPIO.output(LATCH, False)    # Latch is used to output the saved data
GPIO.output(CLOCK, False)    # Used to shift the value of DATAIN to the register

BOARD = {}
FILEPATH = "/var/scoreboard/state" + str(os.geteuid())
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
    #Extract home score
    ht, ho = divmod(int(board_data["home"]), 10)

    #extract away score
    at, ao = divmod(int(board_data["away"]), 10)
    
    inning = int(board_data["inning"])
    
    #Formula X^2-x+1 will appropriately translate the integer to the needed binary value. But I might forget how that worked!
    #for i in [ board_data["balls"], board_data["outs"], board_data["strikes"]]:
    #    count_string = count_string + '{0:03b}'.format(((i*i)-i)+1)
    
    count_string = build_count_string(board_data)
    #set Latch low to start sending data
    GPIO.output(LATCH, False)

    for i in range(0, 8):
        pprint(i)
        if ht == 0:
            GPIO.output(DATA_HT, False)
        else:
            GPIO.output(DATA_HT, False if str(numbers[ht])[i] == "0" else True)
        
        GPIO.output(DATA_HO, False if str(numbers[ho])[i] == "0" else True)
        GPIO.output(DATA_INNING, False if str(numbers[inning])[i] == "0" else True)
        GPIO.output(DATA_COUNT, False if str(count_string)[i] == "0" else True)
        
        if at == 0:
            GPIO.output(DATA_AT, False)
        else:
            GPIO.output(DATA_AT, False if str(numbers[at])[i] == "0" else True)
            
        GPIO.output(DATA_AO, False if str(numbers[ao])[i] == "0" else True)

        
        sleep(0.001)
        GPIO.output(CLOCK, True)
        sleep(0.001)
        GPIO.output(CLOCK, False)
        sleep(0.001)

    #set Latch high to finish data transfer
    GPIO.output(LATCH, True)


def print_to_leds_chained(board_data):
    #Order of Chips
    
    #1 - Away Score One's
    #2 - Away Score Ten's
    #3 - Counts (Strikes - Outs - Balls)
    #4 - Inning
    #5 - Home Score One's
    #6 - Home Score Ten's
    
    # Data has to be sent backwards (6->1)
    
    #Extract home score
    ht, ho = divmod(int(board_data["home"]), 10)

    #extract away score
    at, ao = divmod(int(board_data["away"]), 10)
    
    inning = int(board_data["inning"])
    

    #Formula X^2-x+1 will appropriately translate the integer to the needed binary value. But I might forget how that worked!
    #for i in [ board_data["balls"], board_data["outs"], board_data["strikes"]]:
    #    count_string = count_string + '{0:03b}'.format(((i*i)-i)+1)
    
    count_string = build_count_string(board_data)
        
    #set Latch low to start sending data
    GPIO.output(LATCH, False)

    #Send the score data in order
    count = 1
    for data_to_send in [ ht, ho, inning, count_string, at, ao]:
        
    	
        if count == 4:
                #Send the count data first (its last) - since it doesnt leverage the lookup
            for i in count_string:
                #send data
                GPIO.output(DATAIN, False if i == "0" else True)
                #pulse clock line
                sleep(0.001)
                GPIO.output(CLOCK, True)
                sleep(0.001)
                GPIO.output(CLOCK, False)
                sleep(0.001)
            print("done")
        else:
            for i in numbers[data_to_send]:
                #Hacky way of not prepending a 0 when the score is less then 10
                if data_to_send == 0 and (count == 1 or count == 5):
                    GPIO.output(DATAIN, False)
                else:    
                #send data
                    GPIO.output(DATAIN, False if i == "0" else True)
                    
                #pulse clock line
                sleep(0.001)
                GPIO.output(CLOCK, True)
                sleep(0.001)
                GPIO.output(CLOCK, False)
                sleep(0.001)
            print("done")
        count = count + 1
        sleep(0.001)
    
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

def build_count_string(board_data):
    ##### Output wiring for Counts:
    ##### Strikes: 1,2
    ##### Outs: 3,4
    ##### Balls: 5,6,7
    
    count_string = ""
    if int(board_data["strikes"]) == 0:
        count_string = "00"
    elif int(board_data["strikes"]) == 1:
        count_string = "01"
    elif int(board_data["strikes"]) == 2:
        count_string = "11"
        
    if int(board_data["outs"]) == 0:
        count_string = "00" + count_string
    elif int(board_data["outs"]) == 1:
        count_string = "01" + count_string
    elif int(board_data["outs"]) == 2:
        count_string = "11" + count_string
        
    if int(board_data["balls"]) == 0:
        count_string = "0000" + count_string
    elif int(board_data["balls"]) == 1:
        count_string = "0001" + count_string
    elif int(board_data["balls"]) == 2:
        count_string = "0011" + count_string
    elif int(board_data["balls"]) == 3:
        count_string = "0111" + count_string
    
    return count_string
        
        
def update_board(board_data):
    global BOARD
    BOARD=board_data
    #print_to_leds(board_data)
    print_to_leds_chained(board_data)
    with open(FILEPATH, 'w') as f:
        json.dump(board_data, f)
    pprint(board_data)
    return True
    
    
if __name__ == "__main__": 
    
    scoreboard_file = Path(FILEPATH)

    try:
        f = open(FILEPATH)
        BOARD = json.load(f)
        f.close()
    except:
        BOARD = {   "inning" : 1,
                    "home" : 0,
                    "away" : 0,
                    "strikes" : 0,
                    "outs" : 0,
                    "balls" : 0 }
    
    #Setup the scoreboard
    print("Setting Up The Board")
    update_board(BOARD)       
    
    #If running as root run it on port 80
    if os.geteuid() == 0:
        PORT = 80
        
    try:
        app.run(host='0.0.0.0',port=PORT)
    except KeyboardInterrupt:
        GPIO.cleanup()
    
