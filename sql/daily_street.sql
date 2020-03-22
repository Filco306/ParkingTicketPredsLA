SELECT
  exactissuingtime::DATE as dateissued,
  STR_NM as StreetName,
  COUNT(*) as Count
  FROM PARKINGTICKET
  WHERE EXTRACT(year from exactissuingtime) >= '{minyear}'
  GROUP BY dateissued, STREETNAME
  ORDER BY DATEISSUED;
