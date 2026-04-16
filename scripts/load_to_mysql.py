import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ecommerce")
BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "events.csv"



def get_engine():
    if not MYSQL_USERNAME or not MYSQL_PASSWORD:
        raise ValueError(
            "MYSQL_USERNAME and MYSQL_PASSWORD must be set as environment variables."
        )

    return create_engine(
        f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )


def main():
    print("Reading CSV...")
    df = pd.read_csv(CSV_PATH)

    print("Data preview:")
    print(df.head())
    print(f"Total rows: {len(df)}")

    engine = get_engine()

    print("Uploading to MySQL...")

    # Write in batches to avoid memory pressure during large uploads.
    df.to_sql(
        name="events_raw",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000,
    )

    print("Upload completed!")


if __name__ == "__main__":
    main()
