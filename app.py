from flask import Flask, request, jsonify, send_from_directory
import os

from Chezz import *

app = Flask(__name__, static_folder='static')

game = Chezz()

@app.route('/beg', methods=['GET'])
def beg():
    return game.__str__(), 200, {'Content-Type': 'text/plain'}

@app.route('/legal_moves', methods=['GET'])
def legal_moves():
    # Retrieve legal moves from the current game state.
    moves = game.get_legal_moves()    # now a list of (piece,from,to)
    # Convert each tuple to a list so jsonify can encode it
    return jsonify([ [p, f, t] for p,f,t in moves ])

@app.route('/next_move', methods=['POST'])
def next_move():
    data = request.get_json()
    user_move = data.get('move')

    # 1) Apply the user’s move
    game.board = game.board.generate_board_after_move(user_move)

    # # 2) Generate the AI’s response
    best_move = game.max_score(game, 2)[1]
    game.board = game.board.generate_board_after_move(best_move)

    # 3) Grab the new board state
    #    You can return either FEN or your position‐object
    updated_position = game.board.to_fen() 

    # 4) Send back both moves and new position
    return jsonify({
        'user_move': user_move,
        'ai_move':    best_move,
        'updated_position': updated_position
})

# Serve frontend assets (HTML, CSS, JavaScript, and the PNG pieces)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/reset', methods=['POST'])
def reset():
    global game
    game = Chezz()   # or: game.reset() if you implement a reset() method
    # send back the fresh position so the UI can sync immediately
    return jsonify({ 'updated_position': game.board.to_fen() })

if __name__ == '__main__':
    # Debug mode is fine for development; for production use a proper WSGI server.
    app.run(debug=True)
