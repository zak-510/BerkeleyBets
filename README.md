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

Open `http://localhost:5173` in your browser.

## Tech Stack

### Frontend
- **React 18**
- **Tailwind CSS**
- **Vite**
- **React Router**
- **Fuse.js**

### Backend
- **Node.js**
- **Express.js**
- **Python**
- **Firebase**

### ML
- **scikit-learn**
- **pandas**
- **numpy**]
- **joblib**

### Datasets
- **ESPN API**
- **NBA API**
- **Custom scrapers**

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

## Usage

### For Users
1. **Sign up/Login**: Create an account or log in to access the platform
2. **Browse Players**: Select a sport (NBA/NFL/MLB) to view top players
3. **View Player Profiles**: Click on any player to see detailed statistics
4. **Place Bets**: Use Bear Bucks to bet on player performance metrics
5. **Track Performance**: Monitor your betting history and portfolio
