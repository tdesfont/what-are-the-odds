import sqlite3
from flask import g, Flask

DATABASE = "universe.db" # TODO: Must be passed in sys.args in the final app

app = Flask(__name__)


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


@app.route('/')
def index():
    return build_graph()

if __name__ == "__main__":
    app.run(debug=True)