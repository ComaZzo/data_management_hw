-- SELECT 'ФИО: Чуваев Павел Сергеевич';

CREATE TABLE IF NOT EXISTS movie.content_genres (
    movieid INT, 
    genre TEXT);

COPY movie.content_genres 
FROM '/usr/share/data_store/raw_data/genres.csv' 
DELIMITER ',' 
CSV HEADER;

WITH top_rated AS(
SELECT
    movieid,
    avg_rating
FROM(
    SELECT
        movieid,
        AVG(rating) OVER (PARTITION BY movieid) as avg_rating
    FROM movie.ratings
) as avg_res
GROUP BY movieid, avg_rating
HAVING COUNT(movieId) > 50
ORDER BY avg_rating DESC, movieid
LIMIT 150)

SELECT 
    top_rated.movieid,
--    avg_rating,
    genre
INTO movie.top_rated_tags
FROM movie.content_genres
RIGHT JOIN top_rated
    ON movie.content_genres.movieid=top_rated.movieid

\COPY (SELECT * FROM movie.top_rated_tags) 
TO '/usr/share/data_store/raw_data/top_rated_tags_file.csv' 
WITH CSV HEADER 
DELIMITER as E'\t';
