from flask import Flask, request, render_template
from flask_socketio import SocketIO, send
from werkzeug.utils import secure_filename
import sys
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
print("Upload folder: ", UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

host = "0.0.0.0"
port = 5100

socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
    print("\n\nMessage:", msg, "\n\n")
    send(msg, broadcast=True)

@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')

if __name__ == '__main__':
    # app.run(host=host, port=port)
    socketio.run(app, host=host, port=port, debug=True)