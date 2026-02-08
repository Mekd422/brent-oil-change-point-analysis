# Brent Oil Change Point Analysis

A comprehensive analysis of Brent oil price changes and their association with major geopolitical and economic events using Bayesian change point detection.

## Project Overview

This project analyzes how major political and economic events affect Brent oil prices, focusing on:
- Political decisions
- Conflicts in oil-producing regions
- International sanctions
- OPEC policy changes

## Project Structure

```
brent-oil-change-point-analysis/
├── data/
│   ├── events.csv              # Key events dataset
│   └── brent_prices.csv        # Historical Brent oil prices
├── notebooks/
│   └── change_point_analysis.ipynb  # Main analysis notebook
├── backend/
│   ├── app.py                  # Flask application
│   ├── models.py               # Data models
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/                    # React source code
│   ├── public/                 # Public assets
│   └── package.json            # Node dependencies
├── docs/
│   ├── task1_foundation.md     # Task 1 deliverables
│   └── assumptions_limitations.md
└── README.md
```

## Tasks

### Task 1: Foundation
- Data analysis workflow
- Event data compilation
- Assumptions and limitations documentation

### Task 2: Change Point Modeling
- Bayesian change point detection using PyMC
- Statistical analysis and interpretation
- Impact quantification

### Task 3: Interactive Dashboard
- Flask backend API
- React frontend with visualizations

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Data Generation
First, generate the Brent oil price dataset:
```bash
python scripts/generate_brent_data.py
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The backend API will run on `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

### Running the Analysis Notebook
To run the Jupyter notebook for change point analysis:
```bash
# Install Jupyter if not already installed
pip install jupyter

# Navigate to notebooks directory
cd notebooks
jupyter notebook change_point_analysis.ipynb
```

## API Endpoints

The Flask backend provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/prices` - Get historical price data (supports `start_date`, `end_date` query params)
- `GET /api/events` - Get event data (supports `category`, `impact_level`, `start_date`, `end_date` query params)
- `GET /api/statistics` - Get summary statistics (supports `start_date`, `end_date` query params)
- `GET /api/event-impact` - Get price impact around specific events (requires `event_date`, optional `window_days`)
- `GET /api/categories` - Get list of event categories and impact levels
- `GET /api/date-range` - Get available date range in dataset

## Authors

Data Science Team - Birhan Energies
