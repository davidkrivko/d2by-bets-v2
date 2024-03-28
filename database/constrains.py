sql = """
    ALTER TABLE d2by_matches
    ADD CONSTRAINT d2by_matches_unique_constrain UNIQUE (team_1, team_2, d2by_id, d2by_url);
    
    ALTER TABLE bets4pro_matches
    ADD CONSTRAINT bets4pro_matches_unique_constrain UNIQUE (team_1, team_2, id);
    
    ALTER TABLE matches
    ADD CONSTRAINT matches_unique_constrain UNIQUE (team_1, team_2);
    
    CREATE OR REPLACE FUNCTION insert_into_matches()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Check if a matching record already exists in the matches table
        IF EXISTS (
            SELECT 1 FROM matches
            WHERE team_1 = NEW.team_1 AND team_2 = NEW.team_2
        ) THEN
            -- If a matching record exists, do nothing
            RETURN NULL;
        ELSE
            -- If no matching record exists, insert a new record into the matches table
            INSERT INTO matches (team_1, team_2, start_at)
            VALUES (NEW.team_1, NEW.team_2, NEW.start_at);
            RETURN NEW;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    
    
    -- Create a trigger for bets4pro_matches table
    CREATE TRIGGER bets4pro_insert_trigger
    AFTER INSERT ON bets4pro_matches
    FOR EACH ROW
    EXECUTE FUNCTION insert_into_matches();
    
    -- Create a trigger for d2by_matches table
    CREATE TRIGGER d2by_insert_trigger
    AFTER INSERT ON d2by_matches
    FOR EACH ROW
    EXECUTE FUNCTION insert_into_matches();
    
    -- Create a trigger for fansport_matches table
    CREATE TRIGGER fansport_insert_trigger
    AFTER INSERT ON fansport_matches
    FOR EACH ROW
    EXECUTE FUNCTION insert_into_matches();
"""
