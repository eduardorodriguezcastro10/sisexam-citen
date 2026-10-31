DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT table_name, column_name FROM information_schema.columns WHERE column_default LIKE 'nextval%' AND table_schema = 'public') LOOP
        EXECUTE 'SELECT setval(pg_get_serial_sequence(''' || r.table_name || ''', ''' || r.column_name || '''), coalesce(max(' || r.column_name || '), 0) + 1, false) FROM ' || r.table_name || ';';
    END LOOP;
END $$;