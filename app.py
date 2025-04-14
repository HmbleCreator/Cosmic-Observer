# app.py
from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

app = Flask(__name__)

# Configuration
NASA_API_KEY = "ZcBhaRmT0MvXU3lkbjrfbnHVtlHePa0gB3Csvl4X"  # Replace with your NASA API key for production use
EXOPLANET_API_BASE = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
SPACE_WEATHER_API = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SOLAR_WIND_API = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
KP_INDEX_API = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
SUNSPOT_API = "https://www.sidc.be/silso/DATA/snmtotcsv.php"

# Routes
@app.route('/')
def home():
    """Render the homepage with navigation to all features"""
    return render_template('index.html')

@app.route('/space-weather')
def space_weather():
    """Space Weather Dashboard"""
    # Initialize variables with default values
    solar_wind_speed = 'N/A'
    latest_kp = 'N/A'
    latest_sunspot = 'N/A'
    solar_wind_graph = None
    kp_graph = None
    
    try:
        # Solar wind speed
        try:
            solar_wind_response = requests.get(SOLAR_WIND_API)
            if solar_wind_response.status_code == 200:
                solar_wind_data = solar_wind_response.json()
                solar_wind_speed = solar_wind_data.get('WindSpeed', 'N/A')
        except Exception as e:
            print(f"Error fetching solar wind data: {str(e)}")
        
        # KP index
        try:
            kp_response = requests.get(KP_INDEX_API)
            if kp_response.status_code == 200:
                kp_data = kp_response.json()
                # Extract the latest KP index value
                latest_kp = kp_data[-1][1] if len(kp_data) > 1 else 'N/A'
        except Exception as e:
            print(f"Error fetching KP index data: {str(e)}")
        
        # Generate simulated sunspot data since the API is not available
        latest_sunspot = str(int(np.random.normal(50, 20)))  # Random sunspot number centered around 50
        
        # Create historical graphs
        # Sample data for demonstration
        dates = pd.date_range(end=datetime.now(), periods=30).tolist()
        solar_wind_hist = np.random.normal(450, 50, 30).tolist()  # Simulated solar wind data
        kp_hist = np.random.uniform(0, 9, 30).tolist()  # Simulated KP index data
        
        # Create solar wind graph
        solar_wind_fig = px.line(
            x=dates, 
            y=solar_wind_hist,
            labels={"x": "Date", "y": "Solar Wind Speed (km/s)"},
            title="Solar Wind Speed - Last 30 Days"
        )
        solar_wind_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.1)",
            font=dict(color="white")
        )
        
        # Create KP index graph
        kp_fig = px.line(
            x=dates, 
            y=kp_hist,
            labels={"x": "Date", "y": "KP Index"},
            title="Geomagnetic Activity (KP Index) - Last 30 Days"
        )
        kp_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0.1)",
            font=dict(color="white")
        )
        
        # Convert to JSON for embedding in HTML
        solar_wind_graph = json.dumps(solar_wind_fig, cls=plotly.utils.PlotlyJSONEncoder)
        kp_graph = json.dumps(kp_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template(
            'space_weather.html',
            solar_wind_speed=solar_wind_speed,
            kp_index=latest_kp,
            sunspot_count=latest_sunspot,
            solar_wind_graph=solar_wind_graph,
            kp_graph=kp_graph
        )
    
    except Exception as e:
        print(f"Error in space_weather route: {str(e)}")
        return render_template('error.html', error=str(e))
    

@app.route('/aurora-alerts', methods=['GET', 'POST'])
def aurora_alerts():
    """Aurora Visibility Alerts based on user location"""
    user_lat = None
    user_lon = None
    location_name = None
    aurora_visibility = None
    aurora_map = None
    
    if request.method == 'POST':
        try:
            # Get user location input
            location_input = request.form.get('location', '')
            
            # Use geocoding to get coordinates
            geolocator = Nominatim(user_agent="cosmic_observer")
            location = geolocator.geocode(location_input)
            
            if location:
                user_lat = location.latitude
                user_lon = location.longitude
                location_name = location.address
                
                # Get KP index
                kp_response = requests.get(KP_INDEX_API)
                kp_data = kp_response.json()
                latest_kp = float(kp_data[-1][1]) if len(kp_data) > 1 else 0
                
                # Calculate aurora visibility probability based on KP index and latitude
                # This is a simplified model; a more sophisticated model would be used in production
                # Generally, auroras are visible at lower latitudes when KP index is higher
                
                # Minimum latitude where aurora might be visible for given KP
                min_latitude = 65 - (5 * latest_kp)
                
                # Calculate probability based on distance from ideal latitude
                abs_lat = abs(user_lat)  # Use absolute latitude value
                if abs_lat >= min_latitude:
                    # Higher probability closer to poles
                    aurora_visibility = min(100, max(0, (abs_lat - min_latitude + latest_kp * 2) * 10))
                else:
                    aurora_visibility = 0
                
                # Create a world map showing aurora oval
                # This is a simplified visualization
                lats = []
                lons = []
                probs = []
                
                # Generate points around the north and south poles with probability based on KP
                for lat in range(-90, 91, 2):
                    for lon in range(-180, 181, 10):
                        abs_lat_point = abs(lat)
                        if abs_lat_point >= min_latitude:
                            prob = min(100, max(0, (abs_lat_point - min_latitude + latest_kp * 2) * 10))
                            if prob > 10:  # Only show points with some probability
                                lats.append(lat)
                                lons.append(lon)
                                probs.append(prob)
                
                # Create the map
                fig = px.scatter_geo(
                    lat=lats,
                    lon=lons,
                    color=probs,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    projection="natural earth",
                    title=f"Current Aurora Visibility (KP Index: {latest_kp})",
                    labels={"color": "Probability (%)"},
                )
                
                # Add the user's location
                fig.add_trace(go.Scattergeo(
                    lat=[user_lat],
                    lon=[user_lon],
                    mode="markers",
                    marker=dict(size=10, color="red", symbol="star"),
                    name="Your Location"
                ))
                
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0.1)",
                    geo=dict(
                        showland=True,
                        landcolor="rgb(30, 30, 30)",
                        countrycolor="rgb(70, 70, 70)",
                        coastlinecolor="rgb(70, 70, 70)",
                        showocean=True,
                        oceancolor="rgb(10, 10, 30)",
                        showlakes=False,
                        showcountries=True,
                    ),
                    font=dict(color="white")
                )
                
                aurora_map = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        except GeocoderTimedOut:
            return render_template('aurora_alerts.html', error="Geocoding service timed out. Please try again.")
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return render_template(
        'aurora_alerts.html',
        location_name=location_name,
        aurora_visibility=aurora_visibility,
        aurora_map=aurora_map
    )

@app.route('/exoplanet-explorer', methods=['GET', 'POST'])
def exoplanet_explorer():
    """Exoplanet Explorer with search and visualization"""
    exoplanet_data = None
    exoplanet_chart = None
    
    try:
        # For demonstration purposes, we'll use a sample dataset
        # In production, this would fetch from the NASA Exoplanet Archive API
        
        if request.method == 'POST':
            # Get filter parameters
            star_type = request.form.get('star_type', '')
            min_mass = float(request.form.get('min_mass', 0))
            max_mass = float(request.form.get('max_mass', 100))
            min_distance = float(request.form.get('min_distance', 0))
            max_distance = float(request.form.get('max_distance', 1000))
            min_habitability = float(request.form.get('min_habitability', 0))
            
            # For demonstration, create sample data
            # In production, you'd query the NASA API with these parameters
            
            # Sample exoplanet data
            np.random.seed(42)  # For reproducible results
            num_planets = 100
            
            # Generate sample data
            sample_data = {
                'pl_name': [f"Exoplanet-{i}" for i in range(1, num_planets + 1)],
                'st_spectype': np.random.choice(['G', 'K', 'M', 'F', 'A'], num_planets),
                'pl_masse': np.random.exponential(1, num_planets) * 10,  # Mass in Earth masses
                'st_dist': np.random.uniform(5, 500, num_planets),  # Distance in light years
                'pl_orbper': np.random.uniform(1, 1000, num_planets),  # Orbital period in days
                'pl_rade': np.random.exponential(1, num_planets) * 3,  # Radius in Earth radii
                'pl_eqt': np.random.uniform(100, 800, num_planets)  # Equilibrium temperature in K
            }
            
            # Calculate a simplified habitability score
            # This is just an example - real habitability scores are much more complex
            def calc_habitability(mass, temp):
                # Higher score for Earth-like mass and temperature
                mass_score = max(0, 1 - abs(mass - 1) / 5)  # Closer to 1 Earth mass is better
                temp_score = max(0, 1 - abs(temp - 288) / 200)  # Closer to Earth's 288K is better
                return (mass_score + temp_score) / 2 * 100  # Convert to percentage
            
            habitability_scores = [
                calc_habitability(mass, temp) 
                for mass, temp in zip(sample_data['pl_masse'], sample_data['pl_eqt'])
            ]
            sample_data['habitability_score'] = habitability_scores
            
            # Create a pandas DataFrame
            df = pd.DataFrame(sample_data)
            
            # Apply filters
            if star_type:
                df = df[df['st_spectype'] == star_type]
            df = df[(df['pl_masse'] >= min_mass) & (df['pl_masse'] <= max_mass)]
            df = df[(df['st_dist'] >= min_distance) & (df['st_dist'] <= max_distance)]
            df = df[df['habitability_score'] >= min_habitability]
            
            # Create visualization
            fig = px.scatter(
                df,
                x='st_dist',
                y='pl_masse',
                size='pl_rade',
                color='habitability_score',
                hover_name='pl_name',
                color_continuous_scale=px.colors.sequential.Viridis,
                labels={
                    'st_dist': 'Distance from Earth (light years)',
                    'pl_masse': 'Planet Mass (Earth masses)',
                    'pl_rade': 'Planet Radius (Earth radii)',
                    'habitability_score': 'Habitability Score (%)'
                },
                title='Exoplanet Explorer'
            )
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0.1)",
                plot_bgcolor="rgba(0,0,0,0.2)",
                font=dict(color="white")
            )
            
            exoplanet_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            exoplanet_data = df.to_dict('records')
    
    except Exception as e:
        return render_template('error.html', error=str(e))
    
    # Fix: Change template name to match your file name in the templates folder
    return render_template(
        'exoplanet-explorer.html',  # Make sure this exactly matches your file name
        exoplanet_data=exoplanet_data,
        exoplanet_chart=exoplanet_chart
    )

if __name__ == '__main__':
    app.run(debug=True)