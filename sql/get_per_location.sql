SELECT location,
       AVG(latitude) as latitude,
       AVG(longitude) as longitude,
       count(*) as freq
FROM parkingticket
WHERE EXACTISSUINGTIME >= '{startdate}'
AND EXACTISSUINGTIME <= '{enddate}'
group by location
ORDER BY freq DESC
LIMIT '{limit}';

/*
SELECT location, AVG(latitude) as latitude, AVG(longitude) as longitude, count(*) as freq FROM parkingticket group by location ORDER BY freq DESC LIMIT '{limit}';
*/
/*SELECT location,
       AVG(latitude) as latitude,
       AVG(longitude) as longitude,
       count(*) as freq
FROM parkingticket
group by location
ORDER BY freq DESC
LIMIT 10000;
*&

SELECT location,
       AVG(latitude) as latitude,
       AVG(longitude) as longitude,
       count(*) as freq
FROM parkingticket
WHERE EXACTISSUINGTIME >= '2014-09-16'
AND EXACTISSUINGTIME <= '2019-09-16'
group by location
ORDER BY freq DESC
LIMIT 10000000000;

*/
