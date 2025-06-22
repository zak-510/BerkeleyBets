#!/usr/bin/env python3
"""
MLB Fantasy Prediction System - Inference
Clean interface for making predictions with trained models
"""

import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime, timedelta
from src.data_collection import MLBDataCollector
from src.position_mapping import PositionMapper
from src.temporal_validation import TemporalValidator
from src.feature_config import MLBFeatureConfig

class MLBInference:
    """Clean inference interface for MLB fantasy predictions"""
    
    def __init__(self, models_dir="models", data_dir="mlb_data"):
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.models = {}
        self.scalers = {}
        self.performance = {}
        self.data_collector = MLBDataCollector(cache_dir=data_dir)
        self.position_mapper = PositionMapper()
        self.temporal_validator = TemporalValidator()
        self.feature_config = MLBFeatureConfig()
        
        # Load models and performance data
        self._load_models()
        
    def _load_models(self):
        """Load all trained models and scalers"""
        try:
            # Load performance metrics
            with open(f"{self.models_dir}/model_performance.json", 'r') as f:
                self.performance = json.load(f)
            
            # Load models for each position
            positions = ['1B', '2B', '3B', 'SS', 'OF', 'P', 'C']
            
            for position in positions:
                try:
                    model_file = f"{self.models_dir}/mlb_{position.lower()}_model.pkl"
                    scaler_file = f"{self.models_dir}/mlb_{position.lower()}_scaler.pkl"
                    
                    self.models[position] = joblib.load(model_file)
                    self.scalers[position] = joblib.load(scaler_file)
                    
                    r2_val = self.performance.get(position, {}).get('r2', 'N/A')
                    r2_str = f"{r2_val:.3f}" if isinstance(r2_val, (int, float)) else str(r2_val)
                    print(f"✅ Loaded {position} model (R²={r2_str})")
                    
                except FileNotFoundError:
                    print(f"⚠️  {position} model not found")
                    
        except Exception as e:
            print(f"❌ Error loading models: {e}")
    
    def predict_player(self, player_name: str, date_range: tuple = None, use_enhanced_models: bool = False):
        """
        Predict fantasy points for a specific player
        
        Args:
            player_name: Player name (e.g., "Aaron Judge")
            date_range: Tuple of (start_date, end_date) for prediction period
            use_enhanced_models: Whether to use the enhanced models for P and 3B
        """
        print(f"\n🎯 PREDICTING: {player_name}")
        print("=" * 50)
        
        try:
            # Get player data
            if date_range is None:
                # Default to recent week
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                date_range = (start_date, end_date)
            
            # Collect player data
            print(f"📊 Collecting data for {date_range[0]} to {date_range[1]}...")
            
            # Parse player name
            name_parts = player_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            else:
                print(f"❌ Invalid player name format: {player_name}")
                return None
            
            # Get player ID
            player_id = self.data_collector.get_player_id(last_name, first_name)
            if player_id is None:
                print(f"❌ Could not find player ID for {player_name}")
                return None
            
            # Collect game data (try both batter and pitcher)
            player_data = None
            for player_type in ['b', 'p']:
                try:
                    game_data = self.data_collector.get_game_data(player_id, date_range[0], date_range[1], player_type)
                    if game_data and len(game_data) > 0:
                        player_data = pd.DataFrame(game_data)
                        break
                except Exception as e:
                    continue
            
            if player_data is None:
                # Try using the collect_player_data method
                player_info = {'first_name': first_name, 'last_name': last_name, 'player_id': player_id}
                result = self.data_collector.collect_player_data(player_info, date_range[0], date_range[1])
                if result.get('success') and result.get('game_data'):
                    player_data = pd.DataFrame(result['game_data'])
                else:
                    player_data = None
            
            if player_data is None or len(player_data) == 0:
                print(f"❌ No data found for {player_name}")
                return None
            
            # Get position
            position = self.position_mapper.get_player_position(player_id, player_name)
            if position is None:
                print(f"❌ Could not determine position for {player_name}")
                return None
            
            print(f"🏷️  Position: {position}")
            
            # Check if we have a model for this position
            if position not in self.models:
                print(f"❌ No model available for position {position}")
                return None
            
            # Generate features
            print("🔧 Generating features...")
            features_data = self.temporal_validator.generate_historical_features(player_data)
            
            if len(features_data) == 0:
                print("❌ Could not generate features")
                return None
            
            # Get the features used by the model (fallback to centralized config)
            model_features = self.performance[position].get('features', 
                                                          self.feature_config.get_features_for_position(position))
            
            # Filter features to only those available in the data
            available_features = [f for f in model_features if f in features_data.columns]
            
            if not available_features:
                print("❌ No valid features available for prediction")
                return None
            
            # Prepare feature matrix
            X = features_data[available_features].fillna(0)
            
            if len(X) == 0:
                print("❌ No valid feature data")
                return None
            
            # Scale features
            X_scaled = self.scalers[position].transform(X)
            
            # Make predictions
            predictions = self.models[position].predict(X_scaled)
            
            # Prepare results
            results = []
            for i, (idx, row) in enumerate(features_data.iterrows()):
                result = {
                    'game_date': row['game_date'],
                    'predicted_points': round(predictions[i], 2),
                    'actual_points': row.get('fantasy_points', None),
                                         'confidence': self.performance[position].get('cv_r2_mean', self.performance[position].get('r2', 0.5))
                }
                results.append(result)
            
            # Display results
            print("\n📈 PREDICTIONS:")
            print("-" * 60)
            for result in results:
                actual_str = f"(Actual: {result['actual_points']:.1f})" if result['actual_points'] is not None else ""
                print(f"  {result['game_date']}: {result['predicted_points']:.1f} points {actual_str}")
            
            avg_prediction = np.mean(predictions)
            print(f"\n📊 Average Predicted Points: {avg_prediction:.1f}")
            r2_val = self.performance[position].get('cv_r2_mean', self.performance[position].get('r2', 0.5))
            print(f"🎯 Model Confidence (R²): {r2_val:.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return None
    
    def batch_predict(self, player_list: list, date_range: tuple = None):
        """
        Make predictions for multiple players
        
        Args:
            player_list: List of player names
            date_range: Tuple of (start_date, end_date)
        """
        print(f"\n🎯 BATCH PREDICTIONS FOR {len(player_list)} PLAYERS")
        print("=" * 60)
        
        results = {}
        
        for player_name in player_list:
            result = self.predict_player(player_name, date_range)
            results[player_name] = result
        
        # Summary
        print(f"\n📊 BATCH SUMMARY")
        print("-" * 30)
        successful = sum(1 for r in results.values() if r is not None)
        print(f"✅ Successful predictions: {successful}/{len(player_list)}")
        
        return results
    
    def get_model_performance(self):
        """Display model performance metrics"""
        print("\n🏆 MODEL PERFORMANCE SUMMARY")
        print("=" * 50)
        
        for position, perf in self.performance.items():
            r2 = perf.get('cv_r2_mean', perf.get('r2', 'N/A'))
            mae = perf.get('cv_mae_mean', perf.get('mae', 'N/A'))
            n_samples = perf.get('n_samples', 'N/A')
            
            # Handle string/numeric values safely
            if isinstance(r2, (int, float)):
                status = "🎯 EXCELLENT" if r2 > 0.7 else "✅ GOOD" if r2 > 0.3 else "⚠️ POOR"
                r2_str = f"{r2:6.3f}"
            else:
                status = "❓ UNKNOWN"
                r2_str = f"{str(r2):>6}"
            
            mae_str = f"{mae:5.2f}" if isinstance(mae, (int, float)) else f"{str(mae):>5}"
            n_str = f"{n_samples:>3}" if isinstance(n_samples, (int, float)) else f"{str(n_samples):>3}"
            
            print(f"{position:>3}: R²={r2_str} | MAE={mae_str} | Samples={n_str} | {status}")
    
    def predict_top_players(self, position: str = None, date_range: tuple = None):
        """
        Predict for top players at a specific position or all positions
        
        Args:
            position: Specific position (e.g., 'OF', 'P') or None for all
            date_range: Tuple of (start_date, end_date)
        """
        # Top players by position
        top_players = {
            'C': ['Salvador Pérez', 'Will Smith'],
            '1B': ['Freddie Freeman', 'Vladimir Guerrero Jr.', 'Pete Alonso'],
            '2B': ['José Altuve', 'Gleyber Torres', 'Marcus Semien'],
            '3B': ['Manny Machado', 'Rafael Devers', 'Nolan Arenado'],
            'SS': ['Trea Turner', 'Francisco Lindor', 'Corey Seager'],
            'OF': ['Aaron Judge', 'Mookie Betts', 'Ronald Acuña Jr.', 'Juan Soto'],
            'P': ['Gerrit Cole', 'Shane Bieber', 'Spencer Strider']
        }
        
        if position:
            if position in top_players:
                players = top_players[position]
                print(f"\n🎯 TOP {position} PLAYERS PREDICTIONS")
            else:
                print(f"❌ Position {position} not found")
                return None
        else:
            players = []
            for pos_players in top_players.values():
                players.extend(pos_players[:2])  # Top 2 per position
            print(f"\n🎯 TOP PLAYERS ACROSS ALL POSITIONS")
        
        return self.batch_predict(players, date_range)

def main():
    """Main inference interface"""
    print("⚾ MLB FANTASY PREDICTION SYSTEM")
    print("=" * 40)
    
    # Initialize inference system
    mlb = MLBInference()
    
    # Show model performance
    mlb.get_model_performance()
    
    # Example predictions
    print("\n🔍 EXAMPLE PREDICTIONS")
    print("-" * 30)
    
    # Single player prediction
    mlb.predict_player("Aaron Judge")
    
    # Top players prediction
    # mlb.predict_top_players("OF")

if __name__ == "__main__":
    main() 