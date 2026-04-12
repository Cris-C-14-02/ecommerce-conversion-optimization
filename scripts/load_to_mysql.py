import pandas as pd
from sqlalchemy import create_engine

# 👉 改这里（你的 MySQL 信息）
USERNAME = "REMOVED_USER"
PASSWORD = "REMOVED_SECRET"
HOST = "localhost"
PORT = "3306"
DATABASE = "ecommerce"

# 👉 CSV 路径
CSV_PATH = "data/raw/events.csv"

def main():
    print("Reading CSV...")
    df = pd.read_csv(CSV_PATH)

    print("Data preview:")
    print(df.head())
    print(f"Total rows: {len(df)}")

    # 建立数据库连接
    engine = create_engine(
        f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    )

    print("Uploading to MySQL...")

    # 分批写入，避免卡死
    df.to_sql(
        name="events_raw",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000
    )

    print("Upload completed!")

if __name__ == "__main__":
    main()