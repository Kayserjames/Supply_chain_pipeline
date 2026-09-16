-- Zone Staging : Réception brute des données sans contraintes fortes

CREATE TABLE IF NOT EXISTS raw.stg_suppliers (
    supplier_id VARCHAR(100),
    supplier_name VARCHAR(200),
    country VARCHAR(100),
    lead_time_days VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.stg_warehouses (
    warehouse_id VARCHAR(100),
    warehouse_name VARCHAR(200),
    city VARCHAR(100),
    capacity_m3 VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.stg_stores (
    store_id VARCHAR(100),
    store_name VARCHAR(200),
    city VARCHAR(100),
    region VARCHAR(100),
    store_size_m2 VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.stg_products (
    product_id VARCHAR(100),
    product_name VARCHAR(200),
    category VARCHAR(100),
    standard_cost VARCHAR(50),
    suggested_retail_price VARCHAR(50),
    reorder_point VARCHAR(50),
    supplier_id VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.stg_supplier_receipts (
    receipt_id VARCHAR(100),
    supplier_id VARCHAR(100),
    warehouse_id VARCHAR(100),
    product_id VARCHAR(100),
    quantity_received VARCHAR(50),
    unit_purchase_cost VARCHAR(50),
    receipt_timestamp VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.stg_warehouse_transfers (
    transfer_id VARCHAR(100),
    source_warehouse_id VARCHAR(100),
    destination_store_id VARCHAR(100),
    product_id VARCHAR(100),
    quantity_transferred VARCHAR(50),
    unit_transfer_price VARCHAR(50),
    transfer_timestamp VARCHAR(100),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);