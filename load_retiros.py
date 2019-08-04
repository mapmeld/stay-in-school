# pip3 install psycopg2
from sys import argv
from os import system

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
years = [2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

# importing CSVs into database
# for year in years:
#     print(year)
#     system('csvsql -v --db ' + connection_string + ' --tables retiros_' + str(year) + ' retiros/' + str(year) + '.csv')

conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

grades = [
    ['ACELERADA'],
    ['ADULTOS'],
    ['CICLO 1', 'CICLO I'],
    ['CICLO 2', 'CICLO II'],
    ['CICLO 3', 'CICLO III'],
    ['EDUC. MEDIA']
]

reasons = {
    'work': ['A','B','C'],
    # DEF to other schools / towns
    'emigrate': ['G'], # left the country
    'pregnant': ['H'],
    'economics': ['I', 'J'],
    # K = school is too far
    # LM = bad student
    # NOPQ = disability, sickness, accident, or natural death
    # S = accidental death
    'crime': ['R', 'T', 'U'], # murder or other serious
    # V = other causes
}

for year in years:
    # cursor.execute('CREATE INDEX retir_' + str(year) + ' ON school_export (school_code)')
    cursor.execute('CREATE INDEX retiroo_' + str(year) + ' ON retiros_' + str(year) + ' ("CÓDIGO C.E.")')
    conn.commit()
    print(year)

    for grade in grades:
        print(grade)

        edu_query = '(UPPER(REPLACE("NIVEL EDUCATIVO", \' \', \'\')) LIKE \'%' + grade[0].replace(' ', '') + '%\''
        if len(grade) > 1:
            edu_query += ' OR UPPER(REPLACE("NIVEL EDUCATIVO", \' \', \'\')) LIKE \'%' + grade[1].replace(' ', '') + '\''
        edu_query += ')'

        col_name = 'retiros_' + str(year) + '_' + grade[0].replace(' ', '').replace('.', '')
        cursor.execute('ALTER TABLE school_export ADD COLUMN ' + col_name + '_total INT')

        # all people leaving (we should already know this, but we want it to be consistent)
        cursor.execute('UPDATE school_export SET ' + col_name + '_total = ( \
            SELECT SUM("ALUMNOS") \
            FROM retiros_' + str(year) + ' \
            WHERE school_code::text = "CÓDIGO C.E."::text \
            AND ' + edu_query + ' \
        )')

        for reason in reasons.keys():
            print(reason)

            reason_col = col_name + '_' + reason
            cursor.execute('ALTER TABLE school_export ADD COLUMN ' + reason_col + ' INT')
            cursor.execute('UPDATE school_export SET ' + reason_col + ' = ( \
                SELECT SUM("ALUMNOS") \
                FROM retiros_' + str(year) + ' \
                WHERE school_code::text = "CÓDIGO C.E."::text \
                AND ' + edu_query + ' \
                AND "COD. CAUSA" IN (\'' + '\',\''.join(reasons[reason]) + '\') \
            )')
    conn.commit()
conn.close()
