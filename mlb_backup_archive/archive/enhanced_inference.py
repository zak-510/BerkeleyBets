#!/usr/bin/env python3
"""
Enhanced MLB Inference System
Predicts both fantasy points and individual player statistics
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.data_collection import MLBDataCollector
from src.position_mapping import PositionMapper

class EnhancedMLBInference:
    """Enhanced inference system for fantasy points and individual stats"""
    
    def __init__(self, models_dir="models", stat_models_dir=None):
        self.models_dir = models_dir
        self.stat_models_dir = stat_models_dir or self._find_latest_stat_models()
        
        # Fantasy point models
        self.fantasy_models = {}
        self.fantasy_scalers = {}
        self.fantasy_performance = {}
        
        # Individual stat models
        self.stat_models = {}
        self.stat_scalers = {}
        self.stat_performance = {}
        
        # System components
        self.data_collector = MLBDataCollector(cache_dir="mlb_data")
        self.position_mapper = PositionMapper()
        
        # Load models
        self.load_fantasy_models()
        self.load_stat_models()
    
    def _find_latest_stat_models(self):
        """Find the latest individual stat models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('individual_stat_models_')]
            if dirs:
                latest = max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
                return latest
        except:
            pass
        return None
    
    def load_fantasy_models(self):
        """Load fantasy point prediction models"""
        try:
            # Load performance metrics
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.fantasy_performance = json.load(f)
            
            # Load models for all positions
            positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'P']
            
            for position in positions:
                try:
                    model_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_model.pkl')
                    scaler_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_scaler.pkl')
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.fantasy_models[position] = joblib.load(model_file)
                        self.fantasy_scalers[position] = joblib.load(scaler_file)
                        
                except Exception as e:
                    print(f"⚠️ Failed to load fantasy model for {position}: {e}")
            
            print(f"✅ Loaded {len(self.fantasy_models)} fantasy point models")
            
        except Exception as e:
            print(f"❌ Failed to load fantasy models: {e}")
    
    def load_stat_models(self):
        """Load individual stat prediction models"""
        if not self.stat_models_dir or not os.path.exists(self.stat_models_dir):
            print("⚠️ No individual stat models found")
            return
        
        try:
            # Load performance metrics
            perf_file = os.path.join(self.stat_models_dir, 'individual_stat_performance.json')
            with open(perf_file, 'r') as f:
                self.stat_performance = json.load(f)
            
            # Load all stat models
            for model_name in self.stat_performance.keys():
                try:
                    model_file = os.path.join(self.stat_models_dir, f'{model_name}_model.pkl')
                    scaler_file = os.path.join(self.stat_models_dir, f'{model_name}_scaler.pkl')
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.stat_models[model_name] = joblib.load(model_file)
                        self.stat_scalers[model_name] = joblib.load(scaler_file)
                        
                except Exception as e:
                    print(f"⚠️ Failed to load stat model {model_name}: {e}")
            
            print(f"✅ Loaded {len(self.stat_models)} individual stat models")
            
        except Exception as e:
            print(f"❌ Failed to load stat models: {e}")
    
    def predict_player_enhanced(self, player_name, position_hint=None):
        """Predict both fantasy points and individual stats for a player"""
        try:
            print(f"\n🎯 ENHANCED PREDICTION: {player_name}")
            print("=" * 50)
            
            # Get player ID and position
            # Split name into first and last name
            name_parts = player_name.strip().split()
            if len(name_parts) < 2:
                return {'success': False, 'error': f'Please provide full name (first last): {player_name}'}
            
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
            
            player_id = self.data_collector.get_player_id(last_name, first_name)
            if not player_id:
                return {'success': False, 'error': f'Player not found: {player_name}'}
            
            # Detect position
            position = self.position_mapper.get_player_position(player_id, player_name, position_hint)
            print(f"🏷️ Position: {position}")
            
            # Collect recent game data
            from datetime import timedelta
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            
            # Try both batter and pitcher data
            game_data = None
            for player_type in ['b', 'p']:
                try:
                    data = self.data_collector.get_game_data(player_id, start_date, end_date, player_type)
                    if data and len(data) > 0:
                        game_data = data
                        break
                except:
                    continue
            
            if not game_data or len(game_data) == 0:
                return {'success': False, 'error': f'No recent game data for {player_name}'}
            
            print(f"📊 Using {len(game_data)} recent games")
            
            # Generate features
            features = self._generate_features(game_data)
            if features is None:
                return {'success': False, 'error': 'Failed to generate features'}
            
            # Predict fantasy points
            fantasy_prediction = self._predict_fantasy_points(features, position)
            
            # Predict individual stats
            individual_stats = self._predict_individual_stats(features, position)
            
            result = {
                'success': True,
                'player_name': player_name,
                'position': position,
                'fantasy_points': fantasy_prediction,
                'individual_stats': individual_stats,
                'prediction_date': datetime.now().isoformat(),
                'games_analyzed': len(game_data)
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Prediction failed: {str(e)}'}
    
    def _generate_features(self, game_data):
        """Generate features from game data (same as current system)"""
        try:
            df = pd.DataFrame(game_data)
            
            # Calculate historical features
            fantasy_points = df['fantasy_points'].fillna(0)
            
            features = {
                'avg_fantasy_points_L15': fantasy_points.tail(15).mean() if len(fantasy_points) >= 1 else 0,
                'avg_fantasy_points_L10': fantasy_points.tail(10).mean() if len(fantasy_points) >= 1 else 0,
                'avg_fantasy_points_L5': fantasy_points.tail(5).mean() if len(fantasy_points) >= 1 else 0,
                'games_since_last_good_game': self._games_since_good_game(fantasy_points),
                'trend_last_5_games': self._calculate_trend(fantasy_points.tail(5)),
                'consistency_score': self._calculate_consistency(fantasy_points)
            }
            
            return features
            
        except Exception as e:
            print(f"❌ Feature generation failed: {e}")
            return None
    
    def _games_since_good_game(self, fantasy_points, threshold=10):
        """Calculate games since last good performance"""
        try:
            for i, points in enumerate(reversed(fantasy_points)):
                if points >= threshold:
                    return i
            return min(len(fantasy_points), 10)  # Cap at 10
        except:
            return 5
    
    def _calculate_trend(self, points):
        """Calculate performance trend"""
        try:
            if len(points) < 2:
                return 0
            x = np.arange(len(points))
            return np.polyfit(x, points, 1)[0]  # Slope of trend line
        except:
            return 0
    
    def _calculate_consistency(self, points):
        """Calculate performance consistency score"""
        try:
            if len(points) < 2:
                return 0.5
            std = np.std(points)
            mean = np.mean(points)
            if mean == 0:
                return 0.5
            cv = std / mean  # Coefficient of variation
            return max(0, min(1, 1 - cv))  # Convert to 0-1 scale
        except:
            return 0.5
    
    def _predict_fantasy_points(self, features, position):
        """Predict fantasy points using existing models"""
        try:
            if position not in self.fantasy_models:
                return {'predicted': 0, 'confidence': 0, 'error': 'No model for position'}
            
            # Prepare features
            feature_order = [
                'avg_fantasy_points_L15',
                'avg_fantasy_points_L10', 
                'avg_fantasy_points_L5',
                'games_since_last_good_game',
                'trend_last_5_games',
                'consistency_score'
            ]
            
            feature_values = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
            feature_values = np.nan_to_num(feature_values, nan=0.0)
            
            # Scale and predict
            scaled_features = self.fantasy_scalers[position].transform(feature_values)
            prediction = self.fantasy_models[position].predict(scaled_features)[0]
            
            # Calculate confidence
            model_r2 = self.fantasy_performance[position]['r2']
            confidence = min(0.9, max(0.3, model_r2))
            
            return {
                'predicted': round(prediction, 2),
                'confidence': round(confidence, 2),
                'model_r2': round(model_r2, 3)
            }
            
        except Exception as e:
            return {'predicted': 0, 'confidence': 0, 'error': str(e)}
    
    def _predict_individual_stats(self, features, position):
        """Predict individual stats"""
        predictions = {}
        
        # Determine player type
        player_type = 'pitcher' if position == 'P' else 'batter'
        
        # Define stats to predict based on player type
        if player_type == 'batter':
            stat_names = ['hits', 'doubles', 'triples', 'home_runs', 'walks', 
                         'strikeouts', 'runs', 'rbis', 'stolen_bases']
        else:
            stat_names = ['innings_pitched', 'strikeouts', 'hits_allowed', 
                         'walks_allowed', 'home_runs_allowed', 'earned_runs']
        
        # Predict each stat
        for stat_name in stat_names:
            model_key = f"{player_type}_{stat_name}"
            
            if model_key in self.stat_models:
                try:
                    # Prepare features (same as fantasy points)
                    feature_order = [
                        'avg_fantasy_points_L15',
                        'avg_fantasy_points_L10', 
                        'avg_fantasy_points_L5',
                        'games_since_last_good_game',
                        'trend_last_5_games',
                        'consistency_score'
                    ]
                    
                    feature_values = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
                    feature_values = np.nan_to_num(feature_values, nan=0.0)
                    
                    # Scale and predict
                    scaled_features = self.stat_scalers[model_key].transform(feature_values)
                    prediction = self.stat_models[model_key].predict(scaled_features)[0]
                    
                    # Ensure non-negative for count stats
                    if stat_name != 'innings_pitched':
                        prediction = max(0, prediction)
                    
                    # Round appropriately
                    if stat_name == 'innings_pitched':
                        prediction = round(prediction, 1)
                    else:
                        prediction = round(prediction)
                    
                    # Get model performance
                    model_r2 = self.stat_performance[model_key]['r2']
                    confidence = min(0.9, max(0.1, model_r2))
                    
                    predictions[f'predicted_{stat_name}'] = {
                        'value': prediction,
                        'confidence': round(confidence, 2),
                        'model_r2': round(model_r2, 3)
                    }
                    
                except Exception as e:
                    predictions[f'predicted_{stat_name}'] = {
                        'value': 0,
                        'confidence': 0,
                        'error': str(e)
                    }
            else:
                predictions[f'predicted_{stat_name}'] = {
                    'value': 0,
                    'confidence': 0,
                    'error': 'No model available'
                }
        
        return predictions
    
    def get_system_status(self):
        """Get status of both fantasy and stat prediction systems"""
        return {
            'fantasy_models_loaded': len(self.fantasy_models),
            'stat_models_loaded': len(self.stat_models),
            'fantasy_models_available': list(self.fantasy_models.keys()),
            'stat_models_available': list(self.stat_models.keys()),
            'system_ready': len(self.fantasy_models) > 0 or len(self.stat_models) > 0
        }

def main():
    """Test the enhanced inference system"""
    print("🚀 ENHANCED MLB INFERENCE SYSTEM TEST")
    print("=" * 50)
    
    # Initialize system
    inference = EnhancedMLBInference()
    
    # Check status
    status = inference.get_system_status()
    print(f"📊 System Status:")
    print(f"  Fantasy Models: {status['fantasy_models_loaded']}")
    print(f"  Stat Models: {status['stat_models_loaded']}")
    print(f"  System Ready: {status['system_ready']}")
    
    if not status['system_ready']:
        print("❌ System not ready - no models loaded")
        return
    
    # Test prediction
    test_player = "Aaron Judge"
    print(f"\n🧪 Testing enhanced prediction for {test_player}...")
    
    result = inference.predict_player_enhanced(test_player)
    
    if result['success']:
        print(f"\n✅ Enhanced prediction successful!")
        print(f"📊 Fantasy Points: {result['fantasy_points']['predicted']:.2f} "
              f"(confidence: {result['fantasy_points']['confidence']:.2f})")
        
        print(f"\n📈 Individual Stats:")
        for stat_name, stat_data in result['individual_stats'].items():
            if 'error' not in stat_data:
                print(f"  {stat_name}: {stat_data['value']} "
                      f"(confidence: {stat_data['confidence']:.2f})")
            else:
                print(f"  {stat_name}: Error - {stat_data['error']}")
    else:
        print(f"❌ Prediction failed: {result['error']}")

if __name__ == "__main__":
    main()