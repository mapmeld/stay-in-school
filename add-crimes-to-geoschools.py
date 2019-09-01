from sys import argv

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

years = ['2010', '2011', '2014', '2015']
crimes = ['robos', 'hurtos', 'homicidios']
radii = ['100', '250', '1000', '5000', '8000']

for radius in radii:
    for crime in crimes:
        for year in years:
            print(year + ' ' + crime + ' ' + radius)
            # geo index helper
            cursor.execute('DROP INDEX IF EXISTS geoi_' + crime + '_' + year)
            cursor.execute('CREATE INDEX geoi_' + crime + '_' + year + ' ON geocoded_' + crime + '_' + year + ' USING GIST (point)')
            conn.commit()

            # do count
            cursor.execute('ALTER TABLE school_export ADD COLUMN IF NOT EXISTS ' + crime + '_' + year + '_' + radius + ' INT')
            cursor.execute('UPDATE school_export SET ' + crime + '_' + year + '_' + radius + ' = ( \
                SELECT COUNT(*) \
                FROM geocoded_' + crime + '_' + year + ' \
                WHERE ST_DWithin(school_export.point, geocoded_' + crime + '_' + year + '.point, ' + radius + ') \
            )')

        # sum crimes
        cursor.execute('ALTER TABLE school_export ADD COLUMN IF NOT EXISTS ' + crime + '_' + str(radius) + '_allyrs INT')
        cursor.execute('UPDATE school_export SET ' + crime + '_' + str(radius) + '_allyrs = ' +
            ' + '.join([
                crime + '_' + radius,
                crime + '_2010_' + radius,
                crime + '_2011_' + radius,
                crime + '_2014_' + radius,
                crime + '_2015_' + radius
            ]))
        conn.commit()
