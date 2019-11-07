import sqlite3
from flask import Flask
from flask import g
from flask import request, jsonify
from flask import render_template, url_for, json
from flask import flash
from collections import defaultdict
import solver
import pandas as pd
import os

app = Flask(__name__)

proba = 0

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
    graph = {}
    for row in query_db(db_path, "SELECT * FROM routes"):
        if row['origin'] not in graph:
            graph[row['origin']] = {}
        graph[row['origin']][row['destination']] = int(row['travel_time'])
    return graph


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def convert_to_csv(graph):
    planets = set()
    sources = []
    targets = []
    weights = []

    for source in graph:
        planets.add(source)
        for dest in graph[source]:
            planets.add(dest)
            sources.append(source)
            targets.append(dest)
            weights.append(graph[source][dest])

    planets = list(planets)
    d = {"id": planets}
    df = pd.DataFrame(d)
    df.to_csv('./static/data/nodes.csv', sep=",", index=False, header=True)

    d = {"source": sources, "target": targets, "weight": weights}
    df = pd.DataFrame(d)
    df.to_csv('./static/data/edges.csv', sep=",", index=False, header=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    print(app.root_path)
    global proba
    # Load millenium-falcon json
    milleniumFalcon = json.load(open("millenium-falcon.json"))
    db_path = milleniumFalcon['routes_db']
    graph = graphFromDB("universe.db")
    if not "nodes.csv" in os.listdir('./static/data/') or not "nodes.csv" in os.listdir('./static/data/'):
        convert_to_csv(graph)
    print("\n Millenium Falcon: \n", milleniumFalcon)
    print("\n Graph: \n", graph)

    # Load empire intelligence json
    empire = request.get_json(silent=True)
    if empire:
        proba = solver.odds(milleniumFalcon, graph, empire)

    return render_template("home.html", percentage=proba*100)

if __name__ == "__main__":
    app.run(debug=True)
