# 🏀 NBA Player Fantasy Point Prediction System - LEAKAGE-FREE VERSION

A production-ready machine learning system for predicting NBA player fantasy points using position-specific models with **ZERO data leakage** and real-time NBA API data.

## 📋 Overview

This system uses the `nba_api` library to fetch live NBA player statistics and trains position-specific Random Forest models to predict fantasy basketball points. The system implements **strict temporal validation** and **historical feature engineering** to eliminate data leakage and provide truly predictive models.

### ✨ Key Features

- **🔒 ZERO DATA LEAKAGE**: Uses only historical averages from previous games
- **Position-Specific Models**: Separate models for PG, SG, SF, PF, and C positions  
- **Real NBA Data**: Integration with `nba_api` for live player statistics
- **Temporal Validation**: Time-series splits prevent data leakage
- **Historical Features**: Uses past game efficiency to predict future performance
- **Production Ready**: 100% success rate on inference with realistic predictions
- **Clean Data Pipeline**: Robust data validation and feature engineering

## 🚀 Quick Start

### Installation

1. **Install Dependencies**:
```bash
pip install pandas numpy scikit-learn nba_api joblib
```

2. **Train Models** (if needed):
```bash
python nba_model_fixed.py
```

3. **Run Inference on All Players**:
```bash
python run_inference.py
```

4. **Clean CSV Results**:
```bash
python clean_csv.py
```

## 📁 File Structure

```
nba/
├── nba_model_fixed.py                    # Main ML pipeline (LEAKAGE-FREE)
├── run_inference.py                      # Run predictions on all NBA players
├── clean_csv.py                          # Clean up CSV decimal places
├── inference_results_fixed.csv           # Model validation results
├── nba_inference_clean_*.csv            # Clean inference results
├── nba_pg_model_fixed.pkl               # Point Guard model (FIXED)
├── nba_sg_model_fixed.pkl               # Shooting Guard model (FIXED)
├── nba_sf_model_fixed.pkl               # Small Forward model (FIXED)
├── nba_pf_model_fixed.pkl               # Power Forward model (FIXED)
├── nba_c_model_fixed.pkl                # Center model (FIXED)
├── DATA_LEAKAGE_ANALYSIS.md             # Analysis of data leakage issues
└── README.md                            # This file
```

## 🎯 Fantasy Scoring System

The system uses standard fantasy basketball scoring:

| Statistic | Points | Bonus |
|-----------|--------|-------|
| Points | 1.0 per point | |
| Rebounds | 1.2 per rebound | |
| Assists | 1.5 per assist | |
| Steals | 3.0 per steal | |
| Blocks | 3.0 per block | |
| Turnovers | -1.0 per turnover | |
| Double-double | | +1.5 |
| Triple-double | | +3.0 |

## 🔒 Data Leakage Prevention

### The Problem
Previous models had **data leakage** where same-game statistics were used to predict that same game's performance, leading to unrealistically high accuracy.

### The Solution
Our **FIXED** model uses only **historical averages**:

- **Features**: `hist_fg_pct`, `hist_fg3_pct`, `hist_ft_pct`, `hist_min_avg`, `hist_usage_rate`
- **Source**: Calculated from previous games only (never current game)
- **Validation**: Temporal splits ensure past predicts future
- **Result**: Realistic performance (R² 0.2-0.6, not 0.9+)

## 🏋️ Training Models

### Basic Training
```bash
python nba_model_fixed.py
```

### Training Process
1. **Data Collection**: Fetches player game logs from NBA API
2. **Position Assignment**: Maps players to positions (PG, SG, SF, PF, C)
3. **Historical Feature Engineering**: Calculates rolling averages from previous games
4. **Data Filtering**: Removes players with insufficient history (< 5 games)
5. **Temporal Split**: Uses first 80% of games for training, last 20% for testing
6. **Model Training**: Trains separate Random Forest models per position
7. **Validation**: Time-series cross-validation
8. **Model Saving**: Saves trained models as `*_fixed.pkl` files

### Expected Performance (Realistic)
```
PTS:     MAE = 5.99  | R² = 0.389  | Within 6 pts:  58.3%
REB:     MAE = 2.11  | R² = 0.421  | Within 3 reb:  79.2%
AST:     MAE = 1.60  | R² = 0.352  | Within 3 ast:  88.4%
FANTASY: MAE = 9.47  | R² = 0.440  | Within 8 pts:  49.4%
```

## 🎯 Running Inference

### All NBA Players
```bash
python run_inference.py
```

This will:
1. Fetch data for 100+ active NBA players
2. Calculate historical features for each player
3. Run predictions using the leakage-free models
4. Save results to timestamped CSV file
5. Display top performers and position breakdowns

### Clean Up Results
```bash
python clean_csv.py
```

Rounds decimal places for better readability:
- Historical percentages: 3 decimal places
- Minutes: 1 decimal place  
- Predictions: 1 decimal place

## 📊 Sample Results

### Top Performers (Fantasy Points)
| Player | Pos | FG% | 3P% | FT% | Min | PTS | REB | AST | Fantasy |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|---------|
| Giannis Antetokounmpo | PF | 59.6% | 19.3% | 60.7% | 34.0 | 32.3 | 13.0 | 4.8 | **56.3** |
| Paolo Banchero | PF | 44.9% | 32.1% | 72.2% | 34.2 | 26.4 | 8.4 | 4.9 | **46.6** |
| Bam Adebayo | C | 48.7% | 35.1% | 75.7% | 34.3 | 20.9 | 9.9 | 3.3 | **43.8** |

## 🔧 Programmatic Usage

```python
from nba_model_fixed import NBAPlayerProjectionModelFixed

# Initialize model
model = NBAPlayerProjectionModelFixed()

# Load pre-trained models
model.load_models()

# Make prediction using historical features
player_features = {
    'position': 'PG',
    'hist_fg_pct': 0.450,      # Historical field goal percentage
    'hist_fg3_pct': 0.380,     # Historical 3-point percentage  
    'hist_ft_pct': 0.850,      # Historical free throw percentage
    'hist_min_avg': 32.0,      # Historical minutes average
    'hist_usage_rate': 0.667   # Historical usage rate
}

prediction = model.predict_player_performance(player_features)
print(f"Predicted: {prediction['pts']} PTS, {prediction['fantasy_points']} Fantasy")
```

## ⚠️ Important Notes

### Data Requirements
- Players need **5+ games** for historical feature calculation
- **First 3 games** are skipped (insufficient history)
- Only players with **valid shooting percentages** are included

### Model Limitations
- Predictions are based on **historical efficiency only**
- Does not account for injuries, rest, or matchup-specific factors
- Performance is **intentionally realistic** (not perfect)

### File Naming Convention
- `*_fixed.pkl`: Leakage-free models (USE THESE)
- `*.csv`: Clean results with proper decimal rounding

## 🎯 Production Use Cases

- **Daily Fantasy Sports**: Realistic player projections
- **Player Analysis**: Efficiency-based performance prediction
- **Trade Evaluation**: Historical performance patterns
- **Draft Strategy**: Position-specific value assessment

## 📈 Model Quality Indicators

✅ **Good Signs:**
- Perfect predictions < 5%
- R² scores 0.2-0.6 range
- Position-appropriate predictions
- Realistic statistical ranges

❌ **Warning Signs:**
- Perfect predictions > 10%
- R² scores > 0.9
- Impossible statistical values
- Same-game feature usage

---

**Built with production-ready, leakage-free machine learning practices** 🏀✨ 