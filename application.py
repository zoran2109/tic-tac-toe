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

def check_win(board, turn):
    for line in WINS:
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == board[line[2][0]][line[2][1]] == turn:
            return True
    return False

def check_draw(board):
    for line in board:
        if None in line:
            return False
    return True

@app.route("/game")
def game():
    if "turn" not in session:
        session["turn"] = "X"
    if "board" not in session:
        session["board"] = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]
    if "history" not in session:
        session["history"] = [copy.deepcopy(session["board"])]
    if session["computer"] == session["turn"]:
        values = minimax(session["board"], session["computer"])
        row, column = values[1]
        return redirect(url_for('play', row = row, column = column))
    
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])

@app.route("/play/<int:row>/<int:column>")
def play(row, column):
    session["board"][row][column] = session["turn"]
    win = check_win(session["board"], session["turn"])
    session["history"].append(copy.deepcopy(session["board"]))
    if win:
        return render_template("game.html", game=session["board"], turn=session["turn"], win=win, history=session["history"])
    if (check_draw(session["board"])):
        return render_template("game.html", game=session["board"], turn=session["turn"], draw = True, history=session["history"])
    session["turn"] = move(session["turn"])
    if session["computer"] == session["turn"]:
        values = minimax(session["board"], session["computer"])
        row, column = values[1]
        return redirect(url_for('play', row = row, column = column))
    return render_template("game.html", game=session["board"], turn=session["turn"], win=False, history=session["history"])

@app.route("/reset")
def reset():
    session["turn"] = "X"
    session["board"] = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]
    session["history"] = [copy.deepcopy(session["board"])]
    return redirect(url_for('game'))

@app.route("/previous")
def previous():
    i = session["history"].index(session["board"])
    if i-1 >= 0:
        session["board"] = copy.deepcopy(session["history"][i-1])
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])

@app.route("/next")
def next():
    i = session["history"].index(session["board"])
    if i-1 <= len(session["history"]):
        session["board"] = copy.deepcopy(session["history"][i+1])
    return render_template("game.html", game=session["board"], turn=session["turn"], history=session["history"])


@app.route("/", methods = ['POST', 'GET'])
def start():
    session["board"] = [[None, None, None],
                        [None, None, None],
                        [None, None, None]]
    session["history"] = [copy.deepcopy(session["board"])]
    session["computer"] = None
    session["player"] = None
    session["turn"] = "X"

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


def computer_move(board):
    for line in WINS:
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == session["computer"]:
            if board[line[2][0]][line[2][1]] == None:
                return line[2]
        elif board[line[0][0]][line[0][1]] == board[line[2][0]][line[2][1]] == session["computer"]:
            if board[line[1][0]][line[1][1]] == None:
                return line[1]
        elif board[line[2][0]][line[2][1]] == board[line[1][0]][line[1][1]] == session["computer"]:
            if board[line[0][0]][line[0][1]] == None:
                return line[0]

    for line in WINS: 
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == session["player"]:
            if board[line[2][0]][line[2][1]] == None:
                return line[2]
        elif board[line[0][0]][line[0][1]] == board[line[2][0]][line[2][1]] == session["player"]:
            if board[line[1][0]][line[1][1]] == None:
                return line[1]
        elif board[line[2][0]][line[2][1]] == board[line[1][0]][line[1][1]] == session["player"]:
            if board[line[0][0]][line[0][1]] == None:
                return line[0]

    moves = ((0,0), (2,2), (0,2), (2,0), (1,1), (0,1), (1,0), (1,2), (2,1))
    for line in moves:
        if board[line[0]][line[1]] == None:
            return line

def check_win1(board):
    for line in WINS:
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == board[line[2][0]][line[2][1]]:
            return board[line[0][0]][line[0][1]]


def minimax (game, turn):
    result = check_win1(game)
    if result == "X" or result == "O":
        if result == "X":
            return (1,())
        elif result == "O":
            return (-1,())
    elif check_draw(game):
        return (0,())
    
    game = copy.deepcopy(game)
    moves = []
    for i in range(3):
        for j in range(3):
            if game[i][j] == None:
                moves.append((i, j))
                

    win = []
    even = []
    lose = []
    if turn == "X":
        value = -1
        for move in moves:
            game1 = copy.deepcopy(game)
            game1[move[0]][move[1]] = turn
            value1 = minimax(game1, "O")

            value = max(value, value1[0])
            if value == 1:
                win.append(move)
            elif value == 0:
                even.append(move)
            else:
                lose.append(move)

    if turn == "O":
        value = 1
        for move in moves:
            game1 = copy.deepcopy(game)
            game1[move[0]][move[1]] = turn
            value1 = minimax(game1, "X")

            value = min(value, value1[0])
            if value == -1:
                win.append(move)
            elif value == 0:
                even.append(move)
            else:
                lose.append(move)

    if len(win) > 0:
        return (value, win[0])
    elif len(even) > 0:
        return (value, even[0])
    else:
        return (value, lose[0])
    