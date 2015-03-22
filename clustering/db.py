import mysql.connector

class Db:
	def __init__(self):
		self.conn = mysql.connector.connect(
			user='root', password='', host='localhost', database='mpca')
		self.cursor = self.conn.cursor()
	def execute(self, query, params=()):
		self.cursor.execute(query, params)
		return self.cursor
	def commit(self):
		self.conn.commit()
	def close(self):
		self.cursor.close()
		self.conn.close()
	def insert(self, statement, params=()):
		self.execute(statement, params)
		return self.cursor.lastrowid
	def update(self, statement, params=()):
		self.execute(statement, params)
	def delete(self, statement, params=()):
		self.execute(statement, params)
	def query(self, statement, params=(), cursor=True):
		if cursor:
			return self.execute(statement, params)
		else:
			c = self.conn.cursor()
			c.execute(statement, params)
			result = c.fetchall()
			c.close()
			return result