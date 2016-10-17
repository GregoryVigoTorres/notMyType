CREATE ROLE "notmytypeapp"
WITH
LOGIN
ENCRYPTED PASSWORD 'WetIcnevaitPommoubCoygdimGoygyic';

GRANT ALL
ON DATABASE notmytype
TO notmytypeapp;
