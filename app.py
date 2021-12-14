import os
import psycopg2
from flask import Flask, Markup, jsonify
from passlib.hash import sha256_crypt

url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
schema = "schema.sql"
conn = psycopg2.connect(db)

cur = conn.cursor()
x = os.environ.get('DATABASE_URL')

app = Flask(__name__)

@app.route("/")
def index():
	cur.execute("SELECT * FROM secrets")
	x = cur.fetchone()
	return "Szia Uram! " + str(x)