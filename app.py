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
    
    moves = [ str(m) for m in game.get_legal_moves() ]
    return jsonify(moves)


# Serve frontend assets (HTML, CSS, JavaScript, and the PNG pieces)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    # Debug mode is fine for development; for production use a proper WSGI server.
    app.run(debug=True)
