# MLB Leak-Free Prediction System - Architecture Design

## 🎯 **System Overview**

A game-level MLB fantasy prediction system that follows strict temporal validation to eliminate data leakage while providing realistic, actionable predictions.

### **Core Principles (The 5 Rules)**
1. **Zero Data Leakage**: Never use future data to predict past/current performance
2. **Simplicity with Maximal Functionality**: Build the simplest system that delivers core value
3. **Position-Specific Reality**: Honor baseball's positional differences with proper data
4. **Game-Level Granularity**: Predict individual game performance, not season totals
5. **Realistic Performance Expectations**: Set honest benchmarks (R² 0.25-0.45)

---

## 📊 **1. Data Collection Strategy**

### **Primary Data Source**
- **Function**: `pybaseball.season_game_logs(player_id, year, player_type)`
- **Coverage**: Individual game logs for all MLB players
- **Granularity**: Game-by-game statistics
- **Historical Depth**: 2019-2024 (5 seasons for robust training)

### **Player Discovery Pipeline**
```
Step 1: Get Active Player List
├── Use batting_stats_bref(2024) for position players
├── Use pitching_stats_bref(2024) for pitchers  
└── Extract player names → playerid_lookup() → MLB IDs

Step 2: Position Assignment
├── Manual position mapping table (C, 1B, 2B, 3B, SS, OF, P)
├── Fallback: Infer from game log patterns
└── Group similar positions: LF/CF/RF → OF

Step 3: Game Log Collection
├── season_game_logs(player_id, year) for each player/year
├── Rate limiting: 1 request per 2 seconds
└── Cache results locally (CSV files by player/year)
```

### **Rate Limiting & Error Handling**
- **API Limits**: 1 request per 2 seconds (conservative)
- **Retry Logic**: 3 attempts with exponential backoff
- **Timeout Handling**: 30-second timeout per request
- **Error Recovery**: Continue with available data, log failures
- **Progress Tracking**: Save intermediate results every 10 players

### **Caching Strategy**
```
Cache Structure:
mlb_data/
├── raw_game_logs/
│   ├── 2024/
│   │   ├── 592450_aaron_judge.csv
│   │   ├── 543037_gerrit_cole.csv
│   │   └── ...
│   └── 2023/
├── processed_features/
│   └── historical_features_2024.csv
└── position_mapping.csv
```

---

## 🔧 **2. Historical Feature Engineering Architecture**

### **Feature Categories**

#### **Position Players (C, 1B, 2B, 3B, SS, OF)**
```python
# Historical Performance (Last N Games)
hist_batting_avg = hits / at_bats (last 15 games)
hist_hr_rate = home_runs / games (last 15 games)  
hist_rbi_rate = rbi / games (last 15 games)
hist_runs_rate = runs / games (last 15 games)
hist_sb_rate = stolen_bases / games (last 15 games)
hist_bb_rate = walks / plate_appearances (last 15 games)
hist_so_rate = strikeouts / plate_appearances (last 15 games)

# Recent Form (Last 5 Games)
recent_batting_avg = hits / at_bats (last 5 games)
recent_hr_rate = home_runs / games (last 5 games)
recent_hot_streak = games_with_hit / 5 (last 5 games)

# Consistency Metrics
batting_avg_std = std(game_batting_avg, last 15 games)
hr_consistency = games_with_hr / 15 (last 15 games)
```

#### **Pitchers (P)**
```python
# Historical Performance (Last N Starts)
hist_era = earned_runs / innings_pitched (last 10 starts)
hist_whip = (walks + hits) / innings_pitched (last 10 starts)
hist_k_rate = strikeouts / innings_pitched (last 10 starts)
hist_ip_per_start = innings_pitched / starts (last 10 starts)
hist_win_rate = wins / starts (last 10 starts)

# Recent Form (Last 3 Starts)  
recent_era = earned_runs / innings_pitched (last 3 starts)
recent_k_rate = strikeouts / innings_pitched (last 3 starts)
recent_quality_starts = quality_starts / 3 (last 3 starts)

# Role-Specific (SP vs RP)
if starter: use starts-based windows
if reliever: use appearances-based windows, save opportunities
```

### **Feature Engineering Rules**

#### **Temporal Safety**
- **Never use same-game stats**: Features from games 1-(N-1) to predict game N
- **Minimum history**: Require 10 games for position players, 5 starts for pitchers
- **Rolling windows**: Always chronologically ordered, no future contamination
- **Missing data**: Use career averages for insufficient history periods

#### **Position-Specific Logic**
```python
def get_position_features(position, game_logs):
    if position == 'P':
        return calculate_pitcher_features(game_logs)
    elif position in ['C', '1B', '2B', '3B', 'SS', 'OF']:
        return calculate_batter_features(game_logs)
    else:
        raise ValueError(f"Unknown position: {position}")
```

---

## ⏰ **3. Temporal Validation Framework**

### **Strict Temporal Ordering**
```python
# Data Splitting Strategy
def create_temporal_splits(player_game_logs):
    # Sort by date (critical!)
    games = player_game_logs.sort_values('Date')
    
    # Skip first 10 games (insufficient history)
    valid_games = games.iloc[10:]
    
    # 80/20 temporal split per player
    split_idx = int(len(valid_games) * 0.8)
    train_games = valid_games.iloc[:split_idx]
    test_games = valid_games.iloc[split_idx:]
    
    return train_games, test_games
```

### **Cross-Validation Approach**
- **Method**: TimeSeriesSplit with 3 folds
- **Gap**: 5-game gap between train/validation to prevent leakage
- **Expanding Window**: Each fold uses all previous data for training

### **Cold Start Handling**
- **First 10 games**: Use league averages by position
- **Games 11-20**: Blend individual history (70%) + league averages (30%)
- **Games 21+**: Use full individual historical features

### **Validation Checks**
```python
def validate_temporal_integrity(features_df):
    # Ensure no future data contamination
    for idx, row in features_df.iterrows():
        game_date = row['game_date']
        feature_data_cutoff = row['feature_cutoff_date']
        assert feature_data_cutoff < game_date, "Data leakage detected!"
```

---

## 🏷️ **4. Position Mapping System**

### **Position Hierarchy**
```python
POSITION_MAPPING = {
    # Primary positions
    'C': 'C',           # Catcher
    '1B': '1B',         # First Base  
    '2B': '2B',         # Second Base
    '3B': '3B',         # Third Base
    'SS': 'SS',         # Shortstop
    'OF': 'OF',         # Outfield (LF, CF, RF combined)
    'P': 'P',           # Pitcher
    
    # Outfield consolidation
    'LF': 'OF',
    'CF': 'OF', 
    'RF': 'OF',
    
    # Designated hitter
    'DH': 'OF',         # Treat as OF for modeling purposes
}
```

### **Position Detection Strategy**
1. **Manual Mapping Table**: Pre-defined for top 200 players
2. **Game Log Analysis**: Infer from most frequent position in logs
3. **Fallback Rules**: Default unknown batters to 'OF', pitchers to 'P'

### **Multi-Position Players**
- **Primary Position**: Most games played at that position
- **Minimum Threshold**: 20+ games to qualify for position-specific model
- **Flexibility**: Allow players in multiple position models if they qualify

---

## 🎯 **5. Fantasy Scoring & Target Definition**

### **Fantasy Point Calculation**

#### **Position Players**
```python
def calculate_batter_fantasy_points(game_stats):
    points = (
        game_stats['H'] * 1 +           # Singles, doubles, triples
        game_stats['2B'] * 1 +          # Extra base bonus  
        game_stats['3B'] * 2 +          # Extra base bonus
        game_stats['HR'] * 4 +          # Home runs
        game_stats['RBI'] * 2 +         # RBI
        game_stats['R'] * 2 +           # Runs scored
        game_stats['SB'] * 2 +          # Stolen bases
        game_stats['BB'] * 1            # Walks
    )
    return points
```

#### **Pitchers**
```python
def calculate_pitcher_fantasy_points(game_stats):
    points = (
        game_stats['W'] * 10 +          # Wins
        game_stats['SV'] * 10 +         # Saves  
        game_stats['SO'] * 1 +          # Strikeouts
        game_stats['IP'] * 3            # Innings pitched
    )
    
    # ERA bonuses
    if game_stats['IP'] >= 5:  # Minimum 5 IP
        game_era = game_stats['ER'] / game_stats['IP'] * 9
        if game_era <= 2.00:
            points += 5
        elif game_era <= 3.00:
            points += 2
    
    return points
```

### **Missing Data Handling**
- **Imputation Strategy**: Use 0 for counting stats, position averages for rates
- **Quality Gates**: Require minimum plate appearances (2+) or innings pitched (1+)
- **Outlier Capping**: Cap extreme performances (50+ fantasy points)

---

## 🏗️ **6. System Architecture & Data Flow**

### **Complete Pipeline**
```
Raw Data Collection
├── Player Discovery (batting_stats_bref, pitching_stats_bref)
├── ID Mapping (playerid_lookup)
├── Game Log Extraction (season_game_logs)
└── Position Assignment (manual + inference)
        ↓
Historical Feature Engineering  
├── Rolling Statistics Calculation
├── Temporal Validation Checks
├── Position-Specific Features
└── Target Variable Calculation
        ↓
Model Training Pipeline
├── Temporal Train/Test Splits
├── Position-Specific Models
├── TimeSeriesSplit Cross-Validation
└── Model Persistence
        ↓
Inference & Validation
├── New Game Predictions
├── Performance Monitoring
├── Data Drift Detection
└── Model Retraining Triggers
```

### **File Structure**
```
mlb_prediction_system/
├── data/
│   ├── raw/                    # Cached API responses
│   ├── processed/              # Feature-engineered datasets
│   └── positions/              # Position mapping tables
├── src/
│   ├── data_collection.py      # API interaction & caching
│   ├── feature_engineering.py  # Historical feature calculation
│   ├── temporal_validation.py  # Leakage prevention
│   ├── position_mapping.py     # Position assignment logic
│   ├── fantasy_scoring.py      # Target variable calculation
│   └── model_training.py       # ML pipeline
├── models/                     # Trained model artifacts
├── config/                     # Configuration files
└── tests/                      # Unit & integration tests
```

---

## 🎯 **7. Performance Expectations & Validation**

### **Realistic Benchmarks**
```python
PERFORMANCE_TARGETS = {
    'position_players': {
        'mae': 6.0,           # Mean Absolute Error
        'r2': 0.35,           # R-squared
        'within_5pts': 0.45,  # % predictions within 5 points
        'perfect': 0.02       # % perfect predictions
    },
    'pitchers': {
        'mae': 8.0,           # Higher volatility
        'r2': 0.25,           # Lower predictability  
        'within_8pts': 0.40,  # % predictions within 8 points
        'perfect': 0.01       # % perfect predictions
    }
}
```

### **Model Validation Framework**
- **Temporal Cross-Validation**: 3-fold TimeSeriesSplit
- **Position-Specific Metrics**: Separate evaluation per position
- **Outlier Analysis**: Track predictions >20 points error
- **Consistency Checks**: Monitor prediction variance over time

---

## 🚨 **8. Risk Mitigation & Failure Points**

### **Potential Failure Points**
1. **API Rate Limiting**: pybaseball blocks excessive requests
2. **Missing Game Logs**: Players with insufficient data
3. **Position Changes**: Mid-season position switches
4. **Data Quality**: Inconsistent stat reporting
5. **Model Drift**: Performance degradation over time

### **Mitigation Strategies**
1. **Robust Caching**: Never re-fetch existing data
2. **Graceful Degradation**: Continue with available players
3. **Position Flexibility**: Multi-position model eligibility
4. **Data Validation**: Sanity checks on all statistics
5. **Monitoring Pipeline**: Track model performance metrics

---

## 🛣️ **9. Implementation Roadmap**

### **Phase 1: Foundation (Week 1)**
- [ ] Data collection infrastructure
- [ ] Position mapping system  
- [ ] Basic feature engineering
- [ ] Temporal validation framework

### **Phase 2: Core System (Week 2)**
- [ ] Complete feature engineering pipeline
- [ ] Fantasy scoring implementation
- [ ] Model training infrastructure
- [ ] Initial model validation

### **Phase 3: Production Ready (Week 3)**
- [ ] Error handling & robustness
- [ ] Performance monitoring
- [ ] Inference pipeline
- [ ] Documentation & testing

### **Success Metrics**
- ✅ Zero data leakage (validated by temporal checks)
- ✅ 200+ players with sufficient data
- ✅ Position-specific models for all positions
- ✅ Realistic performance metrics achieved
- ✅ Robust error handling implemented

---

## 📋 **10. Technical Specifications**

### **Dependencies**
```python
# Core libraries
pandas >= 1.5.0
numpy >= 1.21.0
scikit-learn >= 1.1.0
pybaseball >= 2.2.0

# Optional enhancements  
joblib >= 1.1.0        # Model persistence
tqdm >= 4.64.0         # Progress tracking
```

### **Configuration Management**
```python
# config/settings.py
HISTORICAL_WINDOW = 15      # Games for historical features
RECENT_WINDOW = 5           # Games for recent form
MIN_GAMES_REQUIRED = 10     # Minimum games for predictions
RATE_LIMIT_DELAY = 2.0      # Seconds between API calls
CACHE_EXPIRY_DAYS = 7       # Cache refresh frequency
```

### **Data Quality Standards**
- **Completeness**: >90% of expected games per player
- **Accuracy**: Sanity checks on all statistical ranges
- **Consistency**: Temporal ordering validated
- **Freshness**: Data updated within 24 hours

---

This architecture ensures we build a production-ready, leak-free MLB prediction system that follows all 5 rules and delivers realistic, actionable predictions for fantasy baseball. 