#!/usr/bin/env python3
"""
Optimized Enhanced MLB Inference System
Uses rate-based models for batters (superior performance) and individual stat models for pitchers
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from src.data_collection import MLBDataCollector
from src.position_mapping import PositionMapper

class EnhancedMLBInference:
    """Optimized inference system using best models for each player type"""
    
    def __init__(self, models_dir="models", stat_models_dir=None, rate_models_dir=None):
        self.models_dir = models_dir
        self.stat_models_dir = stat_models_dir or self._find_latest_stat_models()
        self.rate_models_dir = rate_models_dir or self._find_latest_rate_models()
        
        # Fantasy point models
        self.fantasy_models = {}
        self.fantasy_scalers = {}
        self.fantasy_performance = {}
        
        # Individual stat models (for pitchers)
        self.pitcher_stat_models = {}
        self.pitcher_stat_scalers = {}
        self.pitcher_stat_performance = {}
        
        # Rate-based models (for batters)
        self.rate_models = {}
        self.rate_scalers = {}
        self.rate_performance = {}
        
        # System components
        self.data_collector = MLBDataCollector(cache_dir="mlb_data")
        self.position_mapper = PositionMapper()
        
        # Load all models
        self.load_fantasy_models()
        self.load_pitcher_stat_models()
        self.load_rate_models()
    
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
    
    def _find_latest_rate_models(self):
        """Find the latest rate-based models directory"""
        try:
            dirs = [d for d in os.listdir('.') if d.startswith('rate_based_batter_models_')]
            if dirs:
                latest = max(dirs, key=lambda x: x.split('_')[-2] + x.split('_')[-1])
                return latest
        except:
            pass
        return None
    
    def load_fantasy_models(self):
        """Load fantasy point prediction models"""
        try:
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.fantasy_performance = json.load(f)
            
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
    
    def load_pitcher_stat_models(self):
        """Load individual stat models for pitchers only"""
        if not self.stat_models_dir or not os.path.exists(self.stat_models_dir):
            print("⚠️ No individual stat models found")
            return
        
        try:
            perf_file = os.path.join(self.stat_models_dir, 'individual_stat_performance.json')
            with open(perf_file, 'r') as f:
                all_performance = json.load(f)
            
            # Only load pitcher models (they perform well)
            for model_name, perf in all_performance.items():
                if model_name.startswith('pitcher_'):
                    try:
                        model_file = os.path.join(self.stat_models_dir, f'{model_name}_model.pkl')
                        scaler_file = os.path.join(self.stat_models_dir, f'{model_name}_scaler.pkl')
                        
                        if os.path.exists(model_file) and os.path.exists(scaler_file):
                            self.pitcher_stat_models[model_name] = joblib.load(model_file)
                            self.pitcher_stat_scalers[model_name] = joblib.load(scaler_file)
                            self.pitcher_stat_performance[model_name] = perf
                            
                    except Exception as e:
                        print(f"⚠️ Failed to load pitcher stat model {model_name}: {e}")
            
            print(f"✅ Loaded {len(self.pitcher_stat_models)} pitcher stat models")
            
        except Exception as e:
            print(f"❌ Failed to load pitcher stat models: {e}")
    
    def load_rate_models(self):
        """Load rate-based models for batters"""
        if not self.rate_models_dir or not os.path.exists(self.rate_models_dir):
            print("⚠️ No rate-based models found")
            return
        
        try:
            perf_file = os.path.join(self.rate_models_dir, 'rate_based_performance.json')
            with open(perf_file, 'r') as f:
                self.rate_performance = json.load(f)
            
            for model_name in self.rate_performance.keys():
                try:
                    model_file = os.path.join(self.rate_models_dir, f"{model_name}_model.pkl")
                    scaler_file = os.path.join(self.rate_models_dir, f"{model_name}_scaler.pkl")
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.rate_models[model_name] = joblib.load(model_file)
                        self.rate_scalers[model_name] = joblib.load(scaler_file)
                        
                except Exception as e:
                    print(f"⚠️ Failed to load rate model {model_name}: {e}")
            
            print(f"✅ Loaded {len(self.rate_models)} rate-based batter models")
            
        except Exception as e:
            print(f"❌ Failed to load rate models: {e}")
    
    def predict_player_enhanced(self, player_name, position_hint=None):
        """Predict both fantasy points and individual stats for a player"""
        try:
            print(f"\\n🎯 ENHANCED PREDICTION: {player_name}")
            print("=" * 50)
            
            # Get player ID and position
            name_parts = player_name.strip().split()
            if len(name_parts) < 2:
                return {'success': False, 'error': f'Please provide full name (first last): {player_name}'}
            
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
            
            player_id = self.data_collector.get_player_id(last_name, first_name)
            if not player_id:
                return {'success': False, 'error': f'Player not found: {player_name}'}
            
            position = self.position_mapper.get_player_position(player_id, player_name, position_hint)
            print(f"🏷️ Position: {position}")
            
            # Collect recent game data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            
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
            
            # Predict individual stats (optimized approach)
            individual_stats = self._predict_individual_stats_optimized(features, position)
            
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
        """Generate features from game data"""
        try:
            df = pd.DataFrame(game_data)
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
            return min(len(fantasy_points), 10)
        except:
            return 5
    
    def _calculate_trend(self, points):
        """Calculate performance trend"""
        try:
            if len(points) < 2:
                return 0
            x = np.arange(len(points))
            return np.polyfit(x, points, 1)[0]
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
            cv = std / mean
            return max(0, min(1, 1 - cv))
        except:
            return 0.5
    
    def _predict_fantasy_points(self, features, position):
        """Predict fantasy points using existing models"""
        try:
            if position not in self.fantasy_models:
                return {'predicted': 0, 'confidence': 0, 'error': 'No model for position'}
            
            feature_order = [
                'avg_fantasy_points_L15', 'avg_fantasy_points_L10', 'avg_fantasy_points_L5',
                'games_since_last_good_game', 'trend_last_5_games', 'consistency_score'
            ]
            
            feature_values = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
            feature_values = np.nan_to_num(feature_values, nan=0.0)
            
            scaled_features = self.fantasy_scalers[position].transform(feature_values)
            prediction = self.fantasy_models[position].predict(scaled_features)[0]
            
            model_r2 = self.fantasy_performance[position]['r2']
            confidence = min(0.9, max(0.3, model_r2))
            
            return {
                'predicted': round(prediction, 2),
                'confidence': round(confidence, 2),
                'model_r2': round(model_r2, 3)
            }
            
        except Exception as e:
            return {'predicted': 0, 'confidence': 0, 'error': str(e)}
    
    def _predict_individual_stats_optimized(self, features, position):
        """Predict individual stats using optimized approach"""
        predictions = {}
        
        if position == 'P':
            # Use individual stat models for pitchers (they perform well)
            predictions = self._predict_pitcher_stats(features)
        else:
            # Use rate-based models for batters (much better performance)
            predictions = self._predict_batter_stats_rate_based(features, position)
        
        return predictions
    
    def _predict_pitcher_stats(self, features):
        """Predict pitcher stats using individual stat models"""
        predictions = {}
        stat_names = ['innings_pitched', 'strikeouts', 'hits_allowed', 
                     'walks_allowed', 'home_runs_allowed', 'earned_runs']
        
        for stat_name in stat_names:
            model_key = f"pitcher_{stat_name}"
            
            if model_key in self.pitcher_stat_models:
                try:
                    feature_order = [
                        'avg_fantasy_points_L15', 'avg_fantasy_points_L10', 'avg_fantasy_points_L5',
                        'games_since_last_good_game', 'trend_last_5_games', 'consistency_score'
                    ]
                    
                    feature_values = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
                    feature_values = np.nan_to_num(feature_values, nan=0.0)
                    
                    scaled_features = self.pitcher_stat_scalers[model_key].transform(feature_values)
                    prediction = self.pitcher_stat_models[model_key].predict(scaled_features)[0]
                    
                    if stat_name != 'innings_pitched':
                        prediction = max(0, prediction)
                    
                    if stat_name == 'innings_pitched':
                        prediction = round(prediction, 1)
                    else:
                        prediction = round(prediction)
                    
                    model_r2 = self.pitcher_stat_performance[model_key]['r2']
                    confidence = min(0.9, max(0.1, model_r2))
                    
                    predictions[f'predicted_{stat_name}'] = {
                        'value': prediction,
                        'confidence': round(confidence, 2),
                        'model_r2': round(model_r2, 3)
                    }
                    
                except Exception as e:
                    predictions[f'predicted_{stat_name}'] = {
                        'value': 0, 'confidence': 0, 'error': str(e)
                    }
            else:
                predictions[f'predicted_{stat_name}'] = {
                    'value': 0, 'confidence': 0, 'error': 'No model available'
                }
        
        return predictions
    
    def _predict_batter_stats_rate_based(self, features, position):
        """Predict batter stats using rate-based models"""
        predictions = {}
        
        if not self.rate_models:
            # Fallback to basic estimates if no rate models
            return self._generate_basic_batter_stats(features)
        
        try:
            # Default player features for rate prediction
            default_features = {
                'player_age': 28, 'age_factor': 1.0, 'games_played': 140,
                'playing_time_factor': 0.86, 'G': 140, 'AB': 500, 'PA': 600,
                'season': 2024, 'tier_above_average': 0, 'tier_average': 1,
                'tier_below_average': 0, 'tier_elite': 0
            }
            
            # Predict rates
            predicted_rates = {}
            for rate_name, model in self.rate_models.items():
                try:
                    expected_features = self.rate_performance[rate_name]['features']
                    feature_vector = [default_features.get(f, 0) for f in expected_features]
                    feature_array = np.array(feature_vector).reshape(1, -1)
                    
                    scaled_features = self.rate_scalers[rate_name].transform(feature_array)
                    prediction = model.predict(scaled_features)[0]
                    confidence = self.rate_performance[rate_name]['r2']
                    
                    rate_stat_name = rate_name.replace('rate_', '')
                    predicted_rates[rate_stat_name] = {'value': prediction, 'confidence': confidence}
                    
                except Exception as e:
                    continue
            
            # Convert rates to game stats
            game_stats = self._convert_rates_to_game_stats(predicted_rates)
            return game_stats
            
        except Exception as e:
            return self._generate_basic_batter_stats(features)
    
    def _convert_rates_to_game_stats(self, rates, plate_appearances=4.0, at_bats=3.5):
        """Convert predicted rates to expected per-game stats"""
        game_stats = {}
        
        # Extract rate values
        batting_avg = rates.get('batting_avg', {}).get('value', 0.250)
        on_base_pct = rates.get('on_base_pct', {}).get('value', 0.320)
        slugging_pct = rates.get('slugging_pct', {}).get('value', 0.400)
        walk_rate = rates.get('walk_rate', {}).get('value', 0.08)
        strikeout_rate = rates.get('strikeout_rate', {}).get('value', 0.20)
        home_run_rate = rates.get('home_run_rate', {}).get('value', 0.03)
        steal_rate = rates.get('steal_rate', {}).get('value', 0.05)
        
        # Convert to game stats
        hits = max(0, round(batting_avg * at_bats))
        walks = max(0, round(walk_rate * plate_appearances))
        strikeouts = max(0, round(strikeout_rate * plate_appearances))
        home_runs = max(0, round(home_run_rate * at_bats))
        stolen_bases = max(0, round(steal_rate))
        
        # Estimate other stats
        ops = on_base_pct + slugging_pct
        doubles = max(0, round(hits * 0.22))
        triples = 1 if hits >= 3 and np.random.random() < 0.02 else 0
        
        if ops >= 0.850:
            run_rbi_factor = 1.2
        elif ops >= 0.750:
            run_rbi_factor = 1.0
        else:
            run_rbi_factor = 0.8
        
        runs = max(0, round((hits + walks) * 0.3 * run_rbi_factor))
        rbis = max(0, round(hits * 0.4 * run_rbi_factor))
        
        # Calculate confidence scores
        rate_confidences = [r.get('confidence', 0) for r in rates.values()]
        avg_confidence = np.mean(rate_confidences) if rate_confidences else 0.1
        
        game_stats = {
            'predicted_hits': {'value': hits, 'confidence': rates.get('batting_avg', {}).get('confidence', avg_confidence)},
            'predicted_doubles': {'value': doubles, 'confidence': avg_confidence * 0.8},
            'predicted_triples': {'value': triples, 'confidence': 0.1},
            'predicted_home_runs': {'value': home_runs, 'confidence': rates.get('home_run_rate', {}).get('confidence', avg_confidence)},
            'predicted_walks': {'value': walks, 'confidence': rates.get('walk_rate', {}).get('confidence', avg_confidence)},
            'predicted_strikeouts': {'value': strikeouts, 'confidence': rates.get('strikeout_rate', {}).get('confidence', avg_confidence)},
            'predicted_runs': {'value': runs, 'confidence': avg_confidence * 0.7},
            'predicted_rbis': {'value': rbis, 'confidence': avg_confidence * 0.7},
            'predicted_stolen_bases': {'value': stolen_bases, 'confidence': rates.get('steal_rate', {}).get('confidence', avg_confidence)}
        }
        
        return game_stats
    
    def _generate_basic_batter_stats(self, features):
        """Generate basic batter stat estimates if rate models unavailable"""
        avg_fantasy = features.get('avg_fantasy_points_L5', 5)
        
        # Basic estimates based on fantasy points
        if avg_fantasy >= 12:
            base_hits, base_hr = 2, 1
        elif avg_fantasy >= 8:
            base_hits, base_hr = 1, 0
        else:
            base_hits, base_hr = 1, 0
        
        return {
            'predicted_hits': {'value': base_hits, 'confidence': 0.2},
            'predicted_doubles': {'value': 0, 'confidence': 0.1},
            'predicted_triples': {'value': 0, 'confidence': 0.1},
            'predicted_home_runs': {'value': base_hr, 'confidence': 0.2},
            'predicted_walks': {'value': 1, 'confidence': 0.2},
            'predicted_strikeouts': {'value': 1, 'confidence': 0.2},
            'predicted_runs': {'value': base_hits, 'confidence': 0.2},
            'predicted_rbis': {'value': base_hits, 'confidence': 0.2},
            'predicted_stolen_bases': {'value': 0, 'confidence': 0.1}
        }
    
    def get_system_status(self):
        """Get status of the optimized prediction system"""
        return {
            'fantasy_models_loaded': len(self.fantasy_models),
            'pitcher_stat_models_loaded': len(self.pitcher_stat_models),
            'rate_models_loaded': len(self.rate_models),
            'fantasy_models_available': list(self.fantasy_models.keys()),
            'pitcher_models_available': list(self.pitcher_stat_models.keys()),
            'rate_models_available': list(self.rate_models.keys()),
            'system_ready': len(self.fantasy_models) > 0,
            'batter_prediction_method': 'rate_based' if self.rate_models else 'basic_estimates',
            'pitcher_prediction_method': 'individual_stat_models' if self.pitcher_stat_models else 'basic_estimates'
        }

def main():
    """Test the optimized enhanced inference system"""
    print("🚀 OPTIMIZED ENHANCED MLB INFERENCE SYSTEM TEST")
    print("=" * 50)
    
    inference = EnhancedMLBInference()
    
    status = inference.get_system_status()
    print(f"📊 System Status:")
    print(f"  Fantasy Models: {status['fantasy_models_loaded']}")
    print(f"  Pitcher Stat Models: {status['pitcher_stat_models_loaded']}")
    print(f"  Rate Models: {status['rate_models_loaded']}")
    print(f"  Batter Method: {status['batter_prediction_method']}")
    print(f"  Pitcher Method: {status['pitcher_prediction_method']}")
    print(f"  System Ready: {status['system_ready']}")
    
    if not status['system_ready']:
        print("❌ System not ready - no models loaded")
        return
    
    # Test predictions
    test_players = ["Aaron Judge", "Spencer Strider"]
    
    for test_player in test_players:
        print(f"\\n🧪 Testing optimized prediction for {test_player}...")
        result = inference.predict_player_enhanced(test_player)
        
        if result['success']:
            print(f"✅ Prediction successful!")
            print(f"📊 Fantasy Points: {result['fantasy_points']['predicted']:.2f}")
            
            print(f"📈 Individual Stats:")
            for stat_name, stat_data in result['individual_stats'].items():
                if 'error' not in stat_data:
                    print(f"  {stat_name}: {stat_data['value']} (conf: {stat_data['confidence']:.2f})")
        else:
            print(f"❌ Prediction failed: {result['error']}")

if __name__ == "__main__":
    main()