# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

BerkeleyBets is a comprehensive sports betting prediction platform featuring:
- **React frontend** (`client/`) - Modern web interface with Vite, TailwindCSS, and Firebase integration
- **Sports prediction models** (`Training Model/`) - Machine learning systems for NFL, NBA, and MLB
- **MLB prediction system** (`mlb/`) - Production-ready fantasy points prediction with temporal validation

## Architecture

### Frontend (`client/`)
- **Framework**: React 19 with Vite build system
- **Styling**: TailwindCSS 4.x with Heroicons
- **Authentication**: Firebase integration
- **Search**: Fuse.js for fuzzy search functionality
- **Pages**: Dashboard, Login, SignUp with React Router

### Sports Prediction Models (`Training Model/`)
Three separate prediction systems:
- **NFL**: Position-specific models (QB, RB, WR, TE) using `nfl_data_py`
- **NBA**: Position-based models (PG, SG, SF, PF, C) with `nba_api` integration
- **MLB**: Game-level fantasy prediction system (see detailed section below)

### MLB Prediction System (`mlb/`)
**Production-ready system** with strict temporal validation to prevent data leakage:
- **Data Collection**: Uses `pybaseball` for game logs and Statcast data
- **Models**: Position-specific models (C, 1B, 2B, 3B, SS, OF, P)
- **Features**: Historical rolling averages (15-game windows)
- **Validation**: Temporal splits ensuring no future data contamination
- **Performance**: 86.9% consistency rate, R² scores 0.25-0.95 across positions

## Common Development Commands

### Frontend Development
```bash
cd client/
npm install           # Install dependencies
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Sports Models

#### NFL System
```bash
cd "Training Model/nfl/"
python nfl_model.py                    # Train models
python nfl_cli.py --interactive        # Interactive predictions
python nfl_gui.py                      # GUI interface
```

#### NBA System
```bash
cd "Training Model/nba/"
python nba_model_fixed.py             # Train leakage-free models
python run_inference.py               # Run predictions on all players
python clean_csv.py                   # Clean results formatting
```

#### MLB System (Production)
```bash
cd mlb/
python mlb_cli.py                      # Interactive CLI
python predict.py "Aaron Judge"        # Single player prediction
python run_realistic_inference.py     # Production inference system
```

## Key Implementation Details

### Data Integrity (MLB System)
- **Zero Data Leakage**: Uses only historical data (games 1 to N-1) to predict game N
- **Temporal Validation**: Strict chronological ordering with validation checks
- **Fantasy Scoring**: Standardized scoring system for batters and pitchers
- **Rate Limiting**: 2-second delays between API calls to respect service limits

### Model Architecture
- **Position-Specific**: Separate models trained for each position
- **Feature Engineering**: Rolling averages, recent form, consistency metrics
- **Validation**: TimeSeriesSplit cross-validation with temporal gaps
- **Performance Monitoring**: Tracks consistency rates and prediction accuracy

### Production Files
- `mlb_cli.py`: Main CLI interface for predictions
- `mlb_inference.py`: Core inference engine
- `src/data_collection.py`: Enhanced Statcast data collection
- `src/temporal_validation.py`: Data leakage prevention
- `src/model_training.py`: Position-specific model training

## Testing and Validation

### MLB System Testing
```bash
cd mlb/
python detect_data_leakage.py         # Validate temporal integrity
python run_step1_data_collection.py   # Test data collection pipeline
```

### Performance Benchmarks
- **MLB Consistency Rate**: Target 80%+ (currently 86.9%)
- **Player Coverage**: Target 70%+ (currently 76.1%)
- **Model R² Scores**: 0.25-0.95 depending on position

## Database Integration
- Firebase authentication and user management
- Player lookup tables with MLB IDs and position mappings
- Cached game logs and statistical data to minimize API calls

## Development Workflow
1. All sports models use strict temporal validation to prevent data leakage
2. Frontend follows React/Vite conventions with TypeScript support
3. Machine learning models are position-specific for better accuracy
4. Production systems include comprehensive error handling and fallback mechanisms