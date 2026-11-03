import psycopg
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

# Any User Queries
view_all_movies = "SELECT movie_id, movie_name FROM movies ORDER BY movie_name;"
view_movie_by_name = "SELECT * FROM movies WHERE movie_name == 'The Incredible Hulk';"
view_reviews_for_movie = "SELECT * FROM reviews WHERE movie_id = 12 ORDER BY reviewer;" # Order by reviewer or rating
view_reviews_from_reviewer = "SELECT * FROM reviews WHERE reviewer = 'username' ORDER BY movie_id;" # order by movie_id or rating

# Reviewer Queries (make sure username matches reviewer in all queries)
add_review = """INSERT INTO reviews (reviewer, movie_id, rating, review_description) VALUES ('username', 12, 84, 'Good movie');"""
remove_review = """DELETE FROM reviews WHERE id = 1;"""

# Admin Queries
add_movie = f"""INSERT INTO movies (movie_name, distributor, release_date, budget, opening_weekend_revenue, north_america_revenue, other_revenue, total_revenue, metacritic_score, rotten_tomatoes_score) VALUES ('Movie', 'Distribute Inc.', {datetime.strptime("20081024", "%Y%m%d").date()}, 100000000, 70000000, 200000000, 55000000, 255000000, 98, 20);"""
delete_movie = "DELETE FROM movies WHERE id = 64;"


# Test queries here (change cur.execute)
with psycopg.connect(conn_str) as conn:
	with conn.cursor() as cur:
		cur.execute(view_all_movies)
		rows = cur.fetchall()
		for row in rows:
			print(row)




