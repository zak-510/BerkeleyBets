#!/usr/bin/env python3
"""
Train Rate-Based Batter Models
Instead of predicting individual game stats, predict likely performance rates
then convert to expected game stats
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RateBasedBatterModels:
    """Train models to predict performance rates, then convert to game stats"""
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.models = {}
        self.scalers = {}
        self.performance = {}
        
        # Rate stats to predict (more predictable than counting stats)
        self.rate_stats = {
            'batting_avg': {'target_col': 'AVG', 'min_val': 0.100, 'max_val': 0.450},
            'on_base_pct': {'target_col': 'OBP', 'min_val': 0.200, 'max_val': 0.500},
            'slugging_pct': {'target_col': 'SLG', 'min_val': 0.200, 'max_val': 0.800},
            'walk_rate': {'derived': 'BB_rate', 'min_val': 0.00, 'max_val': 0.25},
            'strikeout_rate': {'derived': 'K_rate', 'min_val': 0.05, 'max_val': 0.45},
            'home_run_rate': {'derived': 'HR_rate', 'min_val': 0.00, 'max_val': 0.15},
            'steal_rate': {'derived': 'SB_rate', 'min_val': 0.00, 'max_val': 0.30}
        }
    
    def load_and_prepare_data(self):
        """Load and prepare rate-based training data"""
        print(f"📊 Loading data from: {self.data_file}")
        data = pd.read_csv(self.data_file)
        
        # Filter to batters with sufficient playing time
        batter_data = data[
            (data['player_type'] == 'batter') & 
            (data['G'] >= 50) &  # At least 50 games
            (data['AB'] >= 100)  # At least 100 at-bats
        ].copy()
        
        print(f"⚾ Qualified batters: {len(batter_data)}")
        
        if len(batter_data) < 50:
            print("❌ Insufficient qualified batter data")
            return None
        
        # Calculate derived rates
        for _, row in batter_data.iterrows():
            pa = row.get('PA', row.get('AB', 0) + row.get('BB', 0))
            ab = row.get('AB', 0)
            games = row.get('G', 1)
            
            # Calculate rates
            batter_data.loc[batter_data.index == _, 'BB_rate'] = row.get('BB', 0) / max(1, pa)
            batter_data.loc[batter_data.index == _, 'K_rate'] = row.get('SO', 0) / max(1, pa)
            batter_data.loc[batter_data.index == _, 'HR_rate'] = row.get('HR', 0) / max(1, ab)
            batter_data.loc[batter_data.index == _, 'SB_rate'] = row.get('SB', 0) / max(1, games)
        
        # Add contextual features
        for _, row in batter_data.iterrows():
            # Age-based features
            age = 2024 - row.get('season', 2024) + 27  # Estimate age
            batter_data.loc[batter_data.index == _, 'player_age'] = age
            batter_data.loc[batter_data.index == _, 'age_factor'] = 1.0 if 25 <= age <= 30 else 0.8
            
            # Experience proxy
            batter_data.loc[batter_data.index == _, 'games_played'] = row.get('G', 0)
            batter_data.loc[batter_data.index == _, 'playing_time_factor'] = min(1.0, row.get('G', 0) / 140)
            
            # Performance tier
            ops = row.get('OBP', 0.300) + row.get('SLG', 0.400)
            if ops >= 0.900:
                tier = 'elite'
            elif ops >= 0.800:
                tier = 'above_average'
            elif ops >= 0.700:
                tier = 'average'
            else:
                tier = 'below_average'
            batter_data.loc[batter_data.index == _, 'performance_tier'] = tier
        
        print(f"✅ Prepared rate-based training data: {len(batter_data)} players")
        return batter_data
    
    def train_rate_models(self, data):
        """Train models to predict performance rates"""
        print("\n🎯 Training rate-based models...")
        
        # Features for rate prediction
        features = [
            'player_age',
            'age_factor',
            'games_played',
            'playing_time_factor',
            'G',  # Games played
            'AB',  # At-bats
            'PA'   # Plate appearances
        ]
        
        # Add league context features if available
        if 'season' in data.columns:
            features.append('season')
        
        # One-hot encode performance tier
        tier_dummies = pd.get_dummies(data['performance_tier'], prefix='tier')
        feature_data = data[features].copy()
        feature_data = pd.concat([feature_data, tier_dummies], axis=1)
        
        # Train a model for each rate stat
        for rate_name, rate_info in self.rate_stats.items():
            try:
                if 'target_col' in rate_info:
                    # Direct column (AVG, OBP, SLG)
                    target = data[rate_info['target_col']].fillna(0.250)
                else:
                    # Derived rate
                    target = data[rate_info['derived']].fillna(0.1)
                
                # Clean target values
                target = target.clip(rate_info['min_val'], rate_info['max_val'])
                
                # Remove missing data
                valid_mask = ~(feature_data.isnull().any(axis=1) | target.isnull())
                X_clean = feature_data[valid_mask].fillna(0)
                y_clean = target[valid_mask]
                
                if len(X_clean) < 30:
                    print(f"⚠️ Insufficient data for {rate_name}: {len(X_clean)} samples")
                    continue
                
                # Train/test split
                split_point = int(len(X_clean) * 0.8)
                X_train = X_clean.iloc[:split_point]
                X_test = X_clean.iloc[split_point:]
                y_train = y_clean.iloc[:split_point]
                y_test = y_clean.iloc[split_point:]
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Try multiple algorithms
                algorithms = [
                    ('RandomForest', RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)),
                    ('Ridge', Ridge(alpha=1.0, random_state=42))
                ]
                
                best_model = None
                best_r2 = -999
                best_mae = 999
                best_name = ""
                
                for name, model in algorithms:
                    try:
                        model.fit(X_train_scaled, y_train)
                        y_pred = model.predict(X_test_scaled)
                        
                        # Clip predictions to valid range
                        y_pred = np.clip(y_pred, rate_info['min_val'], rate_info['max_val'])
                        
                        r2 = r2_score(y_test, y_pred)
                        mae = mean_absolute_error(y_test, y_pred)
                        
                        if r2 > best_r2:
                            best_model = model
                            best_r2 = r2
                            best_mae = mae
                            best_name = name
                            
                    except Exception as e:
                        print(f"  {name} failed for {rate_name}: {e}")
                        continue
                
                if best_model is None:
                    print(f"❌ All algorithms failed for {rate_name}")
                    continue
                
                # Train final model on all data
                X_all_scaled = scaler.fit_transform(X_clean)
                best_model.fit(X_all_scaled, y_clean)
                
                # Store results
                self.models[f'rate_{rate_name}'] = best_model
                self.scalers[f'rate_{rate_name}'] = scaler
                self.performance[f'rate_{rate_name}'] = {
                    'r2': max(0.0, best_r2),
                    'mae': best_mae,
                    'n_samples': len(X_clean),
                    'n_features': len(X_clean.columns),
                    'features': list(X_clean.columns),
                    'algorithm': best_name.lower(),
                    'created': datetime.now().isoformat(),
                    'target_range': f"{y_clean.min():.3f}-{y_clean.max():.3f}",
                    'valid_range': f"{rate_info['min_val']:.3f}-{rate_info['max_val']:.3f}"
                }
                
                print(f"  ✅ {rate_name}: {best_name} R² = {max(0.0, best_r2):.3f}, MAE = {best_mae:.3f}")
                
            except Exception as e:
                print(f"❌ Failed to train {rate_name}: {e}")
                continue
    
    def save_models(self):
        """Save rate-based models"""
        if not self.models:
            print("❌ No models to save!")
            return None
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_dir = f"rate_based_batter_models_{timestamp}"
        os.makedirs(model_dir, exist_ok=True)
        
        # Save models
        for model_name, model in self.models.items():
            model_file = os.path.join(model_dir, f"{model_name}_model.pkl")
            scaler_file = os.path.join(model_dir, f"{model_name}_scaler.pkl")
            
            joblib.dump(model, model_file)
            joblib.dump(self.scalers[model_name], scaler_file)
        
        # Save performance metrics
        perf_file = os.path.join(model_dir, 'rate_based_performance.json')
        with open(perf_file, 'w') as f:
            json.dump(self.performance, f, indent=2)
        
        # Create conversion utility
        converter_code = '''
def convert_rates_to_game_stats(rates, plate_appearances=4.0, at_bats=3.5):
    """Convert predicted rates to expected per-game stats"""
    game_stats = {}
    
    # Hits per game
    game_stats['hits'] = max(0, round(rates.get('batting_avg', 0.250) * at_bats))
    
    # Walks per game  
    game_stats['walks'] = max(0, round(rates.get('walk_rate', 0.08) * plate_appearances))
    
    # Strikeouts per game
    game_stats['strikeouts'] = max(0, round(rates.get('strikeout_rate', 0.20) * plate_appearances))
    
    # Home runs per game
    game_stats['home_runs'] = max(0, round(rates.get('home_run_rate', 0.03) * at_bats))
    
    # Stolen bases per game (rare)
    game_stats['stolen_bases'] = max(0, round(rates.get('steal_rate', 0.05)))
    
    # Estimate other stats from hits and performance
    hits = game_stats['hits']
    slg = rates.get('slugging_pct', 0.400)
    avg = rates.get('batting_avg', 0.250)
    
    # Doubles (typically 20-25% of hits for average players)
    game_stats['doubles'] = max(0, round(hits * 0.22))
    
    # Triples (very rare, ~1% of hits)
    game_stats['triples'] = 1 if hits >= 3 and np.random.random() < 0.01 else 0
    
    # Runs and RBIs (correlated with overall offensive performance)
    ops = rates.get('on_base_pct', 0.320) + slg
    if ops >= 0.850:
        run_rbi_factor = 1.2
    elif ops >= 0.750:
        run_rbi_factor = 1.0
    else:
        run_rbi_factor = 0.8
    
    game_stats['runs'] = max(0, round((hits + game_stats['walks']) * 0.3 * run_rbi_factor))
    game_stats['rbis'] = max(0, round(hits * 0.4 * run_rbi_factor))
    
    return game_stats
'''
        
        converter_file = os.path.join(model_dir, 'rate_to_stats_converter.py')
        with open(converter_file, 'w') as f:
            f.write(converter_code)
        
        print(f"\n✅ Rate-based models saved to: {model_dir}")
        print(f"📊 Total models created: {len(self.models)}")
        
        # Performance summary
        print(f"\n📈 RATE-BASED MODEL PERFORMANCE:")
        print("-" * 60)
        
        for model_name, perf in self.performance.items():
            rate_name = model_name.replace('rate_', '')
            print(f"  {rate_name}: R² = {perf['r2']:.3f}, MAE = {perf['mae']:.3f} ({perf['algorithm']})")
        
        return model_dir

def main():
    """Main training workflow"""
    print("🚀 TRAINING RATE-BASED BATTER MODELS")
    print("=" * 60)
    
    data_file = 'mlb_data_full_seasons/combined_data/mlb_complete_2023_2024.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ Training data not found: {data_file}")
        return False
    
    # Initialize trainer
    trainer = RateBasedBatterModels(data_file)
    
    # Load and prepare data
    training_data = trainer.load_and_prepare_data()
    
    if training_data is None:
        return False
    
    # Train rate models
    trainer.train_rate_models(training_data)
    
    # Save models
    model_dir = trainer.save_models()
    
    if model_dir:
        print(f"\n🎉 Rate-based model training completed!")
        print(f"📁 Models saved to: {model_dir}")
        print(f"\n💡 These models predict performance rates (AVG, OBP, etc.)")
        print(f"   Use the converter to translate rates to expected game stats")
        return True
    else:
        print(f"\n❌ Rate-based model training failed")
        return False

if __name__ == "__main__":
    main()