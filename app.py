import os
import psycopg2
from flask import Flask, Markup, redirect, jsonify, request, render_template
from passlib.hash import sha256_crypt
from urllib.parse import urlparse

from secret_server import *

app = Flask(__name__)

@app.route("/")
def test():
	return render_template("content.html", content = "new_secret")


@app.route("/secret", methods = ["POST", "GET"])
def secret_page():
	if request.method == "POST":
		if request.headers["Content-Type"] == "application/x-www-form-urlencoded":

			secret = Secret()
			secret_text = request.form.get("inputSecret")
			expire_time = request.form.get("inputExpireMinutes")
			expire_views = request.form.get("inputExpireViews")
			secret.create(secret_text, expire_time, expire_views)
			redirect_url = f"/secret/{secret.hash}?format=html"
			return redirect(redirect_url)
		
		else:
			return "invalid content type"
	
	elif request.method == "GET":
		return "get"

	else:
		return "405"

@app.route("/secret/<hash>")
def retrieve_secret(hash):
	default_format = "json"

	secret = Secret()
	secret.get_by_hash(hash)

	if secret.expired:
		return jsonify({"expired" : True, "expiry_reason" : secret.expiry_reason})

	if error in secret.__dict__:
		return jsonify({"error" : secret.error})

	format = request.args.get("format")
	if not format:
		format = default_format	
	
	secret.create_output(format)

	if format == "html":
		return render_template("content.html", content = "secret_details", secret = secret)

	else:
		return secret.output


if __name__ == "__main__":
	app.run(debug=True)