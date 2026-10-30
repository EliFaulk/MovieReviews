# Movie Review Database
Track, rate, review, and compare any movie in one place using this simple database that comes with a pre-loaded catalogue of Marvel films.
This database can also be shared between multiple people or reviewers, allowing for both collaborative catalogueing and comparing opinions.

## USE CASES
- As a reviewer, I need to be able to quanitfy my rating into a numeric value from 1-100 and write a short review description
- As a reviewer, I need to be able to update values that could change over time, such as my rating and my review description
- As a reviewer, I need to be able to view necessary values to include in my reviews, such as a movie's ID in the database.
- As an admin, I need to be able to insert new rows into either table containing movies or reviews with the appropriate information
- As an admin, I need to be able to change incorrect values in tables as necessary, particularly for incorrect movie information

## BUSINESS RULES
### Structural
- Each reviewer can only have one review per movie
- Every review has a movie ID that references a row of the movies table
### Integrity Constraints
- If a reviewer has a new rating or review they wish to submit for a movie they have already reviewed, their previous rating/review should be updated to fit the new one rather than creating a brand new row.
- A review MUST have a rating, a reviewer, and a movie ID
- A movie entry MUST have a movie title and a release date
- If a movie was published on a self-publishing platform (such as YouTube), the creator/director of the movie should be listed as the distributor
- If a movie is removed from the *Movies* table, any corresponding reviews will be removed from the *Reviews* table
### Derivation Rules
- Movie Profit = `movies.total_revenue` - `movies.budget`
- Is Flop? = `movies.total_revenue` >= (`movies.budget` * 2.5)
- Average In_Database Rating = sum of (`reviews.rating`) / number of ratings
- Average Rating = (`movies.metacritic_score` + `movies.rotten_tomatoes_score` + average in-database rating) / 3'

## ERD
![ERD.png]

## DATA DICTIONARY
### Movies
| Column | Column Type | Description | Constraints |
| - | - | - | - |
| `movie_id` | SERIAL | the identifying ID of every movie in a database (can be different in separate databases) | PRIMARY KEY |
| `movie_name` | VARCHAR(255) | the exact title of the movie | NOT NULL |
| `distributor` | VARCHAR(255) | the main distributor of the movie | none |
| `release_date` | DATE | the release date of the movie, in the format YYYY-MM-DD | NOT NULL |
| `budget` | INT | the budget of the movie, rounded to the nearest dollar | none |
| `opening_weekend_revenue` | BIGINT | the revenue of the movie made during its first 7 days after release, rounded to the nearest dollar | none |
| `north_america_revenue` | BIGINT | the total revenue of the movie made in North America, rounded to the nearest dollar | none |
| `other_revenue` | BIGINT | the total revenue of the movie made anywhere except for North America, rounded to the nearest dollar | none |
| `total_revenue` | BIGINT | the total revenue of the movie, rounded to the nearest dollar | none |
| `metacritic_score` | INT | the rating out of 100 of the movie on Metacritic | none |
| `rotten_tomatoes_score` | INT | the rating out of 100% of the movie on Rotten Tomatoes, stored as a rating out of 100 | none |

### Reviews
|Column | Column Type | Description | Constraints | 
| - | - | - | - |
| `review_id` | SERIAL | the identifying ID of every review in a database | PRIMARY KEY |
| `reviewer` | VARCHAR(255) | the name or username of the reviewer | NOT NULL |
| `movie_id` | INT | the identifying ID of the movie being reviewed based on that movie's ID in the *Movies* table | REFERENCES `movies(movie_id)` ON DELETE CASCADE |
| `rating` | INT | the rating out of 100 of the movie given by the reviewer | NOT NULL |
| `review_description` | TEXT | a short description of the rating given by the reviewer | none |
