import os

import psycopg
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_cors import CORS
from werkzeug.security import check_password_hash

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5000", "http://192.168.110.243:5000"])

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
			cur.execute("SELECT * FROM movies WHERE movie_id = %s", (movie_id,))
			rows = cur.fetchall()
	return [{"movie_id": r[0], "movie_name": r[1], "distributor": r[2], "release_date": r[3], "budget": r[4], "opening_weekend_revenue": r[5], "north_america_revenue": r[6], "other_revenue": r[7], "total_revenue": r[8], "metacritic_score": r[9], "rotten_tomatoes_score": r[10]} for r in rows]



# View all of a distributor's movies ANY USER
@app.route("/api/distributor/<string:distributor>", methods=["GET"])
def list_distributor(distributor):
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM movies WHERE distributor = %s", (distributor,))
			rows = cur.fetchall()
	return [{"movie_id": r[0], "movie_name": r[1], "distributor": r[2], "release_date": r[3], "budget": r[4], "opening_weekend_revenue": r[5], "north_america_revenue": r[6], "other_revenue": r[7], "total_revenue": r[8], "metacritic_score": r[9], "rotten_tomatoes_score": r[10]} for r in rows]



# View all reviews ANY USER
@app.route("/api/reviews", methods=["GET"])
def list_reviews():
	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM reviews")
			rows = cur.fetchall()
	return [{"review_id": r[0], "reviewer": r[1], "movie_id": r[2], "rating": r[3], "review_description": r[4]} for r in rows]



# Add a review LOGGED IN
@app.route("/api/add_review", methods=["POST"])
@login_required
def add_review():
	data = request.get_json()
	if not data or "movie_id" not in data or "rating" not in data or "review" not in data:
		return {"error": "requires movie_id, rating, and review"}, 400

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("INSERT INTO reviews (reviewer, movie_id, rating, review_description) VALUES (%s, %s, %s, %s)", (current_user.username, data["movie_id"], data["rating"], data["review"],))
	return {"message": f"Added review to {data['movie_id']}"}, 201



# Remove a review LOGGED IN
@app.route("/api/remove_review/<int:movie_id>", methods=["POST"])
@login_required
def remove_review(movie_id):
	deleted = False

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM reviews WHERE reviewer = %s", (current_user.username,))
			rows = cur.fetchall()
			for r in rows:
				if movie_id == r[2]:
					cur.execute("DELETE FROM reviews WHERE reviewer = %s AND movie_id = %s", (current_user.username, movie_id,))
					deleted = True
	if deleted:
		return {"message": f"Removed review for movie_id:{movie_id}"}, 201
	else:
		return {"error": f"No review exists for movie_id:{movie_id}"}, 201



# Add a movie ADMIN (only movie name and release date necessary)
@app.route("/api/add_movie/<string_name>/<string:date>/", defaults={'distributor': "", 'budget': 0, 'opening': 0, 'america': 0, 'other': 0, 'total': 0, 'meta': 0, 'rotten': 0}, methods=["POST"])
@app.route("/api/add_movie/<string:name>/<string:distributor>/<string:date>/<int:budget>/<int:opening>/<int:america>/<int:other>/<int:total>/<int:meta>/<int:rotten>", methods=["POST"])
@login_required
def add_movie(name, distributor, date, budget, opening, america, other, total, meta, rotten):
	if current_user.role != "admin":
		return {"error": "Only admins can edit movie info"}, 403

	date = datetime.strptime(str(date), "%Y%m%d").date()

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("""INSERT INTO movies (movie_name, distributor, release_date, budget, opening_weekend_revenue, north_america_revenue, other_revenue, total_revenue, metacritic_score, rotten_tomatoes_score) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;""", (name, distributor, date, budget, opening, america, other, total, meta, rotten,))
	return {"message": f"Added new movie: '{name}'"}, 201



# Change movie info ADMIN
@app.route("/api/change_release_date/<int:movie_id>/<string:date>", methods=["POST"])
@login_required
def change_release_date(movie_id, date):
	if current_user.role != "admin":
		return {"error": "Only admins can edit movie info"}, 403

	date = datetime.strptime(str(date), "%Y%m%d").date()

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("UPDATE movies SET release_date = %s WHERE movie_id = %s", (date, movie_id,))
	return {"message": f"Changed release date of movie_id:{movie_id} to {date}"}, 201



# Change movie scores ADMIN
@app.route("/api/change_scores/<int:movie_id>/<int:meta>/<int:rotten>", methods=["POST"])
@login_required
def change_scores(movie_id, meta, rotten):
	if current_user.role != "admin":
		return {"error": "Only admins can edit movie info"}, 403

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("UPDATE movies SET metacritic_score = %s & rotten_tomatoes_score = %s WHERE movie_id = %s", (meta, rotten, movie_id,))
	return {"message": f"Changed scores of movie_id:{movie_id} to Metacritic: {meta} and Rotten Tomatoes: {rotten}"}, 201



# Change movie money ADMIN
@app.route("/api/change_money/<int:movie_id>/<int:budget>/<int:opening>/<int:america>/<int:other>/<int:total>", methods=["POST"])
@login_required
def change_money(movie_id, budget, opening, america, other, total):
	if current_user.role != "admin":
		return {"error": "Only admins can edit movie info"}, 403

	with psycopg.connect(conn_str) as conn:
		with conn.cursor() as cur:
			cur.execute("UPDATE movies SET budget = %s & opening_revenue = %s & america_revenue = %s & other_revenue = %s & total_revenue = %s WHERE movie_id = %s", (budget, opening, america, other, total,))
	return {"message": f"Changed budgets and revenues of movie_id:{movie_id}"}, 201





if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)
