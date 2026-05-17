-- =============================================
-- Project: PulseCheck MS
-- Description: Healthcare Resilience Database Schema
-- Created for: Data Analytics & Healthcare Resilience Hackathon (2026)
-- Author: Md Nurul Amin
-- =============================================

-- 1. Create Database (Optional - depends on environment)
-- CREATE DATABASE pulsecheck_db;

-- 2. Drop existing tables to ensure a clean setup (Careful: this deletes existing data)
DROP TABLE IF EXISTS Disaster_History CASCADE;
DROP TABLE IF EXISTS Hospital_Registry CASCADE;
DROP TABLE IF EXISTS County_SVI_Metrics CASCADE;
DROP TABLE IF EXISTS Postal_Registry CASCADE;

-- 3. Postal Registry Table (The Geographic Glue)
CREATE TABLE Postal_Registry (
    zip_code VARCHAR(10) PRIMARY KEY,
    city VARCHAR(100),
    state_id VARCHAR(5) DEFAULT 'MS',
    county_name VARCHAR(100) NOT NULL
);

-- 4. County SVI Metrics Table (Social Vulnerability Index)
CREATE TABLE County_SVI_Metrics (
    fips_code VARCHAR(10) PRIMARY KEY,
    county_name VARCHAR(100) NOT NULL,
    svi_score DECIMAL(5, 4), -- Range: 0.0000 to 1.0000
    population INT,
    vulnerability_rank VARCHAR(20) -- e.g., 'High', 'Moderate', 'Low'
);

-- 5. Hospital Registry Table (Healthcare Infrastructure)
CREATE TABLE Hospital_Registry (
    hospital_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(255) NOT NULL,
    fips_code VARCHAR(10) REFERENCES County_SVI_Metrics(fips_code),
    zip_code VARCHAR(10) REFERENCES Postal_Registry(zip_code),
    bed_capacity INT DEFAULT 0,
    current_occupancy_rate DECIMAL(5, 2), -- Percentage
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    facility_type VARCHAR(100), -- e.g., 'Critical Access', 'Acute Care'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Disaster History Table (Historical Loss & Impact)
CREATE TABLE Disaster_History (
    event_id SERIAL PRIMARY KEY,
    fips_code VARCHAR(10) REFERENCES County_SVI_Metrics(fips_code),
    disaster_type VARCHAR(100), -- e.g., 'Hurricane', 'Tornado', 'Flood'
    year INT,
    financial_loss_usd DECIMAL(15, 2),
    unserved_patients_estimate INT,
    impact_score DECIMAL(5, 2)
);

-- 7. Optimized Indexes for Faster API Response (Sub-second Latency)
CREATE INDEX idx_hospital_fips ON Hospital_Registry(fips_code);
CREATE INDEX idx_disaster_fips ON Disaster_History(fips_code);
CREATE INDEX idx_zip_code ON Postal_Registry(zip_code);

-- 8. Sample Query for Testing Relational Joins
-- SELECT h.hospital_name, c.county_name, c.svi_score, h.bed_capacity 
-- FROM Hospital_Registry h
-- JOIN County_SVI_Metrics c ON h.fips_code = c.fips_code
-- WHERE c.svi_score > 0.85;

-- =============================================
-- SECTION 9: API BACKEND QUERIES
-- =============================================

-- 1. Statewide Map Data API Query
-- Fetches core metrics for GIS visualization
SELECT 
    fips_code, 
    county_name, 
    svi_score, 
    population, 
    vulnerability_rank 
FROM County_SVI_Metrics;


-- 2. County Insights API Query (Relational Join)
-- Aggregates socioeconomic and disaster data for specific county drill-down
SELECT 
    c.county_name, 
    c.svi_score, 
    c.population,
    SUM(d.financial_loss_usd) as total_economic_loss,
    AVG(d.impact_score) as avg_disaster_impact
FROM County_SVI_Metrics c
LEFT JOIN Disaster_History d ON c.fips_code = d.fips_code
WHERE c.fips_code = %s -- Dynamic FIPS Code input
GROUP BY c.fips_code, c.county_name, c.svi_score, c.population;


-- 3. Proactive Hospital Alerts API Query
-- Identifies hospitals at critical capacity in high-risk zones
SELECT 
    h.hospital_name, 
    h.bed_capacity, 
    h.current_occupancy_rate, 
    c.county_name
FROM Hospital_Registry h
JOIN County_SVI_Metrics c ON h.fips_code = c.fips_code
WHERE h.current_occupancy_rate >= 90 
  AND c.svi_score > 0.70
ORDER BY h.current_occupancy_rate DESC;

-- =============================================
-- End of Script
-- =============================================