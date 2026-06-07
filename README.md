FIFA World Cup 2026 Simulator

An AI-powered FIFA World Cup simulator that predicts match outcomes, simulates the entire FIFA World Cup tournament, and estimates championship probabilities using machine learning and Monte Carlo simulations.

Features
Match outcome prediction using an XGBoost machine learning model
Team strength evaluation using FIFA ratings, Elo ratings, squad depth, and recent performance
FIFA World Cup 2026 tournament simulation
Group stage and knockout stage progression
Monte Carlo simulation for tournament forecasting
FastAPI backend for prediction services
React + Vite frontend for interactive user experience
REST API integration between frontend and backend
Tech Stack
Backend
Python
FastAPI
Pandas
NumPy
Scikit-Learn
XGBoost
Frontend
React
Vite
Axios
CSS
Data & Modeling
FIFA historical rankings
Elo ratings
Feature Engineering
Machine Learning
Monte Carlo Simulation
Project Structure
fifa_wc_simulator/
│
├── api/                    # FastAPI endpoints
├── data/                   # Datasets and processed data
├── frontend/               # React frontend
├── models/                 # ML models and feature engineering
├── simulation/             # Tournament and Monte Carlo simulations
├── notebooks/              # Research and experimentation
├── tests/                  # Unit tests
└── docs/                   # Screenshots and documentation
Key Features Implemented
Match Predictor

Predicts the probability of:

Home Team Win
Draw
Away Team Win

using engineered features such as:

FIFA ratings
Elo ratings
Squad depth
Superstar index
Recent form metrics
Tournament Simulator

Simulates:

Group Stage
Round of 32
Round of 16
Quarter Finals
Semi Finals
Third Place Playoff
Final

and determines:

Champion
Runner-Up
Third Place Team
Monte Carlo Simulator

Runs multiple tournament simulations to estimate:

Championship probability
Runner-up probability
Tournament performance distribution
Machine Learning Pipeline
Data Collection
Data Cleaning
Historical Feature Engineering
Elo Rating Integration
Feature Selection
Model Training (XGBoost)
Model Evaluation
Prediction Service Deployment
Installation
Clone Repository
git clone https://github.com/IshaanS2810/Fifa-WC-Simulator.git
cd Fifa-WC-Simulator
Create Virtual Environment
python -m venv .venv
Activate Virtual Environment

Windows:

.venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
Run Backend
python -m uvicorn fifa_wc_simulator.api.app:app --reload

Backend runs at:

http://127.0.0.1:8000
Run Frontend
cd frontend
npm install
npm run dev

Frontend runs at:

http://localhost:5173
API Endpoints
Match Prediction
POST /api/simulate-match
Tournament Simulation
POST /api/simulate-tournament
Monte Carlo Simulation
POST /api/monte-carlo
Health Check
GET /health
Future Enhancements
Live FIFA rankings integration
Team lineup and injury analysis
Player-level impact modeling
World Cup qualification simulation
Interactive tournament bracket visualization
Explainable AI predictions
