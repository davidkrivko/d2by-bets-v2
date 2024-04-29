sql = """
ALTER TABLE bets4pro_bets
ADD CONSTRAINT bets4pro_bets_unique_constrain UNIQUE (hash);

ALTER TABLE d2by_bets
ADD CONSTRAINT d2by_bets_unique_constrain UNIQUE (d2by_id);

ALTER TABLE matches
ADD CONSTRAINT matches_unique_constrain UNIQUE (team_1, team_2);

ALTER TABLE fansport_matches
ADD CONSTRAINT fansport_matches_unique_constrain UNIQUE (match_id);

ALTER TABLE d2by_matches
ADD CONSTRAINT d2by_matches_unique_constrain UNIQUE (match_id);

ALTER TABLE bets4pro_matches
ADD CONSTRAINT bets4pro_matches_unique_constrain UNIQUE (match_id);

CREATE OR REPLACE FUNCTION insert_into_site_table()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.additional_data->>'site' = 'bets4pro' THEN
        INSERT INTO bets4pro_matches (match_id, team_1, team_2, start_at, is_live, is_reverse, url, bets4pro_id)
        VALUES (
            NEW.id,
            NEW.team_1,
            NEW.team_2,
            NEW.start_at,
            (NEW.additional_data->>'is_live')::bool,
            (NEW.additional_data->>'is_reverse')::bool,
            (NEW.additional_data->>'url')::varchar,
            (NEW.additional_data->>'bets4pro_id')::varchar
        )
        ON CONFLICT (match_id) DO UPDATE
        SET start_at = EXCLUDED.start_at,
            is_live = (EXCLUDED.is_live),
            url = EXCLUDED.url;
    ELSIF NEW.additional_data->>'site' = 'd2by' THEN
        INSERT INTO d2by_matches (match_id, team_1, team_2, start_at, game, team_1_short, team_2_short, d2by_id, url)
        VALUES (
            NEW.id,
            NEW.team_1,
            NEW.team_2,
            NEW.start_at,
            (NEW.additional_data->>'game')::varchar,
            (NEW.additional_data->>'team_1_short')::varchar,
            (NEW.additional_data->>'team_2_short')::varchar,
            (NEW.additional_data->>'d2by_id')::varchar,
            (NEW.additional_data->>'url')::varchar
        )
        ON CONFLICT (match_id) DO UPDATE
        SET start_at = EXCLUDED.start_at,
            game = EXCLUDED.game,
            team_1_short = EXCLUDED.team_1_short,
            team_2_short = EXCLUDED.team_2_short,
            d2by_id = EXCLUDED.d2by_id,
            url = EXCLUDED.url;
    ELSIF NEW.additional_data->>'site' = 'fansport' THEN
        INSERT INTO fansport_matches (match_id, team_1, team_2, start_at, is_live, sub_matches, url)
        VALUES (
            NEW.id,
            NEW.team_1,
            NEW.team_2,
            NEW.start_at,
            (NEW.additional_data->>'is_live')::bool,
            (NEW.additional_data->>'sub_matches')::varchar,
            (NEW.additional_data->>'url')::varchar
        )
        ON CONFLICT (match_id) DO UPDATE
        SET start_at = EXCLUDED.start_at,
            is_live = (EXCLUDED.is_live),
            sub_matches = EXCLUDED.sub_matches,
            url = EXCLUDED.url;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER insert_site_specific_trigger
AFTER INSERT OR UPDATE ON matches
FOR EACH ROW
EXECUTE FUNCTION insert_into_site_table();
"""
