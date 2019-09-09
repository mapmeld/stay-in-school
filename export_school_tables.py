from os import system
from sys import argv

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

grades = ['01','02','03','04','05','06','07','08','1b','2b','3b']

for grade in grades[:9]:
    print(grade)
    cursor.execute('DROP TABLE IF EXISTS geo_school_' + grade)

    # get the schools and geo counts
    cursor.execute('CREATE TABLE geo_school_' + grade + ' AS (SELECT * FROM school_export)')

    # drop columns not needed for predictions
    cursor.execute('ALTER TABLE geo_school_' + grade + ' DROP COLUMN point')
    cursor.execute('ALTER TABLE geo_school_' + grade + ' DROP COLUMN rand')
    # for other_grade in grades:
    #     if other_grade != grade:
    #         try:
    #             other_grade = str(int(other_grade))
    #         except:
    #             b = 1
    #         cursor.execute('ALTER TABLE geo_school_' + grade + ' DROP COLUMN grade_pop_' + other_grade)

    # add columns for y-values
    cursor.execute('ALTER TABLE geo_school_' + grade + ' ADD COLUMN grad_' + grade + ' FLOAT')

    cursor.execute('UPDATE geo_school_' + grade + ' SET grad_' + grade + ' = \
    ( \
        SELECT (students_in_grade - perm_dropped_out - repeated)::float \
            / students_in_grade::float \
        FROM school_perf_2016_' + grade + ' \
        WHERE school_perf_2016_' + grade + '.school_code::text = geo_school_' + grade + '.school_code::text \
        LIMIT 1 \
    )')
    conn.commit()
    try:
        grade_col = str(int(grade))
    except:
        grade_col = grade
    system('sql2csv --db ' + connection_string + ' --query \'SELECT * FROM geo_school_' + grade + ' WHERE grade_pop_' + grade_col + ' > 0 AND grad_' + grade + ' IS NOT NULL\' > grad_' + grade + '.csv')

    cursor.execute('DROP TABLE geo_school_' + grade)
    conn.commit()

conn.close()
