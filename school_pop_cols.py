CREATE TABLE school_export AS (SELECT * FROM geo_schools);

ALTER TABLE school_export ADD COLUMN school_pop INT;

UPDATE school_export SET school_pop = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
) + (
    SELECT COUNT(*) FROM high_school_students
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
);

ALTER TABLE school_export ADD COLUMN grade_pop_1 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_2 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_3 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_4 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_5 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_6 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_7 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_8 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_9 INT;
ALTER TABLE school_export ADD COLUMN grade_pop_1b INT;
ALTER TABLE school_export ADD COLUMN grade_pop_2b INT;
ALTER TABLE school_export ADD COLUMN grade_pop_3b INT;

UPDATE school_export SET grade_pop_1 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '01 %'
);
UPDATE school_export SET grade_pop_2 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '02 %'
);
UPDATE school_export SET grade_pop_3 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '03 %'
);
UPDATE school_export SET grade_pop_4 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '04 %'
);
UPDATE school_export SET grade_pop_5 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '05 %'
);
UPDATE school_export SET grade_pop_6 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '06 %'
);
UPDATE school_export SET grade_pop_7 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '07 %'
);
UPDATE school_export SET grade_pop_8 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '08 %'
);
UPDATE school_export SET grade_pop_9 = (
    SELECT COUNT(*) FROM students_plus_dates
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '09 %'
);
UPDATE school_export SET grade_pop_1b = (
    SELECT COUNT(*) FROM high_school_students
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '1B %'
);
UPDATE school_export SET grade_pop_2b = (
    SELECT COUNT(*) FROM high_school_students
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '2B %'
);
UPDATE school_export SET grade_pop_3b = (
    SELECT COUNT(*) FROM high_school_students
    WHERE "ANIO" = 2017
    AND "CODIGO_ENTIDAD" = school_code::text
    AND "GRADO" LIKE '3B %'
);


"""
ALTER TABLE school_export ADD COLUMN point GEOGRAPHY;
UPDATE school_export SET point = (
    SELECT point from geo_schools
    WHERE school_export.school_code = geo_schools.school_code
);
"""

ALTER TABLE school_export ADD COLUMN near_schools_pop INT;
CREATE TABLE school_xyz AS (SELECT point, school_pop, school_code FROM school_export WHERE point IS NOT NULL);
UPDATE school_export SET near_schools_pop = (
    SELECT SUM(school_xyz.school_pop) FROM school_xyz
    WHERE school_xyz.school_code != school_export.school_code
    AND ST_DWithin(school_xyz.point, school_export.point, 5000)
);
