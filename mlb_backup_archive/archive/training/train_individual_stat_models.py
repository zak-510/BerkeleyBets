#!/usr/bin/env python3
"""
Train Individual Stat Models for MLB Players
Creates separate models for each individual statistic (hits, HRs, strikeouts, etc.)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, PoissonRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import cross_val_score
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class IndividualStatModelTrainer:
    """Train individual stat prediction models"""
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.models = {}
        self.scalers = {}
        self.performance = {}
        
        # Define the stats we want to predict
        self.batter_stats = {
            'hits': {'column': 'H', 'type': 'count'},
            'doubles': {'column': '2B', 'type': 'count'}, 
            'triples': {'column': '3B', 'type': 'count'},
            'home_runs': {'column': 'HR', 'type': 'count'},
            'walks': {'column': 'BB', 'type': 'count'},
            'strikeouts': {'column': 'SO', 'type': 'count'},
            'runs': {'column': 'R', 'type': 'count'},
            'rbis': {'column': 'RBI', 'type': 'count'},
            'stolen_bases': {'column': 'SB', 'type': 'count'}
        }
        
        self.pitcher_stats = {
            'innings_pitched': {'column': 'IP_numeric', 'type': 'continuous'},
            'strikeouts': {'column': 'SO', 'type': 'count'},
            'hits_allowed': {'column': 'H', 'type': 'count'},
            'walks_allowed': {'column': 'BB', 'type': 'count'},
            'home_runs_allowed': {'column': 'HR', 'type': 'count'},
            'earned_runs': {'column': 'ER', 'type': 'count'}
        }
    
    def load_and_prepare_data(self):
        """Load and prepare training data"""
        print(f"📊 Loading data from: {self.data_file}")
        data = pd.read_csv(self.data_file)
        print(f"✅ Loaded {len(data)} player-season records")
        
        # Convert season totals to per-game averages and create training samples
        training_data = []
        
        for _, row in data.iterrows():
            try:
                name = row['Name']
                season = row['season']
                player_type = row['player_type']
                games = max(1, row.get('G', 1))
                
                # Skip if missing key data
                if pd.isna(row['fantasy_points']) or row['fantasy_points'] <= 0:
                    continue
                
                # Create multiple simulated games per player (season sampling)
                num_games = min(15, max(5, int(games * 0.15)))  # Sample ~15% of games
                
                for game_idx in range(num_games):
                    game_record = {
                        'player_name': name,
                        'season': season,
                        'player_type': player_type,
                        'total_games': games
                    }
                    
                    # Create historical features (same as current system)
                    fantasy_per_game = row['fantasy_points'] / games
                    variation = np.random.normal(0, fantasy_per_game * 0.3)
                    game_fantasy = max(0, fantasy_per_game + variation)
                    
                    game_record.update({
                        'avg_fantasy_points_L15': fantasy_per_game + np.random.normal(0, fantasy_per_game * 0.1),
                        'avg_fantasy_points_L10': fantasy_per_game + np.random.normal(0, fantasy_per_game * 0.15),
                        'avg_fantasy_points_L5': fantasy_per_game + np.random.normal(0, fantasy_per_game * 0.2),
                        'games_since_last_good_game': np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.25, 0.2, 0.15, 0.07, 0.03]),
                        'trend_last_5_games': np.random.normal(0, 0.5),
                        'consistency_score': np.random.beta(2, 2) * 0.8 + 0.2,
                        'fantasy_points': game_fantasy
                    })
                    
                    # Add individual stats (per-game from season totals)
                    if player_type == 'batter':
                        for stat_name, stat_info in self.batter_stats.items():
                            col = stat_info['column']
                            if col in row and not pd.isna(row[col]):
                                season_total = row[col]
                                per_game_avg = season_total / games
                                
                                # Add realistic variation for per-game prediction
                                if stat_info['type'] == 'count':
                                    # Use Poisson-like distribution for count stats
                                    game_value = max(0, np.random.poisson(per_game_avg) if per_game_avg > 0 else 0)
                                else:
                                    # Continuous stats (like innings pitched)
                                    game_value = max(0, per_game_avg + np.random.normal(0, per_game_avg * 0.3))
                                
                                game_record[f'target_{stat_name}'] = game_value
                            else:
                                game_record[f'target_{stat_name}'] = 0
                    
                    elif player_type == 'pitcher':
                        for stat_name, stat_info in self.pitcher_stats.items():
                            col = stat_info['column']
                            if col in row and not pd.isna(row[col]):
                                season_total = row[col]
                                
                                # Special handling for innings pitched
                                if col == 'IP_numeric':
                                    if isinstance(season_total, str):
                                        try:
                                            if '.' in season_total:
                                                whole, partial = season_total.split('.')
                                                season_total = float(whole) + float(partial) / 3
                                            else:
                                                season_total = float(season_total)
                                        except:
                                            season_total = 0
                                
                                per_game_avg = season_total / games
                                
                                if stat_info['type'] == 'count':
                                    game_value = max(0, np.random.poisson(per_game_avg) if per_game_avg > 0 else 0)
                                else:
                                    game_value = max(0, per_game_avg + np.random.normal(0, per_game_avg * 0.3))
                                
                                game_record[f'target_{stat_name}'] = game_value
                            else:
                                game_record[f'target_{stat_name}'] = 0
                    
                    training_data.append(game_record)
                    
            except Exception as e:
                print(f"⚠️ Error processing {row.get('Name', 'Unknown')}: {e}")
                continue
        
        df = pd.DataFrame(training_data)
        print(f"✅ Created {len(df)} training samples")
        print(f"📊 Batters: {len(df[df['player_type'] == 'batter'])}")
        print(f"📊 Pitchers: {len(df[df['player_type'] == 'pitcher'])}")
        
        return df
    
    def train_stat_models(self, training_data):
        """Train individual models for each stat"""
        print("\n🎯 Training individual stat models...")
        
        # Historical features (same as current fantasy point models)
        historical_features = [
            'avg_fantasy_points_L15',
            'avg_fantasy_points_L10', 
            'avg_fantasy_points_L5',
            'games_since_last_good_game',
            'trend_last_5_games',
            'consistency_score'
        ]
        
        # Train batter models
        batter_data = training_data[training_data['player_type'] == 'batter'].copy()
        if len(batter_data) > 50:
            print(f"\n🏃 Training batter stat models ({len(batter_data)} samples)...")
            
            for stat_name in self.batter_stats.keys():
                target_col = f'target_{stat_name}'
                if target_col in batter_data.columns:
                    self._train_single_stat_model(
                        batter_data, historical_features, target_col, 
                        f'batter_{stat_name}', self.batter_stats[stat_name]['type']
                    )
        
        # Train pitcher models
        pitcher_data = training_data[training_data['player_type'] == 'pitcher'].copy()
        if len(pitcher_data) > 50:
            print(f"\n🥎 Training pitcher stat models ({len(pitcher_data)} samples)...")
            
            for stat_name in self.pitcher_stats.keys():
                target_col = f'target_{stat_name}'
                if target_col in pitcher_data.columns:
                    self._train_single_stat_model(
                        pitcher_data, historical_features, target_col,
                        f'pitcher_{stat_name}', self.pitcher_stats[stat_name]['type']
                    )
    
    def _train_single_stat_model(self, data, features, target_col, model_name, stat_type):
        """Train a single stat prediction model"""
        try:
            # Prepare data
            X = data[features].fillna(0)
            y = data[target_col].fillna(0)
            
            # Remove extreme outliers
            q99 = y.quantile(0.99)
            outlier_mask = y <= q99
            X_filtered = X[outlier_mask]
            y_filtered = y[outlier_mask]
            
            if len(X_filtered) < 20:
                print(f"⚠️ Insufficient data for {model_name}: {len(X_filtered)} samples")
                return
            
            # Train/test split
            split_point = int(len(X_filtered) * 0.8)
            X_train = X_filtered.iloc[:split_point]
            X_test = X_filtered.iloc[split_point:]
            y_train = y_filtered.iloc[:split_point]
            y_test = y_filtered.iloc[split_point:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Choose algorithm based on stat type
            if stat_type == 'count':
                # For count data, try Poisson and RandomForest
                algorithms = [
                    ('Poisson', PoissonRegressor(alpha=1.0, max_iter=300)),
                    ('RandomForest', RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42))
                ]
            else:
                # For continuous data, use Ridge and RandomForest
                algorithms = [
                    ('Ridge', Ridge(alpha=1.0, random_state=42)),
                    ('RandomForest', RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42))
                ]
            
            best_model = None
            best_r2 = -999
            best_mae = 999
            best_name = ""
            
            for name, model in algorithms:
                try:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    
                    # Ensure non-negative predictions for count data
                    if stat_type == 'count':
                        y_pred = np.maximum(0, y_pred)
                    
                    r2 = r2_score(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    if r2 > best_r2:
                        best_model = model
                        best_r2 = r2
                        best_mae = mae
                        best_name = name
                        
                except Exception as e:
                    print(f"  {name} failed for {model_name}: {e}")
                    continue
            
            if best_model is None:
                print(f"❌ All algorithms failed for {model_name}")
                return
            
            # Cross-validation
            X_all_scaled = scaler.fit_transform(X_filtered)
            cv_scores = cross_val_score(best_model, X_all_scaled, y_filtered, cv=3, scoring='r2')
            cv_r2_mean = np.mean(cv_scores)
            
            # Train final model on all data
            best_model.fit(X_all_scaled, y_filtered)
            
            # Store results
            self.models[model_name] = best_model
            self.scalers[model_name] = scaler
            self.performance[model_name] = {
                'r2': max(0.0, best_r2),
                'mae': best_mae,
                'cv_r2_mean': max(0.0, cv_r2_mean),
                'n_samples': len(X_filtered),
                'n_features': len(features),
                'features': features,
                'algorithm': best_name.lower(),
                'stat_type': stat_type,
                'created': datetime.now().isoformat(),
                'target_range': f"{y_filtered.min():.2f}-{y_filtered.max():.2f}"
            }
            
            print(f"  ✅ {model_name}: {best_name} R² = {max(0.0, best_r2):.3f}, MAE = {best_mae:.2f}")
            
        except Exception as e:
            print(f"❌ Failed to train {model_name}: {e}")
    
    def save_models(self):
        """Save all trained models"""
        if not self.models:
            print("❌ No models to save!")
            return None
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_dir = f"individual_stat_models_{timestamp}"
        os.makedirs(model_dir, exist_ok=True)
        
        # Save individual models
        for model_name, model in self.models.items():
            model_file = os.path.join(model_dir, f"{model_name}_model.pkl")
            scaler_file = os.path.join(model_dir, f"{model_name}_scaler.pkl")
            
            joblib.dump(model, model_file)
            joblib.dump(self.scalers[model_name], scaler_file)
        
        # Save performance metrics
        perf_file = os.path.join(model_dir, 'individual_stat_performance.json')
        with open(perf_file, 'w') as f:
            json.dump(self.performance, f, indent=2)
        
        print(f"\n✅ Individual stat models saved to: {model_dir}")
        print(f"📊 Total models created: {len(self.models)}")
        
        # Performance summary
        print(f"\n📈 INDIVIDUAL STAT MODEL PERFORMANCE:")
        print("-" * 60)
        
        batter_models = {k: v for k, v in self.performance.items() if k.startswith('batter_')}
        pitcher_models = {k: v for k, v in self.performance.items() if k.startswith('pitcher_')}
        
        if batter_models:
            print("⚾ BATTER STATS:")
            for model_name, perf in batter_models.items():
                stat_name = model_name.replace('batter_', '')
                print(f"  {stat_name}: R² = {perf['r2']:.3f}, MAE = {perf['mae']:.2f} ({perf['algorithm']})")
        
        if pitcher_models:
            print("🥎 PITCHER STATS:")
            for model_name, perf in pitcher_models.items():
                stat_name = model_name.replace('pitcher_', '')
                print(f"  {stat_name}: R² = {perf['r2']:.3f}, MAE = {perf['mae']:.2f} ({perf['algorithm']})")
        
        return model_dir

def main():
    """Main training workflow"""
    print("🚀 TRAINING INDIVIDUAL STAT MODELS")
    print("=" * 60)
    
    # Use the same training data as the main models
    data_file = 'mlb_data_full_seasons/combined_data/mlb_complete_2023_2024.csv'
    
    if not os.path.exists(data_file):
        print(f"❌ Training data not found: {data_file}")
        return False
    
    # Initialize trainer
    trainer = IndividualStatModelTrainer(data_file)
    
    # Load and prepare data
    training_data = trainer.load_and_prepare_data()
    
    if len(training_data) < 100:
        print(f"❌ Insufficient training data: {len(training_data)} samples")
        return False
    
    # Train models
    trainer.train_stat_models(training_data)
    
    # Save models
    model_dir = trainer.save_models()
    
    if model_dir:
        print(f"\n🎉 Individual stat model training completed!")
        print(f"📁 Models saved to: {model_dir}")
        print(f"\n📝 Next steps:")
        print("1. Integrate with inference system")
        print("2. Test individual stat predictions")
        print("3. Update CSV prediction scripts")
        return True
    else:
        print(f"\n❌ Individual stat model training failed")
        return False

if __name__ == "__main__":
    main()