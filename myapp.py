"""
    Flask application main file.
"""

from flask import Flask
from flask import g, request, jsonify, render_template, url_for, json
import os
import pandas as pd
import sqlite3
import solver


app = Flask(__name__)

# Global variable to preview result
path = None
proba = 0
n_explored_path = None


def get_db(db_path):
    """
    Open connection to db file
    :param db_path: <str> Path of the database (db file)
    :return:
    """
    try:
        assert type(db_path) is str
        assert db_path in os.listdir('./')
    except:
        raise Exception('Invalid database path')
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db


def query_db(db_path, query, args=(), one=False):
    """
    Query the database
    :param db_path: <str> Path of the database (db file)
    :param query: <str> SQL like query
        example: "SELECT * FROM routes")
    :param args:
    :param one:
    :return:
    """
    cur = get_db(db_path).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def graphFromDB(db_path):
    """
    Build the Python weighted undirected graph routes from the full fetch of the database
    :param db_path: <str> Path of the database (db file)
    :return: <dict> A graph under the form of a dictionary storing weighted edges (travel time)
        between origin and destination
    """
    try:
        assert type(db_path) is str
        assert db_path  in os.listdir('./')
    except:
        raise Exception("Invalid db pah")
    graph = {}
    # Go through full database
    for row in query_db(db_path, "SELECT * FROM routes"):
        origin, destination = row['origin'], row['destination']
        if origin not in graph:
            graph[row['origin']] = {}
        if destination not in graph:
            graph[row['destination']] = {}
        graph[origin][destination] = int(row['travel_time'])
        graph[destination][origin] = int(row['travel_time'])
    return graph


@app.teardown_appcontext
def close_connection(exception):
    """
    Close connection to the database
    :param exception:
    :return:
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main file for the front end web application
    :return:
    """
    global proba
    global path
    global n_explored_path
    # Load millenium falcon file as json
    milleniumFalcon = json.load(open("millenium-falcon.json"))
    # Load the db path (e.g. universe.db)
    db_path = milleniumFalcon['routes_db']
    # Build the graph
    graph = graphFromDB(db_path)
    # Load empire intelligence json
    empire = request.get_json(silent=True)
    if empire:
        path, n_explored_path, proba = solver.odds(milleniumFalcon, graph, empire)
    return render_template("home.html", path=path,  percentage=proba*100, n_explored_path = n_explored_path)

if __name__ == "__main__":
    app.run(debug=True)
