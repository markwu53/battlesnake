-- SQLite
CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO test (name) VALUES ('Alice');

select *
from test;

drop table test;

CREATE TABLE example (
    id INTEGER PRIMARY KEY,       -- INTEGER affinity
    name VARCHAR(50),             -- TEXT affinity
    price DECIMAL(10,2),          -- NUMERIC affinity
    active BOOLEAN,               -- NUMERIC affinity (stored as 0/1)
    created_at DATETIME,          -- NUMERIC affinity
    file_data BLOB                -- NONE affinity
);

-- Insert mixed types
INSERT INTO example (name, price, active, created_at) VALUES
('Apple', '3.99', 1, '2025-08-30'),
('Banana', 2.5, 0, 1693383600);  -- Unix timestamp

select *
from example;

drop table game_turn;
create table game_turn (
    game_id varchar(50)
    , game_turn int
    , food text
    , insert_date date
);

drop table snake;
create table snake (
    snake_id varchar(50)
    , name text
    , health int
    , body text
    , game_id varchar(50)
    , game_turn int
);

delete from game_turn;
delete from snake;

drop table decision;
create table decision (
    game_id varchar(50)
    , game_turn int
    , decision_order int
    , decision text
);

select *
from game_turn;

select *
from snake;

--out json

with
snake_agg as (

select a.*
--, b.name || b.health || b.body bline
, '{' || '"name": "' || b.name || '"'
|| ', ' || '"health": ' || b.health
|| ', ' ||'"body": ' || b.body || '}'
snake
from game_turn a
join snake b on a.game_id = b.game_id and a.game_turn = b.game_turn
where 1=1
and a.game_id = 'ad5c44ea-805a-441d-8645-ad336340c304'
and a.game_turn = 300
)

select '{' 
|| '"id": "' || game_id || '"'
|| ', ' || '"food": [' || food || ']'
|| ', ' || '"snakes": [' || group_concat(snake, ',') || ']'
|| '}'
from snake_agg
;

