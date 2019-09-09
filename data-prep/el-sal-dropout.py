# load other Python libraries
# pip3 install psycopg2 csvkit
from sys import argv
from os import system

# set up database
import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

min_year = 2010
max_year = 2017 # 2018
deleting_tables = False

school_levels = {
    #'students_plus_dates': [
    #    '01','02','03','04','05','06','07','08','09'
    #],
    'high_school_students': [
       '1B', '2B', '3B', '4B'
    ]
}

# our goal is to find out if each year
# did each STUDENT move, repeat, drop temporarily, or drop permanently

for year in range(min_year, max_year):
    # range only goes to max_year - 1, but when year=2017, next_year=2018
    next_year = year + 1
    print(str(year) + ' to ' + str(next_year))
    for sktype in school_levels.keys():
        for grade in school_levels[sktype][:-1]:
            # again we save the last year to be next_grade = grade + 1
            next_grade = school_levels[sktype][school_levels[sktype].index(grade) + 1]
            print('from ' + str(year) + ' ' + grade + ' to ' + next_grade)

            table_name = 'progress_' + str(year) + '_' + grade + '_to_' + next_grade

            cursor.execute('DROP TABLE IF EXISTS ' + table_name)

            if deleting_tables:
                conn.commit()
                continue

            # why not add school here?
            # because school is sorted alphabetically, we won't know if school_a was Year1 or Year2
            cursor.execute('CREATE TABLE ' + table_name + ' AS \
            (SELECT \
                start_year AS base_year, \
                \'' + grade + '\' AS base_grade, \
                "NIE", \
                (school_a != school_b) AS moved, \
                (start_year = end_year) AS temp_dropped_out, \
                ((start_grade = end_grade) AND (start_year != end_year)) AS repeated, \
                \'00000\' AS school_code, \
                FALSE AS perm_dropped_out \
            FROM ( \
                SELECT "NIE", \
                MIN("ANIO") AS start_year, MAX("ANIO") AS end_year, \
                MIN("GRADO") AS start_grade, MAX("GRADO") AS end_grade, \
                MIN("CODIGO_ENTIDAD") AS school_a, MAX("CODIGO_ENTIDAD") AS school_b \
                FROM ' + sktype + ' \
                WHERE ("GRADO" LIKE \'' + grade + '%\' AND "ANIO" = ' + str(year) + ') \
                OR "ANIO" = ' + str(next_year) + ' \
                GROUP BY "NIE" \
            ) AS foo \
            WHERE start_year = ' + str(year) + ')')

            print("to set perm dropped out")

            # need the full range of years to find out if the student PERMANENTLY dropped out
            # this value will be higher for 2016/2017 as we just didn't see them come back yet
            cursor.execute('UPDATE ' + table_name + ' \
                SET perm_dropped_out = ( \
                    base_year = ( \
                        SELECT MAX("ANIO") \
                        FROM ' + sktype + ' \
                        WHERE ' + sktype + '."NIE" = ' + table_name + '."NIE" \
                    ) \
                ) WHERE temp_dropped_out')

            # can't be temporarily dropped out, if you are permanently dropped out
            cursor.execute('UPDATE ' + table_name + ' SET temp_dropped_out = NOT perm_dropped_out WHERE temp_dropped_out')

            # index the big student table
            cursor.execute('CREATE INDEX ' + table_name + '_i ON ' + table_name + ' (school_code)')

            # add the school ID
            # we only add one ID, so I added an ORDER BY RANDOM() for which school gets the student that year
            cursor.execute('UPDATE ' + table_name + ' SET school_code = ( \
                SELECT "CODIGO_ENTIDAD" FROM ' + sktype + ' \
                WHERE "ANIO" = ' + str(year) + ' \
                    AND "GRADO" LIKE \'' + grade + '%\' \
                    AND ' + sktype + '."NIE" = ' + table_name + '."NIE" \
                ORDER BY RANDOM() \
                LIMIT 1 \
            )')

            ## generate annual + grade + school CSVs
            ## we will glue these together later for export
            school_perf = 'school_perf_' + str(year) + '_' + grade
            cursor.execute('DROP TABLE IF EXISTS ' + school_perf)
            cursor.execute('CREATE TABLE ' + school_perf + ' AS  ( \
                SELECT \
                    base_year,base_grade,school_code, \
                    COUNT(*) AS students_in_grade \
                FROM ' + table_name + ' \
                GROUP BY base_year, school_code, base_grade \
            )')
            conn.commit()
            # create an index to match school_perf with the students
            cursor.execute('CREATE INDEX ' + school_perf + '_i ON ' + school_perf + ' (school_code)')
            conn.commit()

            print('students in school count')
            cursor.execute('ALTER TABLE ' + school_perf + ' ADD students_in_school INT')
            cursor.execute('UPDATE ' + school_perf + ' SET students_in_school = ( \
                SELECT COUNT(*) FROM ' + sktype + ' \
                WHERE "ANIO" = ' + str(year) + ' \
                AND ' + sktype + '."CODIGO_ENTIDAD" = ' + school_perf + '.school_code \
            )')

            for action in ['moved', 'repeated', 'temp_dropped_out', 'perm_dropped_out']:
                print(action)
                cursor.execute('ALTER TABLE ' + school_perf + ' ADD ' + action + ' INT')
                cursor.execute('UPDATE ' + school_perf + ' SET ' + action + ' = ( \
                    SELECT COUNT(*) FROM ' + table_name + ' \
                    WHERE ' + action + ' \
                    AND ' + school_perf + '.school_code = ' + table_name + '.school_code \
                )')
            conn.commit()


    # combine grade-by-grade tables into one big table
    # annual_school_perf = 'school_perf_' + str(year)
    # unions = []
    # for sktype in school_levels.keys():
    #     for grade in school_levels[sktype][:-1]:
    #         unions.append('(SELECT * FROM school_perf_' + str(year) + '_' + grade + ')')
    # cursor.execute('CREATE TABLE ' + annual_school_perf + ' AS (' + ' UNION '.join(unions) + ')')
    # conn.commit()
    #
    # # export the big annual table as a CSV
    # system('sql2csv --db ' + connection_string + ' --query \'SELECT * FROM ' + annual_school_perf + ' ORDER BY school_code, base_grade\' > ' + annual_school_perf + '.csv')
    #
    # # clean up leftover school tables
    # cursor.execute('DROP TABLE ' + annual_school_perf)
    # #for grade in school_levels[sktype][:-1]:
    # #    school_perf = 'school_perf_' + str(year) + '_' + grade
    # #    cursor.execute('DROP TABLE ' + school_perf)
    # conn.commit()
conn.close()
