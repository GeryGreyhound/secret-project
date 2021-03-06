import psycopg2

from flask import Flask, Markup

app = Flask(__name__)

class DatabaseConnection:

	config_file = "database.conf"
	
	with open(config_file) as config:
	    db_config = config.read()
	
	connection = psycopg2.connect(db_config)
	connection.autocommit = True
	cursor = connection.cursor()

dbc = DatabaseConnection()

dbc.cursor.execute("SELECT * FROM coinbase_pro LIMIT 1")
test = dbc.cursor.fetchone()

@app.route("/")
def index():
    return Markup(f"<h1>Szia Uram!</h1><p>{str(test)}</p>")