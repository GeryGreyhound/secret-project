from datetime import datetime, timedelta
import psycopg2
import os
from urllib.parse import urlparse
from hashlib import sha256
from flask import jsonify, Markup

class DatabaseConnection:
	def execute_query(self, query_string, query_parameters, fetch=None):
		url = urlparse(os.environ.get('DATABASE_URL'))
		db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
		schema = "schema.sql"
		try:
			connect = psycopg2.connect(db)
			connect.autocommit = True
			cursor = connect.cursor()
		except:
			return "DatabaseConnectionError"
	
		try:
			cursor.execute(query_string, query_parameters)
		except:
			return "DatabaseQueryError"	

		if fetch=="one":
			result = cursor.fetchone()
		elif fetch=="all":
			result = cursor.fetchall()
		else:
			result = None

		connect.close()

		return result
	
class Secret:

	def __init__(self):
		pass

	def create(self, secret_text, expiry_time=60, views_allowed=5):	
		self.created_at = datetime.now()
		self.secret_text = secret_text
		self.hash = sha256(secret_text.encode("utf-8")).hexdigest()
		self.views_allowed = views_allowed
		
		if int(expiry_time) > 0:
			self.expires_at = datetime.now() + timedelta(minutes = int(expiry_time))
		else:
			self.expires_at = None
		

		self.add_to_database()

	def get_by_hash(self,hash,count_view = True):	
		self.hash = hash
		query_string = "SELECT * FROM secrets WHERE hash = (%s)"
		query_parameters = [self.hash]
		dbc = DatabaseConnection()
		result = dbc.execute_query(query_string, query_parameters, fetch="one")
		
		if result and len(result) > 0:
			self.secret_text = result[1]
			self.created_at = result[2]
			self.expires_at = result[3]
			self.views_allowed = result[4]
			self.check_expiry()

			if count_view:
				query_string = "INSERT INTO views VALUES (%s, %s)"
				query_parameters = [datetime.now(), self.hash]
				dbc.execute_query(query_string, query_parameters)

			else:
				pass
				# the first automatic preview should not count as a view and decrease the number of remaining views

		else:
			self.error = "Not found"


	def check_expiry(self):
		self.expired = False

		if self.expires_at and self.expires_at <= datetime.now():
			self.expired = True
			self.expiry_reason = "date"

		else:
			dbc = DatabaseConnection()
			query_string = "SELECT * FROM views WHERE hash = (%s)"
			query_parameters = [self.hash]
			views = dbc.execute_query(query_string, query_parameters, fetch="all")
			
			try:
				if len(views) >= self.views_allowed:
					self.expired = True
					self.expiry_reason = "views"
				else:
					self.remaining_views = self.views_allowed - len(views)
			
			except:
				self.remaining_views = self.views_allowed
	
	def add_to_database(self):
		query_string = "INSERT INTO secrets VALUES (%s, %s, %s, %s, %s)"
		query_parameters = [self.hash, self.secret_text, self.created_at, self.expires_at, self.views_allowed]
		dbc = DatabaseConnection()
		dbc.execute_query(query_string, query_parameters)

	def create_output(self, format):
		if format == "json":
			self.output = jsonify(self.__dict__)

		elif format == "html":
			table_rows = ""
			
			for key, value in self.__dict__.items():
				table_rows += f"<tr><td>{key}</td><td>{value}</tr>\n"

			self.output = Markup(f'''
			<table class="table">
				  <thead>
				    	<tr>
				      		<th scope="col">parameter</th>
				      		<th scope="col">value</th>
				    	</tr>
				  </thead>
				  	<tbody>
				  		{table_rows}
				  	</tbody>
			</table>

			''')
		
		elif format == "xml":
			self.output = "to be implemented..."

