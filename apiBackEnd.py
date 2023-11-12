import torrent_lister
import json
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

@app.route('/popular-movies',methods=['GET'])
def index():
    torrentList = torrent_lister.getPopular("movies")
    print(torrentList)
    return torrentList
app.run(host="0.0.0.0", port=5000, threaded=True)