import sqlite3
from flask import Flask
from flask import g
from flask import request, jsonify
from flask import render_template, url_for, json


DATABASE = "universe.db" # TODO: Must be passed in sys.args in the final app

app = Flask(__name__)

# Loading universe.db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def build_graph():
    descriptor = ''
    for user in query_db("SELECT * FROM routes"):
        row = [user['origin'], user['destination'], user['travel_time']]
        descriptor += ' '.join(row)+"\n"
    return descriptor


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/graph')
def graph():
    return build_graph()

# Loading millenium-falcon.json
@app.route('/milleniumFalcon')
def showjson():
    data = json.load(open("millenium-falcon.json"))
    return str(data)

# Loading empire.json
@app.route('/json', methods=['POST'])
def json_example():
    """
        Send your json with Postman or Curl
    :return:
    """
    req = request.get_json(silent=True)
    countdown = req['countdown']
    bounty_hunters = req['bounty_hunters']
    print('Information received as json:\n')
    for intel_ in bounty_hunters:
        print(str(intel_)+"\n")
    return("You just posted a json to the web application: {}".format(bounty_hunters[0])
           , 200)


@app.route('/')
def index():
    return "What are the odds ?"


if __name__ == "__main__":
    app.run(debug=True)
