import os
import psycopg2
from flask import Flask, Markup, jsonify, request
from passlib.hash import sha256_crypt
from urllib.parse import urlparse

from secret import *

app = Flask(__name__)

@app.route("/")
def test():
	s = Secret()
	return s


@app.route("/secret", methods = ["POST", "GET"])
def secret_page():
	if request.method == "POST":
		return "post"
	else:
		return "get"

@app.route("/secret/<hash>")
def retrieve_secret(hash):
	cur.execute("SELECT * FROM secrets WHERE")