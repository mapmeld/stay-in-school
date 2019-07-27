from os import system
from sys import argv

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

"""
UPDATE school_geo SET first_grader_count = (SELECT first_graders FROM school_perf WHERE school::text = "CODIGÓ C.E."::text);
UPDATE school_geo SET second_grader_count = (SELECT first_graders - repeat_or_drop FROM school_perf WHERE school::text = "CODIGÓ C.E."::text);

testfix2=> SELECT * FROM school_perf_2017_08 LIMIT 1;
 base_year | base_grade | school_code | students_in_grade | students_in_school | moved | repeated | temp_dropped_out | perm_dropped_out
-----------+------------+-------------+-------------------+--------------------+-------+----------+------------------+------------------
      2017 | 08         | 13351       |                25 |                133 |     1 |        1 |                0 |                1
"""

# get the schools and geo counts
cursor.execute('DROP TABLE IF EXISTS geo_school_1b')
cursor.execute('CREATE TABLE geo_school_1b AS (SELECT * FROM geo_schools)')

# drop columns not needed for predictions
cursor.execute('ALTER TABLE geo_school_1b DROP COLUMN point')
cursor.execute('ALTER TABLE geo_school_1b DROP COLUMN rand')

# add columns for y-values
cursor.execute('ALTER TABLE geo_school_1b ADD COLUMN grad_1b FLOAT')

cursor.execute('UPDATE geo_school_1b SET grad_1b = \
( \
    SELECT (students_in_grade - temp_dropped_out - perm_dropped_out - repeated)::float \
        / students_in_grade::float \
    FROM school_perf_2017_1b \
    WHERE school_perf_2017_1b.school_code::text = geo_school_1b.school_code::text \
    LIMIT 1 \
)')

# get 2b while we are here

# add
cursor.execute('ALTER TABLE geo_school_1b ADD COLUMN grad_2b FLOAT')
cursor.execute('UPDATE geo_school_1b SET grad_2b = \
( \
    SELECT (students_in_grade - temp_dropped_out - perm_dropped_out - repeated)::float \
        / students_in_grade::float \
    FROM school_perf_2017_2b \
    WHERE school_perf_2017_2b.school_code::text = geo_school_1b.school_code::text \
    LIMIT 1 \
)')
conn.commit()
system('sql2csv --db ' + connection_string + ' --query \'SELECT grad_1b, grad_2b FROM geo_school_1b WHERE grad_1b IS NOT NULL AND grad_2b IS NOT NULL \' > grad_2b.csv')

cursor.execute('DROP TABLE geo_school_1b')
conn.commit()

conn.close()
