# Mumbai Women's Safety Score Prediction

## Overview

This project is being developed for a hackathon to build a **geospatial machine learning pipeline** that predicts a **Women's Safety Score (0–100)** for different regions of Mumbai.

The city is divided into **H3 hexagons (resolution 8)**. Each hexagon contains engineered geospatial features extracted from OpenStreetMap and crime data. A Random Forest regression model is trained on a synthetic safety score generated from these features.

> **Note:** The safety score is **synthetically generated** for demonstration purposes and is **not an official measure of women's safety**.

---

# Project Pipeline

```
Mumbai Boundary
        │
        ▼
Generate H3 Hexagons
        │
        ▼
Download OpenStreetMap Data
        │
        ▼
Feature Engineering
        │
        ▼
Generate Synthetic Safety Score
        │
        ▼
Train Random Forest Model
        │
        ▼
Predict Safety Score
        │
        ▼
Interactive Map / Application
```

---

# Project Structure

```
girlthon/

├── data/
│   ├── gadm41_IND.gpkg
│   ├── mumbai_boundary.geojson
│   ├── mumbai_hexagons.geojson
│   ├── mumbai_features.geojson
│   ├── mumbai_ml_dataset.geojson
│   ├── crime.xlsx
│   ├── police.geojson
│   ├── hospitals.geojson
│   ├── railway.geojson
│   ├── metro.geojson
│   ├── bus_stops.geojson
│   ├── restaurants.geojson
│   ├── parks.geojson
│   ├── schools.geojson
│   └── pharmacies.geojson
│
├── script/
│   ├── create_boundary.py
│   ├── generate_hexagons.py
│   ├── download_osm.py
│   ├── download_all.py
│   ├── add_feature.py
│   ├── run_features.py
│   ├── generate_scores.py
│   ├── train_model.py
│   └── app.py
│
├── model.pkl
├── requirements.txt
└── README.md
```

---

# Completed Work

## 1. Mumbai Boundary Generation

Generated the Mumbai city boundary by merging:

- Mumbai City
- Mumbai Suburban

Output:

```
data/mumbai_boundary.geojson
```

---

## 2. H3 Hexagon Generation

Generated H3 hexagons covering Mumbai.

- Resolution: **8**
- Total Hexagons: **719**

Output:

```
data/mumbai_hexagons.geojson
```

Each hexagon contains:

- hex_id
- geometry

---

## 3. OpenStreetMap Data Collection

Reusable downloader implemented.

Downloaded:

- Police Stations
- Hospitals
- Railway Stations
- Metro Stations
- Bus Stops
- Restaurants
- Parks
- Schools
- Pharmacies

Outputs are stored inside the **data/** folder.

---

## 4. Feature Engineering

Feature engineering is reusable through:

```
script/add_feature.py
```

Current engineered features include:

### Distance Features

Nearest distance from each hexagon centroid to:

- police station
- hospital
- railway station
- metro station
- bus stop

Generated columns:

```
police_distance
hospital_distance
railway_distance
metro_distance
bus_stop_distance
```

---

### Count Features

Counts features located inside each H3 hexagon.

Generated columns:

```
restaurants
parks
schools
pharmacies
```

---

### Crime Feature

Crime locations are loaded from:

```
crime.xlsx
```

Crime incidents are spatially joined with H3 hexagons.

Generated column:

```
crime_count
```

---

## 5. Synthetic Safety Score

Synthetic target variable generated using:

```
score = 100

- crime penalty
- distance penalties

+ park bonus
+ school bonus
+ pharmacy bonus
+ restaurant bonus

clip(score, 0, 100)
```

Output:

```
data/mumbai_ml_dataset.geojson
```

Target column:

```
safety_score
```

---

## 6. Machine Learning

Model:

```
RandomForestRegressor
```

Features:

- police_distance
- hospital_distance
- railway_distance
- metro_distance
- bus_stop_distance
- restaurants
- parks
- schools
- pharmacies
- crime_count

Target:

```
safety_score
```

Outputs:

```
model.pkl
```

Current evaluation:

- Train/Test Split: 80/20
- R² ≈ 0.88

---

# Current Dataset

Each H3 hexagon contains:

```
hex_id

police_distance
hospital_distance
railway_distance
metro_distance
bus_stop_distance

restaurants
parks
schools
pharmacies

crime_count

safety_score

geometry
```

---

# Remaining Tasks

## 1. Prediction Pipeline

Implement terminal-based prediction.

Flow:

```
User enters location
        │
        ▼
Geocode location
        │
        ▼
Find corresponding H3 hexagon
        │
        ▼
Load engineered features
        │
        ▼
Predict using model.pkl
        │
        ▼
Display Women's Safety Score
```

---

## 2. User Interface

Build an interactive interface using:

- Streamlit
or
- Folium

Display:

- Color-coded H3 hexagons
- Safety Score
- Crime Count
- Nearby infrastructure
- Search by location

---

## Team Notes

- Feature engineering is centralized in `add_feature.py`.
- `run_features.py` calls the reusable feature engineering functions.
- Avoid creating separate scripts for every feature.
- The project follows a modular pipeline where each script performs one stage of the workflow.

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Generate boundary

```bash
python script/create_boundary.py
```

### Generate hexagons

```bash
python script/generate_hexagons.py
```

### Download OpenStreetMap data

```bash
python script/download_all.py
```

### Generate features

```bash
python script/run_features.py
```

### Generate synthetic safety score

```bash
python script/generate_scores.py
```

### Train model

```bash
python script/train_model.py
```

### Run application

```bash
python script/app.py
```

---

# Contributors

Hackathon Project

Feel free to contribute by:

- Improving feature engineering
- Improving the scoring methodology
- Enhancing the ML model
- Building the frontend
- Optimizing search and visualization
