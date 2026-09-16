import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "C:/Users/USER/OneDrive/Documents/Data engineering/Projets/supply_chain pipeline/data/raw")

load_dotenv()
url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    database=os.environ["DB_NAME"])

engine = create_engine(url)


def load_csv_to_staging(file_name, table_name):
    file_path = os.path.join(RAW_DATA_DIR,file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE raw.{table_name}"))

        df.to_sql(table_name, con= engine, schema= "raw", if_exists= "append", index= False )
        print(f"✔ [Staging] {len(df)} lignes chargées dans raw.{table_name}")


def load_supplier_receipts_to_staging(date_str):
    file_name= f"supplier_receipts_{date_str}.json"
    file_path = os.path.join(RAW_DATA_DIR,file_name)
    if os.path.exists(file_path):
        df = pd.read_json(file_path, orient= "columns")

        df.to_sql("stg_supplier_receipts", con=engine, schema="raw", if_exists="replace", index=False)
        print(f"✔ [Staging] {len(df)} réceptions fournisseurs chargées pour le {date_str}")


def load_warehouse_transfers_to_staging(date_str):
    file_name= f"warehouse_transfers_{date_str}.csv"
    file_path= os.path.join(RAW_DATA_DIR,file_name)
    if os.path.exists(file_path):
        df= pd.read_csv(file_path)

        df.to_sql("stg_warehouse_transfers", con=engine, schema="raw", if_exists="replace", index=False)
        print(f"✔ [Staging] {len(df)} transferts de stock chargés pour le {date_str}")



if __name__ == "__main__":

    today_str = datetime.now().strftime("%Y-%m-%d")

    print("--- Début de l'ingestion Staging (Zone RAW) ---")
    # 1. Chargement des dimensions
    load_csv_to_staging("suppliers.csv", "stg_suppliers")
    load_csv_to_staging("warehouses.csv", "stg_warehouses")
    load_csv_to_staging("stores.csv", "stg_stores")
    load_csv_to_staging("products.csv", "stg_products")
    
    # 2. Chargement des faits quotidiens
    load_supplier_receipts_to_staging(today_str)
    load_warehouse_transfers_to_staging(today_str)
    print("--- Ingestion Staging terminée ---")