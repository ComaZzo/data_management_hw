SELECT 'ФИО: Чуваев Павел Сергеевич';

-- 1
SELECT 
    * 
FROM movie.ratings 
LIMIT 10;

SELECT 
    * 
FROM movie.links 
WHERE 
    imdbid LIKE '%42' 
    AND movieid > 100 
    AND movieid < 1000;

-- 2
SELECT
    imdbid,
    rating 
FROM movie.links 
JOIN movie.ratings
    ON movie.ratings.movieid = movie.ratings.movieid
WHERE movie.ratings.rating = 5
LIMIT 10;

-- 3
SELECT 
    count(*) 
FROM movie.ratings 
RIGHT JOIN movie.links
    ON movie.ratings.movieid=movie.links.movieid
WHERE movie.ratings.rating IS NULL;

SELECT
    userId,
    AVG(rating) as avg_rating
FROM movie.ratings
GROUP BY userId
HAVING AVG(rating) > 3.5
LIMIT 10;

-- 4
SELECT
   imdbid,
   AVG(rating) as avg_rating
FROM movie.links
JOIN movie.ratings
   ON movie.ratings.movieid=movie.links.movieid
GROUP BY imdbid
HAVING AVG(rating)>3.5
LIMIT 10;

WITH tmp_table
AS (
    SELECT userid, COUNT(*)
    FROM movie.ratings
    GROUP BY userid
    HAVING COUNT(*) > 10)
SELECT 
    AVG(rating) AS active_user_rating
FROM movie.ratings
JOIN tmp_table
    ON movie.ratings.userid = tmp_table.userid;
