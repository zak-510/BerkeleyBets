# MLB System - Key Design Decisions Summary

## 🎯 **Critical Design Decisions Made**

### **1. Data Collection Strategy** ✅
- **Primary Source**: `pybaseball.season_game_logs()` for game-level data
- **Player Discovery**: `batting_stats_bref()` + `pitching_stats_bref()` + `playerid_lookup()`
- **Rate Limiting**: 2 seconds between requests (conservative)
- **Caching**: Local CSV files by player/year to avoid re-fetching
- **Historical Depth**: 2019-2024 (5 seasons for robust training)

### **2. Temporal Validation Framework** ✅
- **Zero Leakage Rule**: Features from games 1-(N-1) to predict game N
- **Minimum History**: 10 games for batters, 5 starts for pitchers
- **Train/Test Split**: 80/20 temporal split per player
- **Cross-Validation**: TimeSeriesSplit with 3 folds + 5-game gaps
- **Cold Start**: League averages for first 10 games

### **3. Feature Engineering Architecture** ✅
- **Historical Windows**: 15 games (batters), 10 starts (pitchers)
- **Recent Form**: 5 games (batters), 3 starts (pitchers)
- **Feature Types**: Rates not totals (HR/game not season HRs)
- **Position-Specific**: Different features for batters vs pitchers
- **No Same-Game Stats**: Never use game N stats to predict game N

### **4. Position Mapping System** ✅
- **Consolidation**: LF/CF/RF → OF, DH → OF
- **Core Positions**: C, 1B, 2B, 3B, SS, OF, P (7 total)
- **Detection Method**: Manual mapping + game log inference
- **Multi-Position**: Allow if 20+ games at position
- **Fallback**: Unknown batters → OF, pitchers → P

### **5. Fantasy Scoring Definition** ✅
- **Batter Points**: H(1) + 2B(1) + 3B(2) + HR(4) + RBI(2) + R(2) + SB(2) + BB(1)
- **Pitcher Points**: W(10) + SV(10) + SO(1) + IP(3) + ERA bonuses
- **Target Range**: 5-25 points typical, 50+ point cap
- **Missing Data**: 0 for counting stats, position averages for rates

## 🔄 **Data Pipeline Flow**

```
Player Discovery → ID Lookup → Game Logs → Feature Engineering → Model Training
     ↓              ↓           ↓              ↓                    ↓
batting_stats   playerid_   season_game_   Rolling averages   Position-specific
pitching_stats   lookup()     logs()        (15/10 games)      RandomForest
```

## 📊 **Performance Expectations**

| Metric | Position Players | Pitchers |
|--------|-----------------|----------|
| **MAE** | 6.0 points | 8.0 points |
| **R²** | 0.35 | 0.25 |
| **Within Range** | 45% (±5 pts) | 40% (±8 pts) |
| **Perfect Predictions** | 2% | 1% |

## ⚠️ **Key Risk Mitigations**

1. **API Rate Limiting** → Aggressive caching + 2-second delays
2. **Missing Data** → Graceful degradation + continue with available
3. **Data Leakage** → Temporal validation checks + feature cutoff dates
4. **Position Changes** → Multi-position eligibility + 20-game thresholds
5. **Model Drift** → Performance monitoring + retraining triggers

## 🎯 **Implementation Priority**

**Phase 1** (Foundation): Data collection + caching + temporal validation
**Phase 2** (Core): Feature engineering + model training + position mapping  
**Phase 3** (Production): Error handling + monitoring + inference pipeline

## ✅ **Validation Checkpoints**

- [ ] Can fetch game logs for 200+ players
- [ ] Temporal validation passes (no future data contamination)
- [ ] Position assignment works for all player types
- [ ] Feature engineering produces realistic ranges
- [ ] Model performance meets benchmarks (R² 0.25-0.35)
- [ ] System handles missing data gracefully

This design ensures we build a **leak-free, production-ready MLB prediction system** that follows all 5 rules and delivers honest, actionable predictions. 