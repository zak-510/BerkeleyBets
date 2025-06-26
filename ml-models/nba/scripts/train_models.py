#!/usr/bin/env python3
"""
NBA Prediction Model Rebuild - ZERO DATA LEAKAGE
Strict temporal validation with realistic prediction ranges
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class NBAModelBuilder:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = None
        self.validation_results = {}
        self.checkpoint_dir = "NBA_models_v2_" + datetime.now().strftime("%Y%m%d")
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # REALISTIC TARGET RANGES - CRITICAL VALIDATION
        self.target_ranges = {
            'SUPERSTARS': {'points': (28, 35), 'players': ['Giannis Antetokounmpo', 'Joel Embiid', 'Jayson Tatum', 'Devin Booker']},
            'ALL_STARS': {'points': (20, 28), 'players': ['Pascal Siakam', 'Domantas Sabonis', 'Anthony Edwards', 'Paolo Banchero']},
            'ROLE_PLAYERS': {'points': (12, 20), 'players': ['Marcus Smart', 'Al Horford', 'John Collins', 'Myles Turner']},
            'BENCH_PLAYERS': {'points': (8, 15), 'players': ['Nic Claxton', 'Brook Lopez', 'Rudy Gobert']}
        }
        
    def create_temporal_features(self, df, window=10):
        """
        Create rolling features with STRICT temporal validation
        ZERO data leakage - only use previous games
        """
        print("Creating temporal features with NO data leakage...")
        
        # Sort by player and date to ensure temporal order
        df = df.sort_values(['player_name', 'game_date'])
        
        features = []
        
        for player in df['player_name'].unique():
            player_data = df[df['player_name'] == player].copy()
            
            # Rolling averages - ONLY previous games
            player_data['rolling_fg_pct'] = player_data['fg_pct'].rolling(window=window, min_periods=3).mean().shift(1)
            player_data['rolling_3p_pct'] = player_data['fg3_pct'].rolling(window=window, min_periods=3).mean().shift(1)
            player_data['rolling_ft_pct'] = player_data['ft_pct'].rolling(window=window, min_periods=3).mean().shift(1)
            player_data['rolling_minutes'] = player_data['minutes'].rolling(window=window, min_periods=3).mean().shift(1)
            player_data['rolling_usage'] = player_data['usage_rate'].rolling(window=window, min_periods=3).mean().shift(1)
            
            # Rate-based features (no cumulative stats)
            player_data['points_per_minute'] = player_data['points'] / np.maximum(player_data['minutes'], 1)
            player_data['rebounds_per_minute'] = player_data['rebounds'] / np.maximum(player_data['minutes'], 1)
            player_data['assists_per_minute'] = player_data['assists'] / np.maximum(player_data['minutes'], 1)
            
            # Team pace (rolling average)
            player_data['team_pace'] = player_data['team_possessions'].rolling(window=5, min_periods=2).mean().shift(1)
            
            # Drop rows without enough history
            player_data = player_data.dropna(subset=['rolling_fg_pct', 'rolling_minutes'])
            
            features.append(player_data)
        
        return pd.concat(features, ignore_index=True)
    
    def prepare_training_data(self):
        """
        Prepare clean training data with temporal validation
        """
        print("🔄 Preparing training data with temporal validation...")
        
        # Simulate NBA game data (in production, load from database)
        # This would come from actual NBA game logs with proper dates
        np.random.seed(42)
        
        players_by_position = {
            'PG': ['Luka Dončić', 'Shai Gilgeous-Alexander', 'Trae Young', 'Damian Lillard', 'Chris Paul'],
            'SG': ['Devin Booker', 'Donovan Mitchell', 'Anthony Edwards', 'Jaylen Brown', 'Bradley Beal'],
            'SF': ['Jayson Tatum', 'Jimmy Butler', 'Paul George', 'LeBron James', 'DeMar DeRozan'],
            'PF': ['Giannis Antetokounmpo', 'Paolo Banchero', 'Pascal Siakam', 'Julius Randle', 'Lauri Markkanen'],
            'C': ['Joel Embiid', 'Nikola Jokić', 'Anthony Davis', 'Bam Adebayo', 'Karl-Anthony Towns']
        }
        
        all_data = []
        
        for position, players in players_by_position.items():
            for player in players:
                # Generate 82 games per player (full season)
                for game in range(82):
                    # Realistic baseline stats by position
                    if position == 'C':
                        base_points = np.random.normal(20, 8)
                        base_rebounds = np.random.normal(10, 3)
                        base_assists = np.random.normal(3, 2)
                    elif position == 'PF':
                        base_points = np.random.normal(18, 7)
                        base_rebounds = np.random.normal(8, 3)
                        base_assists = np.random.normal(4, 2)
                    elif position in ['SG', 'SF']:
                        base_points = np.random.normal(16, 6)
                        base_rebounds = np.random.normal(5, 2)
                        base_assists = np.random.normal(4, 2)
                    else:  # PG
                        base_points = np.random.normal(15, 5)
                        base_rebounds = np.random.normal(4, 2)
                        base_assists = np.random.normal(7, 3)
                    
                    # Player skill multipliers (superstars get higher multipliers)
                    if player in ['Giannis Antetokounmpo', 'Joel Embiid', 'Jayson Tatum', 'Luka Dončić']:
                        skill_mult = 1.8
                    elif player in ['Devin Booker', 'Anthony Edwards', 'Pascal Siakam']:
                        skill_mult = 1.4
                    else:
                        skill_mult = 1.0
                    
                    game_data = {
                        'player_name': player,
                        'position': position,
                        'game_date': f"2023-{(game//10)+10:02d}-{(game%10)+1:02d}",
                        'points': max(0, base_points * skill_mult),
                        'rebounds': max(0, base_rebounds),
                        'assists': max(0, base_assists),
                        'minutes': np.random.normal(32, 5),
                        'fg_pct': np.random.normal(0.45, 0.05),
                        'fg3_pct': np.random.normal(0.35, 0.08),
                        'ft_pct': np.random.normal(0.80, 0.10),
                        'usage_rate': np.random.normal(25, 5),
                        'team_possessions': np.random.normal(100, 5)
                    }
                    
                    # Fantasy score calculation
                    game_data['fantasy_score'] = (
                        game_data['points'] + 
                        game_data['rebounds'] * 1.2 + 
                        game_data['assists'] * 1.5
                    )
                    
                    all_data.append(game_data)
        
        df = pd.DataFrame(all_data)
        
        # Apply temporal feature engineering
        df = self.create_temporal_features(df)
        
        print(f"✅ Training data prepared: {len(df)} games with temporal features")
        return df
    
    def validate_data_leakage(self, X_train, X_test, y_train, y_test):
        """
        CRITICAL: Check for data leakage
        """
        # Quick model to check for suspiciously high R²
        quick_model = RandomForestRegressor(n_estimators=10, random_state=42)
        quick_model.fit(X_train, y_train[:, 0])  # Just points
        r2 = quick_model.score(X_test, y_test[:, 0])
        
        if r2 > 0.6:
            print(f"⚠️  WARNING: Suspiciously high R² ({r2:.3f}) - CHECK FOR DATA LEAKAGE!")
            return False
        else:
            print(f"✅ Data leakage check passed: R² = {r2:.3f}")
            return True
    
    def train_position_model(self, df, position):
        """
        Train model for specific position with temporal validation
        """
        print(f"\n🏀 Training {position} model...")
        
        position_data = df[df['position'] == position].copy()
        
        if len(position_data) < 50:
            print(f"⚠️  Insufficient data for {position}: {len(position_data)} games")
            return None
        
        # Features: ONLY temporal rolling averages and rates
        feature_cols = [
            'rolling_fg_pct', 'rolling_3p_pct', 'rolling_ft_pct', 
            'rolling_minutes', 'rolling_usage', 'team_pace'
        ]
        
        # Targets: points, rebounds, assists, fantasy_score
        target_cols = ['points', 'rebounds', 'assists', 'fantasy_score']
        
        X = position_data[feature_cols].values
        y = position_data[target_cols].values
        
        # Remove any remaining NaN values
        valid_mask = ~(np.isnan(X).any(axis=1) | np.isnan(y).any(axis=1))
        X = X[valid_mask]
        y = y[valid_mask]
        
        if len(X) < 30:
            print(f"⚠️  Too few valid samples for {position}: {len(X)}")
            return None
        
        # STRICT temporal split - NO random splitting!
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Data leakage validation
        if not self.validate_data_leakage(X_train, X_test, y_train, y_test):
            print(f"❌ STOPPING: Data leakage detected for {position}")
            return None
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = MultiOutputRegressor(
            RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Validation
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        points_mse = mean_squared_error(y_test[:, 0], y_pred[:, 0])
        points_r2 = r2_score(y_test[:, 0], y_pred[:, 0])
        
        validation_results = {
            'position': position,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'points_mse': float(points_mse),
            'points_r2': float(points_r2),
            'features': feature_cols,
            'targets': target_cols
        }
        
        print(f"📊 {position} Results: MSE={points_mse:.2f}, R²={points_r2:.3f}")
        
        # CRITICAL: Sanity check predictions
        sample_pred = y_pred[:5, 0]  # First 5 point predictions
        print(f"🔍 Sample predictions: {sample_pred}")
        
        if np.any(sample_pred < 5) or np.any(sample_pred > 50):
            print(f"⚠️  WARNING: Unrealistic predictions for {position}")
        
        # Save checkpoint
        self.save_checkpoint(position, model, scaler, validation_results, feature_cols)
        
        return {
            'model': model,
            'scaler': scaler,
            'validation': validation_results
        }
    
    def save_checkpoint(self, position, model, scaler, validation_results, feature_names):
        """
        Save model checkpoint with metadata
        """
        checkpoint_data = {
            'model': model,
            'scaler': scaler,
            'features': feature_names,
            'validation': validation_results,
            'created_date': datetime.now().isoformat(),
            'version': 'v2_rebuild'
        }
        
        # Save model
        model_path = os.path.join(self.checkpoint_dir, f'nba_{position.lower()}_model_v2.pkl')
        joblib.dump(checkpoint_data, model_path)
        
        # Save metadata
        metadata_path = os.path.join(self.checkpoint_dir, f'nba_{position.lower()}_metadata.json')
        with open(metadata_path, 'w') as f:
            metadata = {
                'position': position,
                'validation_results': validation_results,
                'feature_names': feature_names,
                'created_date': datetime.now().isoformat(),
                'model_path': model_path
            }
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Checkpoint saved: {model_path}")
    
    def test_known_players(self):
        """
        Test with known players for sanity check
        """
        print("\n🧪 Testing with known players...")
        
        # Test cases with expected ranges
        test_cases = [
            {
                'name': 'Giannis Antetokounmpo',
                'position': 'PF',
                'features': [0.55, 0.30, 0.70, 35.0, 32.0, 100.0],  # Elite stats
                'expected_points': (28, 35)
            },
            {
                'name': 'Joel Embiid',
                'position': 'C',
                'features': [0.52, 0.35, 0.85, 33.0, 35.0, 98.0],  # Elite center
                'expected_points': (28, 35)
            },
            {
                'name': 'Chris Paul',
                'position': 'PG',
                'features': [0.45, 0.37, 0.85, 28.0, 18.0, 95.0],  # Veteran facilitator
                'expected_points': (12, 20)
            }
        ]
        
        all_tests_passed = True
        
        for test_case in test_cases:
            position = test_case['position']
            
            if position in self.models:
                model_data = self.models[position]
                model = model_data['model']
                scaler = model_data['scaler']
                
                # Make prediction
                features_scaled = scaler.transform([test_case['features']])
                prediction = model.predict(features_scaled)[0]
                
                predicted_points = prediction[0]
                expected_min, expected_max = test_case['expected_points']
                
                print(f"🏀 {test_case['name']} ({position}): {predicted_points:.1f} points")
                
                if expected_min <= predicted_points <= expected_max:
                    print(f"   ✅ PASS: Within expected range ({expected_min}-{expected_max})")
                else:
                    print(f"   ❌ FAIL: Outside expected range ({expected_min}-{expected_max})")
                    all_tests_passed = False
            else:
                print(f"   ⚠️  Model not found for {position}")
                all_tests_passed = False
        
        return all_tests_passed
    
    def build_all_models(self):
        """
        Main function to build all NBA models
        """
        print("🚀 Starting NBA Model Rebuild - ZERO DATA LEAKAGE")
        print("=" * 60)
        
        # Step 1: Prepare data
        df = self.prepare_training_data()
        
        # Step 2: Train models for each position
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        
        for position in positions:
            model_result = self.train_position_model(df, position)
            if model_result:
                self.models[position] = model_result
                self.validation_results[position] = model_result['validation']
        
        # Step 3: Test with known players
        tests_passed = self.test_known_players()
        
        # Step 4: Save final metadata
        final_metadata = {
            'rebuild_date': datetime.now().isoformat(),
            'version': 'v2_rebuild',
            'validation_results': self.validation_results,
            'tests_passed': tests_passed,
            'models_trained': list(self.models.keys()),
            'checkpoint_directory': self.checkpoint_dir
        }
        
        metadata_path = os.path.join(self.checkpoint_dir, 'rebuild_summary.json')
        with open(metadata_path, 'w') as f:
            json.dump(final_metadata, f, indent=2)
        
        print("\n" + "=" * 60)
        if tests_passed:
            print("✅ NBA MODEL REBUILD COMPLETE - ALL TESTS PASSED")
        else:
            print("❌ NBA MODEL REBUILD FAILED - TESTS FAILED")
        
        print(f"📁 Models saved in: {self.checkpoint_dir}")
        return tests_passed

if __name__ == "__main__":
    builder = NBAModelBuilder()
    success = builder.build_all_models()
    
    if success:
        print("\n🎉 Ready to deploy new NBA prediction system!")
    else:
        print("\n🚫 DO NOT DEPLOY - Fix issues first!")