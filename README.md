# 🏥 PulseCheck MS
**Automated GIS & Vulnerability Radar for Healthcare Disaster Readiness in Mississippi**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0+-336791.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📌 Overview
**PulseCheck MS** is an automated Geographic Information System (GIS) and data pipeline designed to bridge critical gaps in Mississippi's healthcare infrastructure. By integrating fragmented data from federal portals (CDC, CMS, FEMA), we provide a unified, real-time command center for state officials, dispatchers, and citizens to proactively mitigate risks and optimize healthcare access during severe weather events.

## ⚠️ The Problem
Mississippi's healthcare response faces a triple threat during emergencies:
1. **Fragmented Data:** Crucial information is trapped in isolated silos across various federal and state portals.
2. **Lack of Real-Time Visibility:** Dispatchers lack immediate insight into hospital bed capacities and exact distances during high-stakes disaster routing.
3. **Reactive Interventions:** Response efforts traditionally focus on post-disaster damage rather than identifying and protecting highly vulnerable (SVI) zones beforehand.

## 💡 Our Solution
We transition emergency healthcare from a *reactive* response to a *proactive* resilience model. **PulseCheck MS** automatically parses, normalizes, and visualizes multi-agency data into a sub-second latency dashboard. 

### Key Features
* 🗺️ **Dynamic GIS Choropleth Mapping:** Statewide visualization color-coded by the CDC's Social Vulnerability Index (SVI).
* 🏥 **Real-Time Resource Visibility:** Live hospital bed tracking and capacity monitoring.
* 📍 **Precision Proximity Routing:** Geodesic distance calculation (using Geopy) to instantly route patients to the nearest available facility.
* 📊 **County Drill-Down:** Deep-dive analytics into local disaster history, financial loss, and healthcare infrastructure stress levels.
* ⚙️ **Unattended Automation:** 100% automated ETL pipeline ensuring data accuracy without manual intervention.

## 🏗️ Technical Architecture

### 1. The ETL Pipeline (Data Engineering)
* **Extraction:** Automated parsing of raw CSV datasets from CDC (SVI), CMS (POS), and FEMA.
* **Normalization:** Standardizing **GEOID** and **FIPS** codes for absolute relational integrity.
* **Enhancement:** Grouping data by State/County and calculating real-time disaster metrics.
* **Validation:** Ensuring missing metadata is resolved before production deployment.

### 2. Robust Data Storage (PostgreSQL & pgAdmin 4)
We utilize a high-performance **PostgreSQL** engine, managed via **pgAdmin 4**, adhering to a strict 3rd Normal Form (3NF) schema to eliminate redundancy.

**Core Data Entities:**
| Entity | Key Identifiers | Description |
| :--- | :--- | :--- |
| **County SVI Metrics** | `FIPS Code` | Socioeconomic vulnerability baseline per county. |
| **Hospital Registry** | `Hospital ID` | Live facility data, capacity, and GPS coordinates. |
| **Disaster History** | `Event ID` | Historical financial loss and patient impact data. |
| **Postal Registry** | `ZIP Code` | The geographic "glue" joining tables across the state. |

### 3. Dual-Core API (FastAPI)
* **Statewide Map API:** Delivers FIPS, SVI scores, and populations for rapid GIS rendering.
* **County Drill-Down API:** Executes complex, multi-table relational joins to deliver aggregated facility and disaster stats in **< 0.5 seconds**.

## 🚀 Local Installation & Setup

Follow these steps to run PulseCheck MS on your local machine:

### Prerequisites
* Python 3.10+
* PostgreSQL & pgAdmin 4
* Git

### Step 1: Clone the Repository
```bash
git clone [https://github.com/nionahmed/PulseCheck-MS.git](https://github.com/nionahmed/PulseCheck-MS.git)
cd PulseCheck-MS

### Step 2: Set Up Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate

**Install Dependencies**
```bash
pip install -r requirements.txt

**Run the Backend**
```bash
uvicorn main:app --reload

**Run the Frontend**
```bash
streamlit run app.py
