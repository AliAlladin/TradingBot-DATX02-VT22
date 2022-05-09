\set QUIET true
SET client_min_messages TO WARNING; -- Less talk please.
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;

\set QUIET false
\i tables.sql
\i triggers.sql
\i views.sql
\i inserts.sql

SELECT * FROM Purchase;
SELECT * From Buy;
