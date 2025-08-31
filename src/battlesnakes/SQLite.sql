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
