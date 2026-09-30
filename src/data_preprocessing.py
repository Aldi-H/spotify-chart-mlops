import os
import psycopg2
import polars as pl

DATABASE_URL = os.getenv("DATABASE_URL_CONNECTION")


def preprocessing():
    con = psycopg2.connect(DATABASE_URL)
    cur = con.cursor()

    # load cleaned data
    cur.execute("SELECT COUNT(*) FROM spotify_charts_cleaned")
    print(f"    Cleaned Data: {cur.fetchone()[0]:,} rows")

    df = pl.read_database_uri(
        "SELECT * FROM spotify_charts_cleaned WHERE chart = 'top200'", uri=DATABASE_URL
    )
    print(f"    Loaded top200 Data: {df.height:,} rows")

    # Features
    df = df.sort(["title", "artist", "region", "date"])

    df = df.with_columns(
        [
            pl.col("rank")
            .shift(1)
            .over(["title", "artist", "region"])
            .alias("prev_rank"),
            pl.col("streams")
            .shift(1)
            .over(["title", "artist", "region"])
            .alias("prev_streams"),
            (
                pl.col("streams")
                - pl.col("streams")
                .shift(1)
                .over(["title", "artist", "region"])
                .alias("streams_change")
            ),
        ]
    )

    before = df.height
    df = df.drop_nulls(subset=["prev_rank", "prev_streams"])
    print(
        f"    Before: {before:,} -> After: {df.height:,} (dropped {before - df.height:,})"
    )

    # Outliers (IQR)
    Q1 = df["streams"].quantile(0.25)
    Q3 = df["streams"].quantile(0.75)
    IQR = Q3 = Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    before = df.height
    df = df.filter(pl.col("streams") >= lower) & (pl.col("streams") <= upper)
    print(
        f"    Before: {before:,} -> After: {df.height:,} (dropped {before - df.height:,} Outliers)"
    )
