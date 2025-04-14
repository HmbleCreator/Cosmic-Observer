# 🌌 Cosmic Observer

Cosmic Observer is a Python-powered Flask web application designed to immerse users in the wonders of space. It provides real-time data and interactive visualizations on space weather, aurora visibility, and exoplanet exploration through an engaging, easy-to-use interface.

## ✨ Features

### 🌞 Space Weather Dashboard
- Monitor solar wind speed, KP index (geomagnetic activity), and sunspot count in real-time
- Interactive visualizations of space weather metrics using Plotly
- Historical data trends to track space weather changes

### 🌈 Aurora Visibility Alerts
- Check aurora visibility probability based on your location
- Interactive global aurora visibility map
- Personalized alerts based on current space weather conditions

### 🪐 Exoplanet Explorer
- Search and filter exoplanets based on various characteristics
- Interactive visualization of exoplanet data
- Explore habitability scores and other key metrics

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cosmic-observer.git
   cd cosmic-observer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## 🛠️ Technologies Used

- **Flask**: Web framework for the backend
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **Requests**: API interactions
- **Geopy**: Geolocation services for aurora visibility
- **HTML/CSS**: Frontend styling with a space-inspired theme

## 📚 Data Sources

- Space Weather Data: NOAA's Space Weather Prediction Center (SWPC)
- Exoplanet Data: NASA's Exoplanet Archive
- Aurora Visibility: Calculated based on KP index and user location

## 📷 Screenshots

*[Add screenshots of your application here]*

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- NOAA for providing space weather data
- NASA for the exoplanet database
- The Flask and Plotly communities for their excellent documentation