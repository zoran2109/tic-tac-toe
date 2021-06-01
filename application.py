from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import copy

app = Flask(__name__)

#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

WINS =  (
            ((0,0), (0,1), (0,2)),
            ((1,0), (1,1), (1,2)),
            ((2,0), (2,1), (2,2)),
            ((0,0), (1,0), (2,0)),
            ((0,1), (1,1), (2,1)),
            ((0,2), (1,2), (2,2)),
            ((0,0), (1,1), (2,2)),
            ((0,2), (1,1), (2,0))
        )

def move(turn):
    if turn == "O":
        return "X"
    else:
        return "O"

def check_win(board):
    for line in WINS:
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == board[line[2][0]][line[2][1]]:
            return board[line[0][0]][line[0][1]]
    return False

def check_draw(board):
    for line in board:
        if None in line:
            return False
    return True

@app.route("/game")
def game():
    # Preparing variables for session (turn, tic-tac-toe grid, game history)
    if "turn" not in session:
        session["turn"] = "X"
    if "board" not in session:
        session["board"] = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]
    if "history" not in session:
        session["history"] = [copy.deepcopy(session["board"])]

    # if first move is computer's, makes the move
    if session["computer"] == session["turn"]:
        values = make_move(session["board"], session["computer"])
        row, column = values
        return redirect(url_for('play', row = row, column = column))
    
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])

@app.route("/play/<int:row>/<int:column>")
def play(row, column):
    # Handles gameplay - moves, checks for a win or draw
    
    # Saves new move
    session["board"][row][column] = session["turn"]
    
    # Saves entry for move history
    session["history"].append(copy.deepcopy(session["board"]))
    
    # Checks for a win and draw and gives feedback
    win = check_win(session["board"])
    if win:
        return render_template("game.html", game=session["board"], turn=session["turn"], win=win, history=session["history"])
    if (check_draw(session["board"])):
        return render_template("game.html", game=session["board"], turn=session["turn"], draw = True, history=session["history"])
    
    # Changes turn
    session["turn"] = move(session["turn"])

    # If it's computer's turn, plays the move
    if session["computer"] == session["turn"]:
        values = make_move(session["board"], session["computer"])
        row, column = values
        return redirect(url_for('play', row=row, column=column))

    return render_template("game.html", game=session["board"], turn=session["turn"], win=False, history=session["history"])

@app.route("/reset")
def reset():
    # Resets the game to initial position (empty board)
    session["turn"] = "X"
    session["board"] = [[None, None, None],
                        [None, None, None],
                        [None, None, None]]
    session["history"] = [copy.deepcopy(session["board"])]
    return redirect(url_for('game'))

@app.route("/previous")
def previous():
    # Loads the previous move in game history
    i = session["history"].index(session["board"])
    if i-1 >= 0:
        session["board"] = copy.deepcopy(session["history"][i-1])
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])

@app.route("/next")
def next():
    # Loads the next move in game history
    i = session["history"].index(session["board"])
    if i-1 <= len(session["history"]):
        session["board"] = copy.deepcopy(session["history"][i+1])
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])


@app.route("/", methods = ['POST', 'GET'])
def start():
    # Resets the variables in session
    session["board"] = [[None, None, None],
                        [None, None, None],
                        [None, None, None]]
    session["history"] = [copy.deepcopy(session["board"])]
    session["computer"] = None
    session["player"] = None
    session["turn"] = "X"

    # Handles the user requests in menu (selecting an opponent - human/computer and side - X/O)
    if request.method == 'POST':
        if request.form['submit-button'] == 'computer':
            return render_template("start.html", start = "side")
        elif request.form['submit-button'] == 'X':
            session["computer"] = "O"
            session["player"] = "X"
            return redirect(url_for('game'))
        elif request.form['submit-button'] == 'O':
            session["computer"] = "X"
            session["player"] = "O"
            return redirect(url_for('game'))

    return render_template("start.html", start = "opponent")

# Minimax algorithm that returns the value for current game position
def minimax (game, turn, depth=0):
    
    # Base case - returns the value with added/substracted length of the game
    # The goal is to grade differentiate between faster and slower win
    result = check_win(game)
    if result == "X":
        return 10-depth
    elif result == "O":
        return -10+depth
    elif check_draw(game):
        return 0
    
    # Makes a list of all available moves in position
    moves = []
    for i in range(3):
        for j in range(3):
            if game[i][j] == None:
                moves.append((i, j))

    # Recursively checks value for every available move and returns the value for optimal play
    if turn == "X":
        value = -10
        for move in moves:
            # Makes a move from the list
            game[move[0]][move[1]] = turn
            # Checks minimax of a new position
            move_value = minimax(game, "O", depth-1)
            # Updates the best value in position
            value = max(value, move_value)
            # Removes the move from the game, preparing for the next iteration
            game[move[0]][move[1]] = None

    if turn == "O":
        value = 10
        for move in moves:
            game[move[0]][move[1]] = turn
            move_value = minimax(game, "X", depth-1)
            value = min(value, move_value)
            game[move[0]][move[1]] = None

    return value

# Check for the best move in given position using minimax
def make_move(game, turn):

    # Makes a list of all available moves in position
    moves = []
    for i in range(3):
        for j in range(3):
            if game[i][j] == None:
                moves.append((i, j))
    
    # Checks minimax for all available moves, stores values in a list
    values=[]
    for move in moves:
        # Makes a move from the list
        game[move[0]][move[1]] = turn
        # Checks minimax
        if turn == "X":
            value = minimax(game,"O")
        elif turn =="O":
            value = minimax(game,"X")          
        values.append(value)
        # Removes the move from the game, preparing for the next iteration
        game[move[0]][move[1]] = None
    
    # Finds the best move according to given value and returns the best move
    if turn == "X":
        if max(values) > 0:
            return moves[values.index(max(values))]
        elif max(values) == 0:
            return moves[values.index(0)]
        else:
            return moves[values.index(max(values))]
    if turn == "O":
        if min(values) < 0:
            return moves[values.index(min(values))]
        elif min(values) == 0:
            return moves[values.index(0)]
        else:
            return moves[values.index(min(values))]