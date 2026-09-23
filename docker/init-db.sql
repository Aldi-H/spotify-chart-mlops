CREATE TABLE IF NOT EXISTS spotify_charts_raw (
    id              SERIAL PRIMARY KEY,
    title           TEXT,
    rank            INTEGER,
    date            DATE,
    artist          TEXT,
    url             TEXT,
    region          TEXT,
    chart           TEXT,
    trend           TEXT,
    streams         FLOAT,
    processed_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS spotify_charts_cleaned (
    id              SERIAL PRIMARY KEY,
    title           TEXT,
    rank            INTEGER,
    date            DATE,
    artist          TEXT,
    url             TEXT,
    region          TEXT,
    chart           TEXT,
    trend           TEXT,
    streams         FLOAT,
    processed_at    TIMESTAMP DEFAULT NOW()
);

-- Validation log - records each data 
CREATE TABLE IF NOT EXISTS validation_log (
    id          SERIAL PRIMARY KEY,
    run_id      TEXT,       -- e.g. "20260923_110000"
    check_name  TEXT,       -- e.g. "duplicate_check"
    status      TEXT,       -- "PASS" or "FAIL"
    detail      TEXT,       -- e.g. "Found 1,234 duplicate rows"
    checked_at  TIMESTAMP DEFAULT NOW()
);

-- Indexing
CREATE INDEX IF NOT EXISTS idx_raw_dedup ON spotify_charts_raw (title, rank, date, artist, region, chart);