import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
conn_str = os.environ["DATABASE_URL"]


view_all_movies = "SELECT movie_id, movie_name FROM movies ORDER BY movie_name;"


with psycopg.connect(conn_str) as conn:
	with conn.cursor() as cur:
		cur.execute(view_all_movies)
		while True:
			cur.fetchone()
			if row is None:
				break




