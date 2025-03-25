DO $$ 
DECLARE 
    event_row RECORD;
    seat_num INT;
BEGIN
    FOR event_row IN SELECT id FROM events LOOP
        FOR seat_num IN 1..10 LOOP
            INSERT INTO seats (event_id, seat_number)
            VALUES (event_row.id, 'S' || seat_num);
        END LOOP;
    END LOOP;
END $$;
