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
			redirect_url = f"/secret/{secret.hash}/html"
			return redirect(redirect_url)
		
		else:
			return "invalid content type"
	
	elif request.method == "GET":
		return "get"

	else:
		return "405"

@app.route("/secret/<hash>/<format>")
def retrieve_secret(hash, format="html"):
	secret = Secret()
	secret.get_by_hash(hash)

	if secret.expired:
		return f"Secret expired: {secret.expiry_reason}"
	else:

		secret.create_output(format)

		if format == "json":
			return secret.output
	
		elif format == "xml":
			return "XML output - to be implemented"
		
		elif format == "html":
			return render_template("content.html", content = "secret_details", secret = secret)


if __name__ == "__main__":
	app.run(debug=True)