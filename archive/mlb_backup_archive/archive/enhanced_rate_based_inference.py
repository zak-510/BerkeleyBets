#!/usr/bin/env python3
"""
Enhanced Rate-Based MLB Inference
Uses rate-based models for much better batter stat predictions
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RateBasedBatterPredictor:
    """Predict batter stats using rate-based models"""
    
    def __init__(self, rate_models_dir=None):
        self.rate_models_dir = rate_models_dir or self._find_latest_rate_models()
        self.rate_models = {}
        self.rate_scalers = {}
        self.rate_performance = {}
        
        self.load_rate_models()
    
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
    
    def load_rate_models(self):
        """Load rate-based models"""
        if not self.rate_models_dir or not os.path.exists(self.rate_models_dir):
            print("⚠️ No rate-based models found")
            return
        
        try:
            # Load performance metrics
            perf_file = os.path.join(self.rate_models_dir, 'rate_based_performance.json')
            with open(perf_file, 'r') as f:
                self.rate_performance = json.load(f)
            
            # Load models
            for model_name in self.rate_performance.keys():
                try:
                    model_file = os.path.join(self.rate_models_dir, f"{model_name}_model.pkl")
                    scaler_file = os.path.join(self.rate_models_dir, f"{model_name}_scaler.pkl")
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.rate_models[model_name] = joblib.load(model_file)
                        self.rate_scalers[model_name] = joblib.load(scaler_file)
                        
                except Exception as e:
                    print(f"⚠️ Failed to load rate model {model_name}: {e}")
            
            print(f"✅ Loaded {len(self.rate_models)} rate-based models")
            
        except Exception as e:
            print(f"❌ Failed to load rate models: {e}")
    
    def predict_batter_rates(self, player_features):
        """Predict performance rates for a batter"""
        if not self.rate_models:
            return {}
        
        predicted_rates = {}
        
        # Default features if not provided
        default_features = {
            'player_age': 28,
            'age_factor': 1.0,
            'games_played': 140,
            'playing_time_factor': 0.86,
            'G': 140,
            'AB': 500,
            'PA': 600,
            'season': 2024,
            'tier_above_average': 0,
            'tier_average': 1,
            'tier_below_average': 0,
            'tier_elite': 0
        }
        
        # Merge provided features with defaults
        features = {**default_features, **player_features}
        
        for rate_name, model in self.rate_models.items():
            try:
                # Get expected feature names from model training
                expected_features = self.rate_performance[rate_name]['features']
                
                # Prepare feature vector
                feature_vector = []
                for feature_name in expected_features:
                    feature_vector.append(features.get(feature_name, 0))
                
                feature_array = np.array(feature_vector).reshape(1, -1)
                
                # Scale and predict
                scaled_features = self.rate_scalers[rate_name].transform(feature_array)
                prediction = model.predict(scaled_features)[0]
                
                # Get confidence from model performance
                confidence = self.rate_performance[rate_name]['r2']
                
                rate_stat_name = rate_name.replace('rate_', '')
                predicted_rates[rate_stat_name] = {
                    'value': prediction,
                    'confidence': confidence
                }
                
            except Exception as e:
                print(f"⚠️ Failed to predict {rate_name}: {e}")
                continue
        
        return predicted_rates
    
    def convert_rates_to_game_stats(self, rates, plate_appearances=4.0, at_bats=3.5):
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
        
        # Estimate other stats from hits and performance
        slg = slugging_pct
        ops = on_base_pct + slg
        
        # Doubles (typically 20-25% of hits for average players)
        doubles = max(0, round(hits * 0.22))
        
        # Triples (very rare, ~1% of hits)
        triples = 1 if hits >= 3 and np.random.random() < 0.02 else 0
        
        # Runs and RBIs (correlated with overall offensive performance)
        if ops >= 0.850:
            run_rbi_factor = 1.2
        elif ops >= 0.750:
            run_rbi_factor = 1.0
        else:
            run_rbi_factor = 0.8
        
        runs = max(0, round((hits + walks) * 0.3 * run_rbi_factor))
        rbis = max(0, round(hits * 0.4 * run_rbi_factor))
        
        # Calculate confidence scores (average of underlying rate confidences)
        rate_confidences = [r.get('confidence', 0) for r in rates.values()]
        avg_confidence = np.mean(rate_confidences) if rate_confidences else 0.1
        
        game_stats = {
            'predicted_hits': {'value': hits, 'confidence': rates.get('batting_avg', {}).get('confidence', avg_confidence)},
            'predicted_doubles': {'value': doubles, 'confidence': avg_confidence * 0.8},
            'predicted_triples': {'value': triples, 'confidence': 0.1},  # Triples are very unpredictable
            'predicted_home_runs': {'value': home_runs, 'confidence': rates.get('home_run_rate', {}).get('confidence', avg_confidence)},
            'predicted_walks': {'value': walks, 'confidence': rates.get('walk_rate', {}).get('confidence', avg_confidence)},
            'predicted_strikeouts': {'value': strikeouts, 'confidence': rates.get('strikeout_rate', {}).get('confidence', avg_confidence)},
            'predicted_runs': {'value': runs, 'confidence': avg_confidence * 0.7},
            'predicted_rbis': {'value': rbis, 'confidence': avg_confidence * 0.7},
            'predicted_stolen_bases': {'value': stolen_bases, 'confidence': rates.get('steal_rate', {}).get('confidence', avg_confidence)}
        }
        
        return game_stats
    
    def predict_enhanced_batter_stats(self, player_features=None):
        """Full pipeline: predict rates then convert to game stats"""
        player_features = player_features or {}
        
        # Step 1: Predict performance rates
        predicted_rates = self.predict_batter_rates(player_features)
        
        if not predicted_rates:
            return {}
        
        # Step 2: Convert rates to game stats
        game_stats = self.convert_rates_to_game_stats(predicted_rates)
        
        return {
            'predicted_rates': predicted_rates,
            'predicted_game_stats': game_stats
        }

def test_rate_based_prediction():
    """Test the rate-based prediction system"""
    print("🧪 TESTING RATE-BASED BATTER PREDICTIONS")
    print("=" * 50)
    
    predictor = RateBasedBatterPredictor()
    
    if not predictor.rate_models:
        print("❌ No rate models loaded")
        return
    
    # Test with different player profiles
    test_players = [
        {
            'name': 'Elite Power Hitter',
            'features': {
                'player_age': 28,
                'games_played': 150,
                'AB': 550,
                'PA': 650,
                'tier_elite': 1,
                'tier_above_average': 0,
                'tier_average': 0,
                'tier_below_average': 0
            }
        },
        {
            'name': 'Average Player',
            'features': {
                'player_age': 29,
                'games_played': 140,
                'AB': 500,
                'PA': 600,
                'tier_elite': 0,
                'tier_above_average': 0,
                'tier_average': 1,
                'tier_below_average': 0
            }
        },
        {
            'name': 'Contact Hitter',
            'features': {
                'player_age': 31,
                'games_played': 130,
                'AB': 480,
                'PA': 540,
                'tier_elite': 0,
                'tier_above_average': 1,
                'tier_average': 0,
                'tier_below_average': 0
            }
        }
    ]
    
    for player in test_players:
        print(f"\n📊 Testing: {player['name']}")
        print("-" * 30)
        
        result = predictor.predict_enhanced_batter_stats(player['features'])
        
        if 'predicted_rates' in result:
            print("🎯 Predicted Rates:")
            for rate_name, rate_data in result['predicted_rates'].items():
                print(f"  {rate_name}: {rate_data['value']:.3f} (conf: {rate_data['confidence']:.2f})")
        
        if 'predicted_game_stats' in result:
            print("\n⚾ Expected Game Stats:")
            for stat_name, stat_data in result['predicted_game_stats'].items():
                stat_short = stat_name.replace('predicted_', '')
                print(f"  {stat_short}: {stat_data['value']} (conf: {stat_data['confidence']:.2f})")

if __name__ == "__main__":
    test_rate_based_prediction()