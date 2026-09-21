import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
 

url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    database=os.environ["DB_NAME"])

engine = create_engine(url)


""" Fontion de chargement des dimensions de la zone staging a la zone analytics  """

def transform_and_load_dimensions(connection):
    logger.info("__Transformations et chargements des dimensions__")

#-----------------------------------------------------------------------------------------------
#                        Dimension warehouse
#------------------------------------------------------------------------------------------------

    query= """INSERT INTO analytics.dim_warehouse (warehouse_id,warehouse_name,city,capacity_m3)
              SELECT DISTINCT warehouse_id,warehouse_name,city,capacity_m3::INT
              FROM raw.stg_warehouses
              WHERE warehouse_id is NOT NULL
              ON CONFLICT (warehouse_id) DO UPDATE SET
              warehouse_name= EXCLUDED.warehouse_name,
              city= EXCLUDED.city,
              capacity_m3= EXCLUDED.capacity_m3;"""

    connection.execute(text(query))

    logger.info("  ✔ Table `analytics.dim_warehouse` mise à jour.")

#--------------------------------------------------------------------------------
#            Dimension supplier
#--------------------------------------------------------------------------------
    query= """INSERT INTO analytics.dim_supplier (supplier_id,supplier_name,country,lead_time_days)
              SELECT DISTINCT supplier_id,supplier_name,country,lead_time_days::INT
              FROM raw.stg_suppliers
              WHERE supplier_id is NOT NULL
              ON CONFLICT (supplier_id) DO UPDATE SET 
              supplier_name= EXCLUDED.supplier_name,
              country= EXCLUDED.country,
              lead_time_days= EXCLUDED.lead_time_days;"""

    connection.execute(text(query))

    logger.info("  ✔ Table `analytics.dim_supplier` mise à jour.")

#-----------------------------------------------------------------------------------------
#                      Dimension produits
#-----------------------------------------------------------------------------------------

    query= """INSERT INTO analytics.dim_product (product_id,product_name,category,standard_cost,
                                                suggested_retail_price,reorder_point,supplier_id)
              SELECT DISTINCT pd.product_id,
                              pd.product_name,
                              pd.category,
                              pd.standard_cost::NUMERIC,
                              pd.suggested_retail_price::NUMERIC,
                              pd.reorder_point::INT,
                              pd.supplier_id
              FROM raw.stg_products pd
              JOIN analytics.dim_supplier s ON pd.supplier_id=s.supplier_id
              WHERE pd.product_id is NOT NULL 
                 ON CONFLICT (product_id) DO UPDATE SET 
                 product_name = EXCLUDED.product_name,
                 category = EXCLUDED.category,
                 standard_cost = EXCLUDED.standard_cost,
                 suggested_retail_price = EXCLUDED.suggested_retail_price,
                 reorder_point = EXCLUDED.reorder_point,
                 supplier_id = EXCLUDED.supplier_id; """

    connection.execute(text(query))

    logger.info("  ✔ Table `analytics.dim_product` mise à jour.")


#-------------------------------------------------------------------
#                     Dimension store
#---------------------------------------------------------------------

    query= """INSERT INTO analytics.dim_store (store_id,store_name,city,region,store_size_m2)
              SELECT DISTINCT store_id,store_name,city,region,store_size_m2::INT
              FROM raw.stg_stores 
              WHERE store_id is NOT NULL
                ON CONFLICT (store_id) DO UPDATE SET 
                store_name = EXCLUDED.store_name,
                city = EXCLUDED.city,
                region = EXCLUDED.region,
                store_size_m2 = EXCLUDED.store_size_m2;"""

    connection.execute(text(query))

    logger.info("  ✔ Table `analytics.dim_store` mise à jour.")




    """ Fonction de chargements des faits de la zone staging a la zone analytics"""
def transform_and_load_facts(connection):
    logger.info("__2. Transformation et chargements des faits__")

#-------------------------------------------------------------------------------------------------
#                              supplier_receipts
#---------------------------------------------------------------------------------------------------

    query= """INSERT INTO analytics.fact_supplier_receipt (receipt_id,supplier_id,warehouse_id,product_id,
                                    quantity_received,unit_purchase_cost,receipt_timestamp)
              SELECT DISTINCT sr.receipt_id,
                              sr.supplier_id,
                              sr.warehouse_id,
                              sr.product_id,
                              sr.quantity_received::INT,
                              sr.unit_purchase_cost::NUMERIC,                              
                              sr.receipt_timestamp::TIMESTAMP
              FROM raw.stg_supplier_receipts sr
              JOIN analytics.dim_supplier s ON sr.supplier_id = s.supplier_id
              JOIN analytics.dim_warehouse w ON sr.warehouse_id = w.warehouse_id
              JOIN analytics.dim_product p ON sr.product_id = p.product_id
              WHERE sr.receipt_id is NOT NULL
                ON CONFLICT (receipt_id) DO NOTHING; """

    connection.execute(text(query))

    logger.info(f"  ✔ Table `analytics.fact_supplier_receipt` chargée.")

#-------------------------------------------------------------------------------------------------
#                                   warehouse_transfer
#-------------------------------------------------------------------------------------------------

    query= """INSERT INTO analytics.fact_warehouse_transfer (transfer_id, source_warehouse_id, destination_store_id, product_id, quantity_transferred, unit_transfer_price, transfer_timestamp)
        SELECT DISTINCT
            stg.transfer_id,
            stg.source_warehouse_id,
            stg.destination_store_id,
            stg.product_id,
            stg.quantity_transferred::INT,
            stg.unit_transfer_price::NUMERIC,
            stg.transfer_timestamp::TIMESTAMP
        FROM raw.stg_warehouse_transfers stg
        INNER JOIN analytics.dim_warehouse w ON stg.source_warehouse_id = w.warehouse_id
        INNER JOIN analytics.dim_store s ON stg.destination_store_id = s.store_id
        INNER JOIN analytics.dim_product p ON stg.product_id = p.product_id
        WHERE stg.transfer_id IS NOT NULL
        ON CONFLICT (transfer_id) DO NOTHING;"""

    connection.execute(text(query))

    logger.info(f"  ✔ Table `analytics.fact_warehouse_transfer` chargée.")



def Run_pipeline():
    try:
      with engine.begin() as connection:
         transform_and_load_dimensions(connection)
         transform_and_load_facts(connection)
         logger.info("\n🎉 Transformation et chargement en zone `analytics` réussis avec succès !")
    except Exception as e:
         logger.error(f"❌ Échec du pipeline : {e}")
         raise
    finally:
        engine.dispose()
 
 
if __name__ == "__main__":
    Run_pipeline()