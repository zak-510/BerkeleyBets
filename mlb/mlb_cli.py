#!/usr/bin/env python3
"""
MLB Fantasy Baseball CLI Predictions
Command-line interface for making MLB player predictions using position-specific models
"""

import argparse
import pandas as pd
import joblib
import numpy as np
from pathlib import Path

class ImprovedMLBCLI:
    def __init__(self):
        self.models = {}
        self.position_features = {
            'P': ['wins', 'losses', 'era', 'whip', 'strikeouts', 'innings_pitched', 'saves', 'holds'],
            'C': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            '1B': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            '2B': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            '3B': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            'SS': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            'OF': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg'],
            'DH': ['hits', 'home_runs', 'rbi', 'runs', 'stolen_bases', 'batting_average', 'obp', 'slg']
        }
    
    def load_models(self):
        """Load all position-specific models"""
        positions = ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH']
        loaded_count = 0
        
        for pos in positions:
            model_file = f'mlb_{pos.lower()}_model.pkl'
            if Path(model_file).exists():
                try:
                    model_data = joblib.load(model_file)
                    self.models[pos] = model_data
                    loaded_count += 1
                    print(f"✓ Loaded {pos} model")
                except Exception as e:
                    print(f"✗ Failed to load {pos} model: {e}")
            else:
                print(f"✗ {pos} model not found: {model_file}")
        
        if loaded_count == 0:
            print("❌ No models loaded. Train models first with: python mlb_model.py")
            return False
        
        print(f"✓ Successfully loaded {loaded_count}/{len(positions)} models")
        return True
    
    def predict_player(self, position, player_stats):
        """Make prediction for a player"""
        if position not in self.models:
            raise ValueError(f"No model available for position: {position}")
        
        model_data = self.models[position]
        model = model_data['model']
        features = model_data['features']
        
        # Extract features in correct order
        feature_values = []
        for feature in features:
            value = player_stats.get(feature, 0)
            feature_values.append(float(value))
        
        # Make prediction
        X = np.array(feature_values).reshape(1, -1)
        prediction = model.predict(X)[0]
        
        return round(prediction, 1)

def main():
    parser = argparse.ArgumentParser(description='MLB Fantasy Baseball Predictions (Position-Specific Models)')
    parser.add_argument('--position', type=str, choices=['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH'],
                       help='Player position')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode for manual stat input')
    parser.add_argument('--show-results', action='store_true',
                       help='Show latest prediction results')
    
    args = parser.parse_args()
    
    cli = ImprovedMLBCLI()
    
    if args.show_results:
        # Show results from CSV
        try:
            results = pd.read_csv('mlb_inference_results.csv')
            print("⚾ Latest MLB Fantasy Predictions")
            print("=" * 50)
            print(f"Total Players: {len(results)}")
            
            # Top 10 performers
            top_10 = results.nlargest(10, 'actual_points')
            print("\nTop 10 Fantasy Performers:")
            print(f"{'Rank':<4} {'Player':<20} {'Pos':<3} {'Actual':<7} {'Predicted':<9}")
            print("-" * 50)
            for i, (_, player) in enumerate(top_10.iterrows(), 1):
                print(f"{i:<4} {player['player_name'][:19]:<20} {player['position']:<3} "
                      f"{player['actual_points']:<7.1f} {player['predicted_points']:<9.1f}")
            
        except FileNotFoundError:
            print("❌ No results found. Run predictions first.")
        return 0
    
    if not cli.load_models():
        return 1
    
    if args.interactive:
        # Interactive mode
        print("⚾ MLB Fantasy Prediction - Interactive Mode")
        print("=" * 50)
        
        # Get position
        if args.position:
            position = args.position
        else:
            position = input("Enter player position (P/C/1B/2B/3B/SS/OF/DH): ").strip().upper()
            if position not in ['P', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH']:
                print("❌ Invalid position. Must be P, C, 1B, 2B, 3B, SS, OF, or DH")
                return 1
        
        if position not in cli.models:
            print(f"❌ No model available for position: {position}")
            return 1
        
        # Get required features for this position
        required_features = cli.position_features[position]
        
        print(f"\nEnter {position} statistics (press Enter for 0):")
        player_stats = {}
        
        # Feature display names
        feature_names = {
            'hits': 'Hits',
            'home_runs': 'Home Runs',
            'rbi': 'RBI',
            'runs': 'Runs',
            'stolen_bases': 'Stolen Bases',
            'batting_average': 'Batting Average',
            'obp': 'OBP',
            'slg': 'SLG',
            'wins': 'Wins',
            'losses': 'Losses',
            'era': 'ERA',
            'whip': 'WHIP',
            'strikeouts': 'Strikeouts',
            'innings_pitched': 'Innings Pitched',
            'saves': 'Saves',
            'holds': 'Holds'
        }
        
        for feature in required_features:
            display_name = feature_names.get(feature, feature)
            try:
                value = input(f"{display_name}: ").strip()
                player_stats[feature] = float(value) if value else 0.0
            except ValueError:
                player_stats[feature] = 0.0
        
        # Make prediction
        try:
            prediction = cli.predict_player(position, player_stats)
            print(f"\n🎯 Fantasy Points Projection: {prediction} points")
            print(f"   📝 Position: {position}")
            print(f"   📊 Based on standard 5x5 scoring")
            
            # Show confidence based on position
            position_confidence = {
                'P': 'Medium (Pitching is volatile)',
                'C': 'High (Catcher stats are consistent)',
                '1B': 'High (Power hitters are predictable)',
                '2B': 'Medium (Mixed skill sets)',
                '3B': 'High (Power/contact balance)',
                'SS': 'Medium (Speed/power mix)',
                'OF': 'High (Outfielders are consistent)',
                'DH': 'High (Designated hitters are predictable)'
            }
            
            print(f"   🎲 Prediction Confidence: {position_confidence[position]}")
            
            # Show scoring breakdown
            if position == 'P':
                print(f"   📈 Scoring: Wins (10), Saves (10), Ks (1), ERA/WHIP bonuses")
            else:
                print(f"   📈 Scoring: Hits (1), HR (4), RBI (2), Runs (2), SB (2)")
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return 1
    
    else:
        print("❌ Please use --interactive mode or --show-results")
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 