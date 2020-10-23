SELECT userid, movieid,
    (rating - MIN(rating) OVER (PARTITION BY userId))/((MAX(rating) OVER (PARTITION BY userId))-(MIN(rating) OVER (PARTITION BY userid))) AS rating_deviance_simplex,
    AVG(rating) OVER(PARTITION BY userid) as avg_rating
FROM(
    SELECT DISTINCT userid, movieid, rating
    FROM movie.ratings
    LIMIT 1000
) as sample
ORDER BY userid, rating DESC 
LIMIT 30;