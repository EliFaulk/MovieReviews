import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, request
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from werkzeug.security import check_password_hash

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
	def __init__(self, user_id, username, role):
		self.id = user_id
		self.username = username
		self.role = role



@login_manager.user_loader
def load user (user_id):
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute(
				"SELECT user_id, username, role FROM app_user WHERE user_id = %s",
				(int(user_id),),
			)
			row = cur.fetchone()
	if row is None:
		return None
	return User(row[0], row[1], row[2])



@login_manager.unauthorized_handler
def unauthorized():
	return {"error": "You must log in first"}, 401



@app.route("/api/login", methods=["POST"])
def login():
	data = request.get_json()
	if not data or "username" not in data or "password" not in data:
		return {"error": "username and password are required"}, 400

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute(
				"SELECT user_id, username, role, password_hash FROM app_user WHERE username = %s",
				(data["username"],),
			)
			row = cur.fetchone()

	if row is None or not check_password_hash(row[3], data["password"]):
		return {"error": "Wrong username or password"}, 401

	login_user(User(row[0], row[1], row[2]))
	return {"message": f"Logged in as {row[1]}",  "role": row[2]}



@app.route("/api/logout", methods=["POSTS"])
@login_required
def logout():
	logout_user()
	return {"message": "Logged out"}



@app.route("/api/categories", methods=["GET"])
def list_categories():
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT movie_id, title FROM movies ORDER BY title")
			rows = cur.fetchall()
	return [{"category_id": r[0], "name": r[1]} for r in rows]


