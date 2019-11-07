import sqlite3
from flask import Flask
from flask import g
from flask import request, jsonify
from flask import render_template, url_for, json
from collections import defaultdict
import solver

app = Flask(__name__)

proba = None

# Loading universe.db
def get_db(db_path):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


def query_db(db_path, query, args=(), one=False):
    cur = get_db(db_path).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def graphFromDB(db_path):
    graph = defaultdict(list)
    for row in query_db(db_path, "SELECT * FROM routes"):
        graph[row['origin'].lower()].append((row['destination'].lower(), int(row['travel_time'])))
    return graph


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    global proba
    # Load millenium-falcon json
    milleniumFalcon = json.load(open("millenium-falcon.json"))
    db_path = milleniumFalcon['routes_db']
    graph = graphFromDB("universe.db")
    # Load json
    req = request.get_json(silent=True)
    if req:
        countdown = req['countdown']
        bounty_hunters = req['bounty_hunters']
        proba = solver.odds(milleniumFalcon, graph, countdown, bounty_hunters)
        print("Survival proba:", proba)
    return "Send a json using POST request to this page. The proba of survival is {}".format(proba)

if __name__ == "__main__":
    app.run(debug=True)
