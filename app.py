import os
import psycopg2
from flask import Flask, Markup, jsonify, request, render_template
from passlib.hash import sha256_crypt
from urllib.parse import urlparse

from secret_server import *

app = Flask(__name__)

@app.route("/")
def test():
	s = Secret()
	return render_template("index.html")


@app.route("/secret", methods = ["POST", "GET"])
def secret_page():
	if request.method == "POST":
		# create secret
		pass
	else:
		return "get"

@app.route("/secret/<hash>")
def retrieve_secret(hash):
	s = Secret()
	s.retrieve(hash)
	return "s"
	