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
   git clone https://github.com/HmbleCreator/cosmic-observer.git
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
![Screenshot 2025-04-14 192839](https://github.com/user-attachments/assets/7b08891e-57ea-4ff4-afad-aaf1905f5695)
![Screenshot 2025-04-14 193205](https://github.com/user-attachments/assets/bd37eca9-4a43-439c-ade1-4f2ae37ef00c)
![Screenshot 2025-04-14 193152](https://github.com/user-attachments/assets/9169ceeb-a6ea-4c5f-af69-d599d9201abf)
![Screenshot 2025-04-14 193101](https://github.com/user-attachments/assets/e9d6a148-f88a-4107-9a00-a41f62c364ea)
![Screenshot 2025-04-14 193030](https://github.com/user-attachments/assets/984701d6-5409-4df0-bf3b-81c1470d923c)
![Screenshot 2025-04-14 193010](https://github.com/user-attachments/assets/2a957417-ac18-49b0-97db-1ac77601e71f)
![Screenshot 2025-04-14 192911](https://github.com/user-attachments/assets/5d9c5b18-9957-4881-9bd8-02cf7e5b3728)


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- NOAA for providing space weather data
- NASA for the exoplanet database
- The Flask and Plotly communities for their excellent documentation
