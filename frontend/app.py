import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from geopy.distance import geodesic

st.set_page_config(page_title="MS Health GIS Dashboard", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
DEFAULT_USER_LOCATION = (31.3271, -89.2903) 

@st.cache_data(ttl=60)
def fetch_map_data():
    response = requests.get(f"{API_BASE_URL}/map-data")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_county_details(county_name):
    response = requests.get(f"{API_BASE_URL}/county-details/{county_name}")
    if response.status_code == 200:
        return response.json()
    return None

st.title("PulseCheck MS: Health Infrastructure & Vulnerability Dashboard")
st.markdown("---")

map_df = fetch_map_data()

if not map_df.empty:
    st.subheader("Statewide County Vulnerability Map")
    
    from urllib.request import urlopen
    import json
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties_geojson = json.load(response)

    fig = px.choropleth(
        map_df, geojson=counties_geojson, locations='fips_code', color='vulnerability_score',
        color_continuous_scale="RdYlGn_r",
        scope="usa",
        hover_name='county_name',
        hover_data={'fips_code': False, 'vulnerability_score': True, 'total_population': True},
        labels={'vulnerability_score': 'SVI Score'}
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Drill Down: County Specific Analytics")
    
    county_list = map_df['county_name'].sort_values().tolist()
    selected_county = st.selectbox("Select a County to view detailed infrastructure & history:", county_list)

    if selected_county:
        details = fetch_county_details(selected_county)
        
        if details:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("##### SVI Vulnerability Gauge")
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=details['vulnerability_score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 1]},
                        'bar': {'color': "darkred"},
                        'steps': [
                            {'range': [0, 0.4], 'color': "lightgreen"},
                            {'range': [0.4, 0.7], 'color': "gold"},
                            {'range': [0.7, 1.0], 'color': "salmon"}
                        ]
                    }
                ))
                gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(gauge, use_container_width=True)
            
            with col2:
                st.markdown("##### Healthcare Capacity Summary")
                summary = details['summary']
                scol1, scol2, scol3, scol4 = st.columns(4)
                scol1.metric("Active Hospitals", summary['active_hospitals'])
                scol2.metric("Total Beds", summary['total_beds'])
                scol3.metric("Occupied Beds", summary['occupied_beds'])
                scol4.metric("Empty Beds", summary['available_beds'])

            st.markdown("### Active Hospitals List")
            hospitals = details.get('hospitals', [])
            if hospitals:
                hosp_df = pd.DataFrame(hospitals)
                
                def calculate_distance(row):
                    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
                        hosp_loc = (row['latitude'], row['longitude'])
                        return round(geodesic(DEFAULT_USER_LOCATION, hosp_loc).miles, 2)
                    return None

                hosp_df['Distance (Miles)'] = hosp_df.apply(calculate_distance, axis=1)
                
                display_cols = ['hospital_name', 'address', 'Distance (Miles)', 'total_beds', 'occupied_beds', 'empty_beds']
                hosp_df = hosp_df[display_cols].sort_values(by='Distance (Miles)')
                st.dataframe(hosp_df, use_container_width=True, hide_index=True)
            else:
                st.info("No active hospitals found in this county.")

            st.markdown("### Historical Disaster Impact")
            history = details.get('history', [])
            if history:
                hist_df = pd.DataFrame(history)
                hist_df['financial_loss_usd'] = hist_df['financial_loss_usd'].apply(lambda x: f"${x:,.2f}")
                hist_df.rename(columns={
                    'disaster_type': 'Disaster Type',
                    'disaster_year': 'Year',
                    'financial_loss_usd': 'Financial Loss (USD)',
                    'unserved_patients': 'Unserved Patients',
                    'hospitals_damaged': 'Hospitals Damaged'
                }, inplace=True)
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
            else:
                st.info("No disaster history found for this county.")