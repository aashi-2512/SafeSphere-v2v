<div align="center">

<img src="assets/logo.png" width="160"/>

# 🛡️ SafeSphere

### AI-Powered Women's Safety Platform

**Intelligent Safe Routing • AI Safety Intelligence • Real-Time Emergency SOS**

<p>

![Next.js](https://img.shields.io/badge/Next.js-React-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript)
![Machine Learning](https://img.shields.io/badge/ML-Random%20Forest-success)
![Hackathon](https://img.shields.io/badge/Built%20For-Hackathon-orange)

</p>

### **Safer Spaces. Smarter Response.**

</div>

---

## 🌍 Overview

SafeSphere is a full-stack AI platform that helps users make safer travel decisions and get immediate help in emergencies. Most navigation apps optimize for speed — SafeSphere optimizes for **safety**, combining crime intelligence, infrastructure data, and geospatial ML into one system that runs from prevention through emergency response.

Four components power the platform:

- 🧠 **AI Safety Scores** — ML-predicted safety rating for any location
- 🗺️ **Intelligent Safe Routing** — routes that weigh real-world risk, not just distance
- 🚨 **Emergency SOS** — live GPS + voice streaming the moment a user needs help
- 🖥️ **Responder Dashboard** — real-time situational awareness for emergency personnel

---

## ✨ Features

### 🧠 AI Safety Score

Search any location in Mumbai for an AI-generated Women's Safety Score (0–100), powered by a **Random Forest Regressor** trained across **719 H3 hexagonal cells** covering the city.

The model learns from:
Police & hospital proximity • Railway & metro connectivity • Bus stop density • Restaurant, park, school & pharmacy density • Historical crime counts

| Score | Classification |
|--------|----------------|
| 80–100 | 🟢 Very Safe |
| 60–79 | 🟢 Safe |
| 40–59 | 🟡 Moderate |
| 20–39 | 🔴 Unsafe |
| 0–19 | 🔴 Very Unsafe |

**Pipeline:** OpenStreetMap + crime data → feature engineering → H3 hexagonal grid → Random Forest → normalized safety score per hexagon.

### 🗺️ Intelligent Safe Routing

Instead of just the fastest path, the routing engine evaluates how safe an entire journey is — sampling the route across H3 hexagons and scoring it against **time-of-day risk profiles** (☀️ Day / 🌆 Evening / 🌙 Night), since the same street can carry different risk depending on when you travel it.

**How a route gets built:**
1. OSRM generates the quickest route between start and destination
2. The route is sampled across H3 hexagons and scored for risk
3. Segments exceeding the risk threshold trigger a search of neighboring hexagons (K-ring search) for safer detours
4. Candidate detours are compared using a weighted cost function:

   ```
   Route Cost = 0.5 × Mean Risk + 0.3 × Maximum Risk + 2.0 × Unsafe Hex Count
   ```

   Weighting unsafe hex count heavily prevents a single dangerous hotspot from hiding inside an otherwise-safe average.
5. The safest viable route within the detour limit is returned

Every response includes **explainable metadata** — mean risk, max risk, unsafe hex count, route cost, distance difference, and iteration history — so routing decisions are transparent, not a black box. If no safer detour exists within the allowed distance, the platform tells the user plainly that the current route is already the safest available, rather than forcing an unnecessary detour.

### 🚨 Emergency SOS

Hold-to-activate SOS that immediately:
- Creates a secure, JWT-authenticated emergency session
- Shares live GPS location
- Streams live microphone audio to responders over WebSockets (low-latency, multi-listener, with automatic session cleanup)

### 🖥️ Emergency Responder Dashboard

Gives responders everything in one view: victim details and phone number, live GPS on an interactive map, active session list, live audio stream and transcript, and real-time session status.

---

## 📸 Application Preview

| | |
|---|---|
| **Home** ![](assets/home.png) | **AI Safety Score** ![](assets/safety-map.png) |
| **Safe Routing** ![](assets/route.png) | **Emergency SOS** ![](assets/sos.png) |

**Emergency Dashboard**
![](assets/admin-dashboard.png)

---

## 📂 Project Structure

```text
SafeSphere-v2v/
│
├── frontend/          # Next.js application
│   ├── app/
│   ├── components/
│   └── public/
│
├── backend/           # FastAPI backend
│   ├── app/
│   ├── routes/
│   ├── websocket/
│   └── models/
│
├── script/            # ML pipeline & routing engine
│   ├── safe_route.py
│   ├── train_model.py
│   ├── generate_scores.py
│   └── run_features.py
│
├── data/               # Geospatial datasets
├── assets/             # README images
├── output/             # Generated route maps
├── cache/
│
├── model.pkl
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

**1. Clone the repo**
```bash
git clone <your-repository-url>
cd SafeSphere-v2v
```

**2. Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs`

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```
App: `http://localhost:3000`

---

## 📡 API Endpoints

**Safety**

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/safety/score` | Predict Women's Safety Score |
| POST | `/safety/route` | Generate safest & quickest routes |
| GET | `/safety/hexagons` | Retrieve H3 safety map |

**Emergency**

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/sos` | Create emergency session |
| GET | `/session/{id}` | Session status |
| DELETE | `/session/{id}` | End emergency session |
| GET | `/sessions` | List active sessions |

**WebSocket**

| Endpoint | Purpose |
|-----------|---------|
| `/ws/broadcast` | Victim broadcasts live audio |
| `/ws/listen` | Responders receive live audio |

---

## 🛠️ Technology Stack

| Layer | Tools |
|---|---|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, Leaflet, Framer Motion |
| **Backend** | FastAPI, Python, Uvicorn, WebSockets, JWT, Pydantic |
| **Machine Learning** | Scikit-learn (Random Forest), GeoPandas, H3, Shapely, Pandas, NumPy |
| **Mapping & Geospatial** | OpenStreetMap, OSRM, Nominatim, Folium, GeoJSON |

---

## 🧪 Testing

Regression and integration tests cover safety score predictions, the safe routing engine, time-based risk evaluation, threshold validation, SOS session creation, WebSocket communication, and emergency session lifecycle.

```bash
pytest
```

---

## 🔮 Future Enhancements

Multi-city support • Driving & cycling safety profiles • Push notifications • Smartwatch integration • Community incident reporting • Offline emergency mode • Live crime feed integration

---

## 👥 Contributors

Built with ❤️ by the **SafeSphere Team**.

---

## ⚠️ Disclaimer

SafeSphere is a hackathon prototype demonstrating how AI, ML, and geospatial analytics can improve urban safety. Safety scores are generated from historical crime data, public infrastructure, and predictive models — they are for demonstration purposes only and should **not** be treated as official safety ratings or emergency guidance.

