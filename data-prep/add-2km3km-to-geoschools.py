from sys import argv

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

crimes = ['robos', 'hurtos', 'homicidios']
radii = ['2000', '3000']
year = '2016'

for radius in radii:
    for crime in crimes:
        print(year + ' ' + crime + ' ' + radius)

        # do count
        cursor.execute('ALTER TABLE school_export ADD COLUMN IF NOT EXISTS ' + crime + '_' + radius + ' INT')
        cursor.execute('UPDATE school_export SET ' + crime + '_' + radius + ' = ( \
            SELECT COUNT(*) \
            FROM geocoded_' + crime + ' \
            WHERE ST_DWithin(school_export.point, geocoded_' + crime + '.point, ' + radius + ') \
        )')
        conn.commit()
