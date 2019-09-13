from sys import argv

import psycopg2
from psycopg2.extras import RealDictCursor

connection_string = argv[1]
conn = psycopg2.connect(connection_string)
cursor = conn.cursor(cursor_factory=RealDictCursor)

radii = ['100', '250', '1000', '5000', '8000']

cursor.execute('DROP INDEX IF EXISTS geobus')
cursor.execute('CREATE INDEX geobus ON bus_stations USING GIST (point)')
conn.commit()

for radius in radii:
    print(radius)

    cursor.execute('ALTER TABLE school_export ADD COLUMN IF NOT EXISTS bus_stop_' + radius + ' INT')
    cursor.execute('UPDATE school_export SET bus_stop_' + radius + ' = ( \
        SELECT COUNT(*) \
        FROM bus_stations \
        WHERE ST_DWithin(school_export.point, bus_stations.point, ' + radius + ') \
    )')

    cursor.execute('ALTER TABLE school_export ADD COLUMN IF NOT EXISTS bus_station_' + radius + ' INT')
    cursor.execute('UPDATE school_export SET bus_station_' + radius + ' = ( \
        SELECT COUNT(*) \
        FROM osm_points \
        WHERE ST_DWithin(school_export.point, osm_points.wkb_geometry, ' + radius + ') \
        AND amenity = \'bus_station\' \
    )')

    conn.commit()
