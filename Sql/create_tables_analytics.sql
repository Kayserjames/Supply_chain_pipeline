-- ============================================================
-- 1. TABLES DE DIMENSIONS (Référentiels)
-- ============================================================

-- Fournisseurs
CREATE TABLE IF NOT EXISTS analytics.dim_supplier (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    lead_time_days INT
);

-- Entrepôts
CREATE TABLE IF NOT EXISTS analytics.dim_warehouse (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    capacity_m3 INT
);

-- Magasins
CREATE TABLE IF NOT EXISTS analytics.dim_store (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    region VARCHAR(50),
    store_size_m2 INT
);

-- Produits (Contient uniquement les prix de référence/catalogue actuels)
CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    standard_cost NUMERIC(10, 2), -- Coût indicatif moyen
    suggested_retail_price NUMERIC(10, 2), -- Prix de revente conseillé
    reorder_point INT NOT NULL,
    supplier_id VARCHAR(50) REFERENCES analytics.dim_supplier(supplier_id)
);


-- ============================================================
-- 2. TABLES DE FAITS (Événements & Flux séparés)
-- ============================================================

-- A. FLUX 1 : Approvisionnement (Fournisseur -> Entrepôt)
CREATE TABLE IF NOT EXISTS analytics.fact_supplier_receipt (
    receipt_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_supplier(supplier_id),
    warehouse_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_warehouse(warehouse_id),
    product_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_product(product_id),
    
    quantity_received INT NOT NULL CHECK (quantity_received > 0),
    unit_purchase_cost NUMERIC(10, 2) NOT NULL, -- Prix d'acquisition REEL à la date de réception
    total_purchase_amount NUMERIC(12, 2) GENERATED ALWAYS AS (quantity_received * unit_purchase_cost) STORED,
    
    receipt_timestamp TIMESTAMP NOT NULL,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- B. FLUX 2 : Redistribution (Entrepôt -> Magasin)
CREATE TABLE IF NOT EXISTS analytics.fact_warehouse_transfer (
    transfer_id VARCHAR(50) PRIMARY KEY,
    source_warehouse_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_warehouse(warehouse_id),
    destination_store_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_store(store_id),
    product_id VARCHAR(50) NOT NULL REFERENCES analytics.dim_product(product_id),
    
    quantity_transferred INT NOT NULL CHECK (quantity_transferred > 0),
    unit_transfer_price NUMERIC(10, 2) NOT NULL, -- Prix attribué lors de la revente/transfert au magasin
    total_transfer_amount NUMERIC(12, 2) GENERATED ALWAYS AS (quantity_transferred * unit_transfer_price) STORED,
    
    transfer_timestamp TIMESTAMP NOT NULL,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);