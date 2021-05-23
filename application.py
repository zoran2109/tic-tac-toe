from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def move():
    if session["turn"] == "O":
        return "X"
    else:
        return "O"

def check_win(board):
    wins = [
            ((0,0), (0,1), (0,2)),
            ((1,0), (1,1), (1,2)),
            ((2,0), (2,1), (2,2)),
            ((0,0), (1,0), (2,0)),
            ((0,1), (1,1), (2,1)),
            ((0,2), (1,2), (2,2)),
            ((0,0), (1,1), (2,2)),
            ((0,2), (1,1), (2,0))
            ]
    for line in wins:
        if board[line[0][0]][line[0][1]] == board[line[1][0]][line[1][1]] == board[line[2][0]][line[2][1]] == session["turn"]:
            return True
    return False

def check_draw(board):
    for line in board:
        if None in line:
            return False
    return True

@app.route("/")
def index():
    if "turn" not in session:
        session["turn"] = "X"
    if "board" not in session:
        session["board"] = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]

    
    return render_template("game.html", game=session["board"], turn=session["turn"])

@app.route("/play/<int:row>/<int:column>")
def play(row, column):
    session["board"][row][column] = session["turn"]
    win = check_win(session["board"])
    if win:
        return render_template("game.html", game=session["board"], turn=session["turn"], win=win)
    if (check_draw(session["board"])):
        return render_template("game.html", game=session["board"], turn=session["turn"], draw = True)
    session["turn"] = move()
    return render_template("game.html", game=session["board"], turn=session["turn"], win=False)

@app.route("/reset")
def reset():
    session["turn"] = "X"
    session["board"] = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]
    return render_template("game.html", game=session["board"], turn=session["turn"])
