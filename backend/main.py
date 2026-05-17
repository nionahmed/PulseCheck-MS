from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI(title="Mississippi Health Interactive GIS API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Interactive Health GIS API!"}

@app.get("/api/v1/map-data")
def get_map_data(db: Session = Depends(get_db)):
    query = text("""
        SELECT fips_code, county_name, overall_svi_score as vulnerability_score, total_population
        FROM svi_metrics
        WHERE overall_svi_score IS NOT NULL
        ORDER BY county_name;
    """)
    result = db.execute(query).mappings().all()
    return [dict(row) for row in result]

@app.get("/api/v1/county-details/{county_name}")
def get_county_details(county_name: str, db: Session = Depends(get_db)):
    summary_query = text("""
        SELECT 
            COUNT(CASE WHEN h.is_active = TRUE THEN 1 END) as active_hospitals,
            COALESCE(SUM(h.bed_capacity), 0) as total_beds,
            COALESCE(SUM(h.occupied_beds), 0) as occupied_beds,
            COALESCE(SUM(h.bed_capacity - h.occupied_beds), 0) as available_beds
        FROM hospitals h
        JOIN svi_metrics s ON h.fips_code = s.fips_code
        WHERE s.county_name = :county_name;
    """)
    summary_result = db.execute(summary_query, {"county_name": county_name}).mappings().first()
    
    svi_query = text("SELECT overall_svi_score FROM svi_metrics WHERE county_name = :county_name;")
    svi_result = db.execute(svi_query, {"county_name": county_name}).scalar()

    hospitals_query = text("""
        SELECT 
            h.hospital_name, h.address, h.latitude, h.longitude, 
            h.bed_capacity as total_beds, h.occupied_beds,
            (h.bed_capacity - h.occupied_beds) as empty_beds
        FROM hospitals h
        JOIN svi_metrics s ON h.fips_code = s.fips_code
        WHERE s.county_name = :county_name AND h.is_active = TRUE;
    """)
    hospitals_result = db.execute(hospitals_query, {"county_name": county_name}).mappings().all()
    
    history_query = text("""
        SELECT cdh.disaster_type, cdh.disaster_year, cdh.financial_loss_usd, 
               cdh.unserved_patients, cdh.hospitals_damaged
        FROM county_disaster_history cdh
        JOIN svi_metrics s ON cdh.fips_code = s.fips_code
        WHERE s.county_name = :county_name
        ORDER BY cdh.disaster_year DESC;
    """)
    history_result = db.execute(history_query, {"county_name": county_name}).mappings().all()
    
    return {
        "vulnerability_score": svi_result if svi_result else 0.0,
        "summary": dict(summary_result) if summary_result else {"active_hospitals": 0, "total_beds": 0, "occupied_beds": 0, "available_beds": 0},
        "hospitals": [dict(row) for row in hospitals_result],
        "history": [dict(row) for row in history_result]
    }