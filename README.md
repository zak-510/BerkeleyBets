```bash
# 1. Clone
git clone https://github.com/zak-510/BerkeleyBets.git
cd BerkeleyBets

# 2. Backend – install deps & run (Port 3001)
npm install
npm start

# 3. Front-end – in a new terminal (Port 5173)
cd client
npm install
npm run dev -- --host
```

Open `http://localhost:5173` in your browser – the React app will talk to the unified API on `http://localhost:3001`.

## Features

### Core Functionality
- **Multi-Sport Support**: NBA, NFL, and MLB player predictions
- **AI-Powered Predictions**: Machine learning models for player performance forecasting
- **Real-Time Data**: Live player statistics and performance metrics
- **Betting System**: Virtual Bear Bucks currency with over/under/exact betting options
- **Portfolio Management**: Track active bets, betting history, and performance analytics
- **Player Profiles**: Comprehensive stat displays with position-specific metrics

### Technical Features
- **Responsive Design**: Optimized for desktop and mobile devices
- **Real-Time Updates**: Live API integration for current player data
- **Data Persistence**: Local storage and Firebase integration for user data
- **Advanced Search**: Fuzzy search across all players and sports
- **Health Monitoring**: API status tracking and error handling

## Technology Stack

### Frontend
- **React 18**: Modern component-based UI framework
- **Tailwind CSS**: Utility-first styling framework
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing
- **Fuse.js**: Fuzzy search functionality

### Backend
- **Node.js**: Server runtime environment
- **Express.js**: Web application framework
- **Python**: Machine learning and data processing
- **Firebase**: Authentication and data storage

### Machine Learning
- **scikit-learn**: ML model training and prediction
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **joblib**: Model serialization and loading

### Data Sources
- **ESPN API**: Player statistics and game data
- **NBA API**: Basketball-specific data
- **Custom scrapers**: MLB and NFL data collection

## Project Structure

```
BerkeleyBets/
├── client/                     # React frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Main application pages
│   │   ├── services/          # API service layers
│   │   └── contexts/          # React context providers
├── backend/                   # Express API server
│   └── server.js             # Main server file
├── ml-models/                 # Machine learning models & scripts
│   ├── nba/                   # NBA models & inference
│   │   ├── scripts/           # get_top_players.py, search_players.py
│   │   ├── models/            # Trained model files (.pkl)
│   │   └── docs/              # NBA-specific documentation
│   ├── nfl/                   # NFL models & inference  
│   │   ├── scripts/           # get_top_players.py, search_players.py
│   │   └── models/            # Trained model files (.pkl)
│   └── mlb/                   # MLB models & inference
│       ├── scripts/           # get_top_players.py, search_players.py
│       ├── models/            # Trained model files (.pkl)
│       ├── src/               # MLB utilities & data processing
│       └── docs/              # MLB-specific documentation
├── docs/                      # General documentation & specs
└── archive/                   # Historical data & old training code
```

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zak-510/BerkeleyBets.git
cd BerkeleyBets
```

2. **Install backend dependencies & start the API**
```bash
npm install
npm start     # Unified Express API on port 3001
```

3. **Install frontend dependencies & start the React dev server**
```bash
cd client
npm install
npm run dev -- --host   # Serves the app at http://localhost:5173
```

4. **(Optional) Python environment for model retraining**
If you need to retrain or fine-tune ML models:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r ml-models/requirements.txt  # or your own list
```

5. **Environment variables (Firebase, etc.)**
```bash
# Create .env file in client directory
cp client/.env.example client/.env
# Add your Firebase and API configurations
```

### Configuration

#### Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication and Firestore
3. Add your Firebase configuration to `client/.env`:
```env
VITE_API_KEY=your_api_key
VITE_AUTH_DOMAIN=your_auth_domain
VITE_PROJECT_ID=your_project_id
```

#### API Configuration
All sports endpoints (NBA, NFL, MLB) are served by the unified Express API on:
- `http://localhost:3001`
The React client proxies requests automatically.

## Usage

### For Users
1. **Sign up/Login**: Create an account or log in to access the platform
2. **Browse Players**: Select a sport (NBA/NFL/MLB) to view top players
3. **View Player Profiles**: Click on any player to see detailed statistics
4. **Place Bets**: Use Bear Bucks to bet on player performance metrics
5. **Track Performance**: Monitor your betting history and portfolio

### For Developers

#### Running Models Locally
```bash
# NBA models
cd ml-models/nba/scripts
python get_top_players.py
python search_players.py "LeBron James"

# NFL models
cd ../nfl/scripts
python get_top_players.py
python search_players.py "Josh Allen"

# MLB models
cd ../mlb/scripts
python get_top_players.py
python search_players.py "Aaron Judge"
```

#### Model Training
```bash
# Retrain NBA models
cd Training Model/nba
python nba_model_fixed.py

# Retrain NFL models
cd ../nfl
python nfl_model.py

# Retrain MLB models
cd ../../mlb
python train_balanced_realistic_models.py
```

## API Endpoints (Unified – Port 3001)

### NBA
- `GET /api/nba/players` – All players
- `GET /api/nba/players/top?limit=50` – Top players
- `GET /api/nba/players/:position` – Position-filtered players
- `GET /api/nba/search?q=name` – Search players

### NFL
- `GET /api/nfl/players`
- `GET /api/nfl/players/top?limit=50`
- `GET /api/nfl/players/:position`
- `GET /api/nfl/search?q=name`

### MLB
- `GET /api/mlb/players`
- `GET /api/mlb/players/top?limit=50`
- `GET /api/mlb/players/:position`
- `GET /api/mlb/search?q=name`

### Misc
- `GET /health` – Health check for the backend

## Data Models

### Player Data Structure
```javascript
{
  id: string,
  name: string,
  team: string,
  position: string,
  stats: {
    predictedPoints: number,
    confidence: number,
    // Sport-specific stats...
  },
  image: string, // Position icon
  // Additional sport-specific fields...
}
```

### Betting Data Structure
```javascript
{
  id: string,
  playerId: string,
  playerName: string,
  sport: 'nba' | 'nfl' | 'mlb',
  statType: string,
  statLabel: string,
  prediction: number,
  target: number,
  direction: 'over' | 'under' | 'exact',
  amount: number,
  potentialPayout: number,
  timestamp: string,
  status: 'active' | 'won' | 'lost' | 'cashed_out',
  confidence: number
}
```

## Model Performance

### NBA Models
- **Points Prediction**: R² score of 0.85+ across all positions
- **Rebounds/Assists**: Position-specific models with 80%+ accuracy
- **Training Data**: 3+ seasons of historical performance

### NFL Models
- **Fantasy Points**: 78% accuracy for skill position players
- **Position-Specific Stats**: Separate models for QB, RB, WR, TE
- **Training Data**: Multiple seasons with weather and matchup factors

### MLB Models
- **Batting Stats**: Hits, runs, RBIs prediction with 75%+ accuracy
- **Pitching Stats**: Strikeouts and innings pitched forecasting
- **Training Data**: Comprehensive historical statistics
