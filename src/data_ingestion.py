import os
import csv
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.getenv("DATABASE_URL")
CSV_PATH = os.getenv("CSV_PATH")
BATCH_SIZE = 100_000

def ingest():
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(*) FROM spotify_charts_raw")
    existing = cur.fetchone()[0]
    
    if existing > 0:
        print(f"Already has {existing:,} rows, skipping.")
        con.close()
        return existing
    
    total = 0
    
    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        next(reader)
        
        batch = []
        for row in reader:
            streams = float(row[8]) if row[8] else None
            batch.append((
                row[0], int(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], streams
            ))
            
            if len(batch) >= BATCH_SIZE:
                execute_values(cur, """
                        INSERT INTO spotify_charts_raw (title, rank, date, artist, url, region, chart, trend, streams) VALUES %s""", batch)
                con.commit()
                total += len(batch)
                batch = []
                print(f"    Loaded {total:,} rows....")
        
        if batch:
            execute_values(cur, """
                           INSERT INTO spotify_charts_raw (title, rank, date, artist, url, region, chart, trend, streams) VALUES %s""", batch)
            con.commit()
            total += len(batch)
            
    print(f"Done: {total:,} rows loaded.")
    con.close()
    return total

if __name__ == "__main__":
    ingest()