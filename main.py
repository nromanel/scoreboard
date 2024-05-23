from flask import Flask, Response, request
from flask import render_template 
from pathlib import Path
from pprint import pprint
import json

BOARD = {}
FILEPATH = "/tmp/scoreboard"

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
            update_board(data)
            return Response(json.dumps({ "success" : True }, indent=4), mimetype='application/json')
        else:
           return Response(json.dumps({ "success" : False, "message" : "Data Incomplete" }, indent=4), mimetype='application/json')
            
        #except:
        #    return Response(json.dumps({ "success" : False, "message" : "Unable to Parse Data" }, indent=4), mimetype='application/json')
        
        
        


def update_board(board_data):
    global BOARD
    BOARD=board_data
    with open(FILEPATH, 'w') as f:
        json.dump(board_data, f)
    pprint(board_data)
    
    
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
    
    app.run(host='0.0.0.0')