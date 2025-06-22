# MLB Fantasy Prediction System - Usage Guide

## 🚀 Quick Start

The system provides multiple ways to make predictions:

### 1. Single Player Predictions
```bash
# Production mode (recommended)
python predict.py "Aaron Judge" --production

# Standard mode
python predict.py "Gerrit Cole"
```

### 2. CSV Batch Predictions

#### For Batters Only
```bash
python predict_batters_csv.py your_batters.csv
```

#### For Pitchers Only
```bash
python predict_pitchers_csv.py your_pitchers.csv
```

#### Unified Interface (Auto-detects)
```bash
python predict_csv.py your_players.csv
```

### 3. Interactive CLI
```bash
python mlb_cli.py
```

## 📊 CSV Input Format

### Required Columns
All CSV prediction scripts require these columns:

```csv
player_name,avg_fantasy_points_L15,avg_fantasy_points_L10,avg_fantasy_points_L5,games_since_last_good_game,trend_last_5_games,consistency_score
Aaron Judge,8.5,9.2,7.8,2,0.5,0.75
```

### Column Descriptions
- **player_name**: Player's name
- **avg_fantasy_points_L15**: Average fantasy points over last 15 games
- **avg_fantasy_points_L10**: Average fantasy points over last 10 games  
- **avg_fantasy_points_L5**: Average fantasy points over last 5 games
- **games_since_last_good_game**: Games since scoring >10 fantasy points
- **trend_last_5_games**: Performance trend (positive = improving)
- **consistency_score**: Performance consistency (0-1, higher = more consistent)

### Optional Columns
- **position**: Player position (C, 1B, 2B, 3B, SS, OF for batters; P for pitchers)

## 📈 Model Performance

### Current Model Performance
- **Batter Models**: R² = 0.28 (realistic for baseball prediction)
- **Pitcher Model**: R² = 0.78 (excellent performance)
- **Training Data**: Real 2023-2024 MLB seasons (1,419 player-seasons)

### Confidence Levels
- **Batters**: Confidence ~0.30 (reflects model uncertainty)
- **Pitchers**: Confidence ~0.78 (higher confidence from better model)

## 🎯 Available Positions

### Batter Positions
- **C**: Catcher
- **1B**: First Base
- **2B**: Second Base
- **3B**: Third Base
- **SS**: Shortstop
- **OF**: Outfield (LF, CF, RF)

### Pitcher Positions
- **P**: Pitcher (all pitchers use same model)

## 📁 File Structure

```
mlb/
├── predict.py                    # Single player predictions
├── predict_csv.py                # Unified CSV interface
├── predict_batters_csv.py        # Batter-specific CSV predictions
├── predict_pitchers_csv.py       # Pitcher-specific CSV predictions
├── mlb_cli.py                    # Interactive CLI
├── mlb_inference_production.py   # Production inference system
├── models/                       # Trained models (symlink)
├── src/                          # Core system modules
├── mlb_data/                     # Cached player data
└── docs/                         # Documentation
```

## 🔧 Advanced Usage

### Custom Output Locations
```bash
# Specify output file
python predict_batters_csv.py batters.csv --output my_results.csv

# Specify output directory
python predict_csv.py players.csv --output-dir results/
```

### Custom Model Directory
```bash
# Use different models
python predict_csv.py players.csv --models custom_models/
```

### Force Player Type
```bash
# Force all players to be treated as batters
python predict_csv.py players.csv --type batters

# Force all players to be treated as pitchers
python predict_csv.py players.csv --type pitchers
```

## 📊 Output Format

### CSV Output Columns

#### Batter Predictions
```csv
player_name,position,model_used,predicted_fantasy_points,confidence,model_r2,prediction_date
Aaron Judge,OF,OF,7.89,0.30,0.286,2025-06-22 01:09:24
```

#### Pitcher Predictions
```csv
player_name,position,predicted_fantasy_points,confidence,model_r2,prediction_date
Spencer Strider,P,12.35,0.78,0.785,2025-06-22 01:09:30
```

## 🚨 Important Notes

### Performance Expectations
- **Baseball is inherently unpredictable**: R² values of 0.2-0.4 for batters are realistic
- **Pitcher predictions are more reliable**: R² of 0.78 indicates good predictive power
- **Use predictions as guidance**: Not absolute forecasts

### Data Requirements
- **Historical features required**: System needs past performance data
- **Temporal integrity**: Uses only historical data (no future leakage)
- **Feature consistency**: All required columns must be present

### System Status
- **Production Ready**: Core functionality tested and working
- **Real Data Training**: Models trained on actual 2023-2024 MLB data
- **Realistic Claims**: Performance metrics reflect actual capability

## 🆘 Troubleshooting

### Common Issues

1. **"Missing required columns"**
   - Ensure CSV has all required columns
   - Check column names match exactly

2. **"No models found"**
   - Verify `models/` directory exists
   - Check model files are present

3. **"No data found for player"**
   - Player may not have recent game data
   - Try different date range or player

### Getting Help
```bash
# See command help
python predict.py --help
python predict_csv.py --help

# Check system status
python mlb_cli.py
```

## 📞 Support

For issues or questions:
1. Check this usage guide
2. Review error messages carefully
3. Ensure input data format is correct
4. Verify all required files are present