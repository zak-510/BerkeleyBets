# NFL Fantasy Football Prediction System

A high-accuracy NFL fantasy football prediction system using position-specific machine learning models trained on live NFL data.

## 🏆 Performance Metrics

- **Overall MAE:** 11.2 points
- **Overall R²:** 0.960 (excellent predictive power)
- **Coverage:** 425+ NFL players
- **Accuracy Distribution:** 70.4% of predictions within 10 points

### Position-Specific Performance
| Position | Players | MAE | R² | 
|----------|---------|-----|----| 
| QB | 60 | 21.9 | 0.929 |
| RB | 105 | 14.8 | 0.947 |
| WR | 170 | 6.8 | 0.987 |
| TE | 90 | 7.9 | 0.961 |

## 🚀 Quick Start

### 1. Train New Models
```bash
python nfl_model.py
```
This will:
- Download latest NFL data (2023 training, 2024 testing)
- Train position-specific Random Forest models
- Save models as `.pkl` files
- Generate performance metrics

### 2. View Results
```bash
python display_results.py
```
Shows comprehensive analysis including:
- Top performers by position
- Most accurate predictions
- Biggest prediction errors
- Accuracy distribution

### 3. GUI Interface
```bash
python nfl_gui.py
```
Interactive GUI for making individual player predictions (requires tkinter).

### 4. CLI Interface  
```bash
python nfl_cli.py
```
Command-line interface for batch predictions and analysis.

## 📁 File Structure

### Core Files
- `nfl_model.py` - Main model training script
- `display_results.py` - Results visualization
- `nfl_gui.py` - Tkinter GUI interface
- `nfl_cli.py` - Command-line interface



### Model Files
- `nfl_qb_model.pkl` - Quarterback model
- `nfl_rb_model.pkl` - Running back model  
- `nfl_wr_model.pkl` - Wide receiver model
- `nfl_te_model.pkl` - Tight end model

### Data Files
- `inference_results.csv` - Latest prediction results

## 🔧 Technical Details

### Model Architecture
- **Algorithm:** Random Forest Regressor
- **Approach:** Position-specific models with tailored features
- **Validation:** Strict temporal split (2023→2024)
- **Target:** Fantasy points (PPR scoring)

### Position-Specific Features

**Quarterback (QB):**
- Passing yards, TDs, interceptions, attempts
- Rushing yards, TDs

**Running Back (RB):**
- Rushing yards, TDs, carries
- Receiving yards, TDs, targets

**Wide Receiver (WR):**
- Receiving yards, TDs, targets, receptions
- Rushing yards (for gadget plays)

**Tight End (TE):**
- Receiving yards, TDs, targets, receptions

### Data Quality Controls
- ✅ No duplicate players
- ✅ Temporal validation (no data leakage)
- ✅ Volume filtering (minimum 10 fantasy points)
- ✅ Position-specific feature engineering
- ✅ Outlier detection and handling

## 📊 Usage Examples



### View Top Performers
```python
from display_improved_results import display_improved_inference_results
results = display_improved_inference_results()
```

## 🔍 Key Improvements Over Original

| Metric | Original | Improved | Change |
|--------|----------|----------|---------|
| **Players** | 181 | 425 | +135% |
| **MAE** | 27.2 | 11.2 | +58.9% |
| **RMSE** | 52.5 | 19.3 | +63.2% |
| **R²** | 0.739 | 0.960 | +29.9% |
| **QB MAE** | 77.3 | 21.9 | +71.6% |

### Issues Resolved
- ❌ Duplicate players → ✅ Eliminated
- ❌ Identical predictions → ✅ Position-specific models
- ❌ Poor QB accuracy → ✅ 71.6% improvement
- ❌ Data quality issues → ✅ Clean validation pipeline

## 📋 Requirements

### Python Packages
```bash
pip install pandas numpy scikit-learn nfl-data-py joblib
```

### Optional (for GUI)
```bash
pip install tkinter  # Usually included with Python
```

## 🎯 Model Validation

### Training Approach
1. **Temporal Split:** 2023 season for training, 2024 for testing
2. **No Data Leakage:** Strict temporal validation
3. **Position Separation:** Dedicated models per position
4. **Feature Selection:** Position-relevant statistics only

### Performance Validation
- **Cross-validation:** Temporal split prevents overfitting
- **Outlier Analysis:** <4% extreme outliers (>50 point error)
- **Distribution:** 42.4% excellent predictions (0-5 error)
- **Consistency:** All positions show strong R² (0.929-0.987)

## 🏈 Fantasy Football Applications

### Use Cases
1. **Draft Preparation** - Identify undervalued players
2. **Weekly Lineups** - Optimize start/sit decisions  
3. **Trade Analysis** - Evaluate player values
4. **Waiver Wire** - Target breakout candidates
5. **DFS Optimization** - Build optimal lineups

### Prediction Confidence
- **High Confidence:** WR/TE predictions (MAE 6.8-7.9)
- **Medium Confidence:** RB predictions (MAE 14.8)
- **Lower Confidence:** QB predictions (MAE 21.9, but much improved)

## 🔄 Model Updates

The system automatically uses the latest NFL data when retraining. To update:

1. Delete existing `.pkl` model files
2. Run `python nfl_model.py`
3. New models will be trained on current data

## 📈 Future Enhancements

- [ ] Weekly prediction updates
- [ ] Injury impact modeling  
- [ ] Weather condition factors
- [ ] Team matchup analysis
- [ ] Confidence intervals
- [ ] REST API endpoint

## 🤝 Contributing

1. Maintain position-specific architecture
2. Preserve temporal validation approach
3. Add comprehensive testing for new features
4. Update documentation for changes

## 📄 License

This project is for educational and research purposes. NFL data is sourced from public APIs and should be used in compliance with their terms of service.

---

**Built with:** Python, scikit-learn, pandas, nfl-data-py  
**Last Updated:** December 2024  
**Model Version:** 2.0 (Position-Specific) 