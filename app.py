from flask import Flask, render_template, request, jsonify, flash
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
import time
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

# Cache configuration
CACHE_DIR = "cache"
CACHE_TTL = 3600  # Cache lifetime in seconds (1 hour)
EXOPLANET_CACHE_TTL = 24 * 3600  # 24 hours for exoplanet data

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

# Configuration
NASA_API_KEY = "ZcBhaRmT0MvXU3lkbjrfbnHVtlHePa0gB3Csvl4X"  # Replace with your NASA API key for production use
EXOPLANET_API_BASE = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
SPACE_WEATHER_API = "https://services.swpc.noaa.gov/products/noaa-scales.json"
SOLAR_WIND_API = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
KP_INDEX_API = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
SUNSPOT_API = "https://www.sidc.be/silso/DATA/snmtotcsv.php"

# In-memory cache for faster access
memory_cache = {}

def cache_key_from_args(*args, **kwargs):
    """Generate a cache key from function arguments"""
    # Convert args and kwargs to a string and hash it
    key_str = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_str.encode()).hexdigest()

def cached(ttl=CACHE_TTL):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a cache key
            key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            cache_file = os.path.join(CACHE_DIR, key)
            
            # First check memory cache
            if key in memory_cache:
                cache_time, cache_data = memory_cache[key]
                if time.time() - cache_time < ttl:
                    print(f"Memory cache hit for {key}")
                    return cache_data
            
            # Then check file cache
            if os.path.exists(cache_file):
                try:
                    modified_time = os.path.getmtime(cache_file)
                    if time.time() - modified_time < ttl:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                            # Also store in memory for faster access next time
                            memory_cache[key] = (time.time(), cache_data)
                            print(f"File cache hit for {key}")
                            return cache_data
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Cache read error: {str(e)}")
            
            # Cache miss - call original function
            result = func(*args, **kwargs)
            
            # Store in memory cache
            memory_cache[key] = (time.time(), result)
            
            # Store in file cache
            try:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            except IOError as e:
                print(f"Cache write error: {str(e)}")
                
            return result
        return wrapper
    return decorator

def cached_api_request(url, params=None, ttl=CACHE_TTL):
    """Make a cached API request"""
    # Generate a cache key
    key = f"api_request:{hashlib.md5((url + str(sorted(params.items() if params else []))).encode()).hexdigest()}"
    cache_file = os.path.join(CACHE_DIR, key)
    
    # First check memory cache
    if key in memory_cache:
        cache_time, cache_data = memory_cache[key]
        if time.time() - cache_time < ttl:
            print(f"Memory cache hit for API: {url}")
            return cache_data
    
    # Then check file cache
    if os.path.exists(cache_file):
        try:
            modified_time = os.path.getmtime(cache_file)
            if time.time() - modified_time < ttl:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Also store in memory for faster access next time
                    memory_cache[key] = (time.time(), cache_data)
                    print(f"File cache hit for API: {url}")
                    return cache_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Cache read error: {str(e)}")
    
    # Cache miss - make actual API request
    print(f"Cache miss for API: {url}")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        try:
            result = response.json()
            
            # Store in memory cache
            memory_cache[key] = (time.time(), result)
            
            # Store in file cache
            try:
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
            except IOError as e:
                print(f"Cache write error: {str(e)}")
                
            return result
        except json.JSONDecodeError:
            return response.text
    else:
        return None

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
        # Solar wind speed - with caching
        try:
            solar_wind_data = cached_api_request(SOLAR_WIND_API, ttl=1800)  # 30 min TTL
            if solar_wind_data:
                solar_wind_speed = solar_wind_data.get('WindSpeed', 'N/A')
        except Exception as e:
            print(f"Error fetching solar wind data: {str(e)}")
        
        # KP index - with caching
        try:
            kp_data = cached_api_request(KP_INDEX_API, ttl=1800)  # 30 min TTL
            if kp_data:
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
            
            # Use geocoding to get coordinates - with caching
            location = get_geocoded_location(location_input)
            
            if location:
                user_lat = location.latitude
                user_lon = location.longitude
                location_name = location.address
                
                # Get KP index - with caching
                kp_data = cached_api_request(KP_INDEX_API, ttl=1800)  # 30 min TTL
                latest_kp = float(kp_data[-1][1]) if kp_data and len(kp_data) > 1 else 0
                
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
            flash("Geocoding service timed out. Please try again.", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    
    return render_template(
        'aurora_alerts.html',
        location_name=location_name,
        aurora_visibility=aurora_visibility,
        aurora_map=aurora_map
    )

@cached(ttl=86400)  # Cache geocoding results for 24 hours
def get_geocoded_location(location_input):
    """Geocode a location with caching"""
    if not location_input:
        return None
        
    geolocator = Nominatim(user_agent="cosmic_observer")
    return geolocator.geocode(location_input)


@app.route('/exoplanet-explorer', methods=['GET', 'POST'])
def exoplanet_explorer():
    """Exoplanet Explorer with search and visualization using real NASA API data"""
    exoplanet_data = None
    exoplanet_chart = None

    try:
        if request.method == 'POST':
            # Get form inputs (filters)
            star_type = request.form.get('star_type', '')
            min_mass = request.form.get('min_mass', '')
            max_mass = request.form.get('max_mass', '')
            min_distance = request.form.get('min_distance', '')
            max_distance = request.form.get('max_distance', '')
            min_habitability = float(request.form.get('min_habitability', 0))

            # Build query parameters
            query_params = {
                'star_type': star_type,
                'min_planet_mass': min_mass,
                'max_planet_mass': max_mass,
                'min_distance': min_distance,
                'max_distance': max_distance,
                'habitable': 'true' if min_habitability > 0 else 'false'
            }

            # Get exoplanet data using cached function
            exoplanet_results = get_exoplanet_data(query_params)
            
            if exoplanet_results:
                # Convert to DataFrame for further processing
                df = pd.DataFrame(exoplanet_results)
                
                if not df.empty:
                    # Clean and process data
                    df['pl_rade'] = df['pl_rade'].fillna(1)  # Replace NaN radius with 1.0
                    
                    # Filter by habitability score if needed
                    if min_habitability > 0:
                        df = df[df['habitability_score'] >= min_habitability]
                    
                    # Rename columns for better clarity
                    df = df.rename(columns={
                        'pl_bmasse': 'Planet Mass',
                        'pl_rade': 'Planet Radius',
                        'sy_dist': 'Distance',
                        'habitability_score': 'Habitability Score'
                    })
                    
                    # Create the Plotly scatter plot
                    if not df.empty:
                        fig = px.scatter(
                            df,
                            x='Distance',
                            y='Planet Mass',
                            size='Planet Radius',
                            color='Habitability Score',
                            hover_name='pl_name',
                            color_continuous_scale=px.colors.sequential.Viridis,
                            labels={
                                'Distance': 'Distance from Earth (light years)',
                                'Planet Mass': 'Planet Mass (Earth masses)',
                                'Planet Radius': 'Planet Radius (Earth radii)',
                                'Habitability Score': 'Habitability Score (%)'
                            },
                            title='Exoplanet Explorer – Real NASA Data'
                        )
                        
                        fig.update_layout(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0.1)",
                            plot_bgcolor="rgba(0,0,0,0.2)",
                            font=dict(color="white")
                        )
                        
                        exoplanet_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        exoplanet_data = df.to_dict('records')
                    else:
                        flash("No exoplanets found matching your criteria.", "info")
                else:
                    flash("No exoplanets found matching your criteria.", "info")
            else:
                flash("Failed to retrieve data from NASA Exoplanet API.", "danger")

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")

    return render_template(
        'exoplanet-explorer.html',
        exoplanet_data=exoplanet_data,
        exoplanet_chart=exoplanet_chart
    )

@cached(ttl=EXOPLANET_CACHE_TTL)  # Cache exoplanet data for 24 hours
def get_exoplanet_data(query_params):
    """Get exoplanet data from NASA API with caching"""
    # Prepare the ADQL query
    query = "SELECT pl_name, hostname, sy_dist, pl_rade, pl_bmasse, pl_orbper, st_spectype, pl_eqt FROM ps"
    where_clauses = []
    
    if query_params.get('star_type'):
        where_clauses.append(f"st_spectype LIKE '{query_params['star_type']}%'")
    if query_params.get('min_planet_mass'):
        where_clauses.append(f"pl_bmasse >= {query_params['min_planet_mass']}")
    if query_params.get('max_planet_mass'):
        where_clauses.append(f"pl_bmasse <= {query_params['max_planet_mass']}")
    if query_params.get('min_distance'):
        where_clauses.append(f"sy_dist >= {query_params['min_distance']}")
    if query_params.get('max_distance'):
        where_clauses.append(f"sy_dist <= {query_params['max_distance']}")
    if query_params.get('habitable') == 'true':
        where_clauses.append("pl_eqt >= 180 AND pl_eqt <= 310")  # Habitability based on temperature
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY sy_dist"  # Sort by distance
    
    # Make the API request
    response = requests.get(
        EXOPLANET_API_BASE,
        params={
            'query': query,
            'format': 'json'
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Calculate habitability scores
        for planet in data:
            # Get temperature and mass values
            temp = planet.get('pl_eqt')
            mass = planet.get('pl_bmasse')
            
            # Calculate habitability score
            if temp is not None and mass is not None:
                # Simplified habitability score calculation
                mass_score = max(0, 1 - abs(float(mass) - 1) / 5)  # Closer to 1 Earth mass
                temp_score = max(0, 1 - abs(float(temp) - 288) / 200)  # Closer to Earth's 288K
                planet['habitability_score'] = (mass_score + temp_score) / 2 * 100  # Convert to percentage
            else:
                planet['habitability_score'] = 0.0
                
        return data
    
    return None

# Cache management endpoints
@app.route('/admin/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all caches - admin endpoint"""
    try:
        # Clear memory cache
        global memory_cache
        memory_cache = {}
        
        # Clear file cache
        for file in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
                
        return jsonify({"status": "success", "message": "Cache cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/admin/cache/status')
def cache_status():
    """Get cache status - admin endpoint"""
    try:
        # Count cache files
        file_count = len([f for f in os.listdir(CACHE_DIR) if os.path.isfile(os.path.join(CACHE_DIR, f))])
        
        # Count memory cache entries
        memory_count = len(memory_cache)
        
        return jsonify({
            "status": "success",
            "file_cache_count": file_count,
            "memory_cache_count": memory_count,
            "cache_dir": CACHE_DIR
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Add these routes from the original code
@app.route('/exoplanets')
def exoplanets():
    """Render the exoplanets page"""
    return render_template('exoplanets.html')

@app.route('/api/exoplanets')
def get_exoplanets():
    """API endpoint for exoplanets"""
    # Parameters for filtering
    star_type = request.args.get('star_type', '')
    min_distance = request.args.get('min_distance', '')
    max_distance = request.args.get('max_distance', '')
    min_planet_mass = request.args.get('min_planet_mass', '')
    max_planet_mass = request.args.get('max_planet_mass', '')
    habitable = request.args.get('habitable', '')
    
    # Create query params dict for cache key
    query_params = {
        'star_type': star_type,
        'min_distance': min_distance,
        'max_distance': max_distance,
        'min_planet_mass': min_planet_mass,
        'max_planet_mass': max_planet_mass,
        'habitable': habitable
    }
    
    # Get cached exoplanet data or fetch from API
    exoplanet_results = get_exoplanet_data(query_params)
    
    if exoplanet_results:
        return jsonify(exoplanet_results)
    else:
        return jsonify({'error': 'Failed to fetch exoplanet data'})

@app.route('/api/exoplanet/<planet_name>')
def get_exoplanet_detail(planet_name):
    """API endpoint for specific exoplanet details"""
    # Use cached function
    return jsonify(get_single_exoplanet_data(planet_name))

@cached(ttl=EXOPLANET_CACHE_TTL)
def get_single_exoplanet_data(planet_name):
    """Get data for a specific exoplanet with caching"""
    try:
        # Remove semicolon at end of query
        query = f"SELECT * FROM ps WHERE pl_name='{planet_name}'"
        
        response = requests.get(
            EXOPLANET_API_BASE,
            params={
                'query': query,
                'format': 'json'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                # Calculate habitability score
                planet = data[0]
                if 'pl_eqt' in planet and planet['pl_eqt'] is not None:
                    temp = float(planet['pl_eqt'])
                    if 273 <= temp <= 300:
                        hab_score = 1.0
                    elif 180 <= temp <= 350:
                        hab_score = 1.0 - min(abs(273 - temp), abs(300 - temp)) / 100
                    else:
                        hab_score = 0.0
                    planet['habitability_score'] = round(hab_score, 2)
                else:
                    planet['habitability_score'] = 0.0
                    
                return planet
            else:
                return {'error': 'Planet not found'}
        else:
            return {'error': 'Failed to fetch exoplanet data'}
    except Exception as e:
        return {'error': f"Failed to fetch exoplanet data: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)