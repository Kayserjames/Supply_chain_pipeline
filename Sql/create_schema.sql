-- 1. Création des schémas isolés pour notre architecture
CREATE SCHEMA IF NOT EXISTS raw;       -- Zone Staging (fichiers bruts)
CREATE SCHEMA IF NOT EXISTS analytics; -- Zone Core (données nettoyées et modélisées)
CREATE SCHEMA IF NOT EXISTS marts;     -- Zone Reporting (vues et agrégats pour KPI)