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
def load_user(user_id):
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



# View all movies ANY USER
@app.route("/api/movies", methods=["GET"])
def list_movies():
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT movie_id, movie_name FROM movies ORDER BY movie_name")
			rows = cur.fetchall()
	return [{"movie_id": r[0], "movie_name": r[1]} for r in rows]



# View a movie's information ANY USER
@app.route("/api/movie_info/<int:movie_id>", methods=["GET"])
def list_movie_info(movie_id):
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM movies WHERE movie_id = (%s)", (movie_id,))
			rows = cur.fetchall()
	return [{"movie_id": r[0], "movie_name": r[1], "distributor": r[2], "release_date": r[3], "budget": r[4], "opening_weekend_revenue": r[5], "north_america_revenue": r[6], "other_revenue": r[7], "total_revenue": r[8], "metacritic_score": r[9], "rotten_tomatoes_score": r[10]} for r in rows]



# View all of a distributor's movies ANY USER
@app.route("/api/distributor/<string:distributor>", methods=["GET"])
def list_distributor(distributor):
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM movies WHERE distributor = (%s)", (distributor,))
			rows = cur.fetchall()
	return [{"movie_id": r[0], "movie_name": r[1], "distributor": r[2], "release_date": r[3], "budget": r[4], "opening_weekend_revenue": r[5], "north_america_revenue": r[6], "other_revenue": r[7], "total_revenue": r[8], "metacritic_score": r[9], "rotten_tomatoes_score": r[10]} for r in rows]



# Add a review LOGGED IN
@app.route("/api/add_review/<int:movie_id>/<int:rating>/<string:review_description>", methods=["POST"])
@login_required
def add_review(movie_id, rating, review_description):
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("INSERT INTO reviews (reviewer, movie_id, rating, review_description) VALUES (%s, %s, %s, %s)", (current_user.username, movie_id, rating, review_description,))
	return {"message": f"Added review to {movie_id}"}, 201



# Change movie values ADMIN



if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)
