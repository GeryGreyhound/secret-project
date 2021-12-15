from datetime import datetime, timedelta
import psycopg2
import os
from urllib.parse import urlparse
from hashlib import sha256
from flask import jsonify

class DatabaseConnection:
	def execute_query(self, query_string, query_parameters, fetch=None):
		url = urlparse(os.environ.get('DATABASE_URL'))
		db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
		schema = "schema.sql"
		try:
			conn = psycopg2.connect(db)
			cur = conn.cursor()
		except:
			return "DatabaseConnectionError"
	
		try:
			cur.execute(query_string, query_parameters)
		except:
			return "DatabaseQueryError"	

		if fetch=="one":
			result = cur.fetchone()
		elif fetch=="all":
			result = cur.fetchall()
		else:
			result = None

		conn.close()

		return result
	
class Secret:

	def __init__(self):
		pass

	def create(self, secret_text, expiry_time=60, views_allowed=5):	
		self.created_at = datetime.now()
		self.secret_text = secret_text
		self.hash = sha256(secret_text.encode("utf-8")).hexdigest()
		self.expires_at = datetime.now() + timedelta(minutes = int(expiry_time))
		self.views_allowed = views_allowed

		self.add_to_database()

	def get_by_hash(self,hash,count_view = True):	
		self.hash = hash
		query_string = "SELECT * FROM secrets WHERE hash = (%s)"
		query_parameters = [self.hash]
		dbc = DatabaseConnection()
		result = dbc.execute_query(query_string, query_parameters, fetch="one")
		
		if len(result) > 0:
			self.secret_text = result[1]
			self.created_at = result[2]
			self.expires_at = result[3]
			self.views_allowed = result[4]
			self.check_expiry()

			if count_view:
				query_string = "INSERT INTO views VALUES (%s, %s)"
				query_parameters = [datetime.now(), self.hash]

			else:
				pass
				# the first automatic preview should not count as a view and decrease the number of remaining views

		else:
			self.error = "Not found"


	def check_expiry(self):
		self.expired = False

		if self.expires_at <= datetime.now():
			self.expired = True
			self.expiry_reason = "date"

		else:
			dbc = DatabaseConnection()
			query_string = "SELECT * FROM views WHERE hash = (%s)"
			query_parameters = [self.hash]
			views = dbc.execute_query(query_string, query_parameters, fetch="all")
			
			if not "Error" in views:
				if len(views) >= self.views_allowed:
					self.expired = True
					self.expiry_reason = "views"
				else:
					self.remaining_views = self.views_allowed - len(views)

	def add_to_database(self):
		query_string = "INSERT INTO secrets VALUES (%s, %s, %s, %s, %s)"
		query_parameters = [self.hash, self.secret_text, self.created_at, self.expires_at, self.views_allowed]
		
		dbc = DatabaseConnection()
		dbc.execute_query(query_string, query_parameters)

	def create_output(self, format):
		if format == "json":
			self.output = jsonify(self.__dict__)

		elif format == "html":
			pass
		
		elif format == "xml":
			self.output = "to be implemented..."

