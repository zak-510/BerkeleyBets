#!/usr/bin/env python3
"""
NFL Fantasy Football CLI Predictions
Command-line interface for making NFL player predictions using improved position-specific models
"""

import argparse
import pandas as pd
import joblib
import numpy as np
from pathlib import Path

class ImprovedNFLCLI:
    def __init__(self):
        self.models = {}
        self.position_features = {
            'QB': ['passing_yards', 'passing_tds', 'interceptions', 'attempts', 'rushing_yards', 'rushing_tds'],
            'RB': ['rushing_yards', 'rushing_tds', 'carries', 'receiving_yards', 'receiving_tds', 'targets'],
            'WR': ['receiving_yards', 'receiving_tds', 'targets', 'receptions', 'rushing_yards'],
            'TE': ['receiving_yards', 'receiving_tds', 'targets', 'receptions']
        }
    
    def load_models(self):
        """Load all position-specific models"""
        positions = ['QB', 'RB', 'WR', 'TE']
        loaded_count = 0
        
        for pos in positions:
            model_file = f'nfl_{pos.lower()}_model.pkl'
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
            print("❌ No models loaded. Train models first with: python nfl_model.py")
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
    parser = argparse.ArgumentParser(description='NFL Fantasy Football Predictions (Improved Models)')
    parser.add_argument('--position', type=str, choices=['QB', 'RB', 'WR', 'TE'],
                       help='Player position')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode for manual stat input')
    parser.add_argument('--show-results', action='store_true',
                       help='Show latest prediction results')
    
    args = parser.parse_args()
    
    cli = ImprovedNFLCLI()
    
    if args.show_results:
        # Show results from CSV
        try:
            results = pd.read_csv('final_inference_results.csv')
            print("🏈 Latest NFL Fantasy Predictions")
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
        print("🏈 NFL Fantasy Prediction - Interactive Mode")
        print("=" * 50)
        
        # Get position
        if args.position:
            position = args.position
        else:
            position = input("Enter player position (QB/RB/WR/TE): ").strip().upper()
            if position not in ['QB', 'RB', 'WR', 'TE']:
                print("❌ Invalid position. Must be QB, RB, WR, or TE")
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
            'passing_yards': 'Passing Yards',
            'passing_tds': 'Passing TDs', 
            'interceptions': 'Interceptions',
            'attempts': 'Passing Attempts',
            'rushing_yards': 'Rushing Yards',
            'rushing_tds': 'Rushing TDs',
            'carries': 'Rushing Attempts',
            'receiving_yards': 'Receiving Yards',
            'receiving_tds': 'Receiving TDs',
            'receptions': 'Receptions',
            'targets': 'Targets'
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
            print(f"   📊 Based on PPR scoring")
            
            # Show confidence based on position
            position_confidence = {
                'QB': 'Medium (MAE: 21.9)',
                'RB': 'Medium (MAE: 14.8)', 
                'WR': 'High (MAE: 6.8)',
                'TE': 'High (MAE: 7.9)'
            }
            
            print(f"   🎲 Prediction Confidence: {position_confidence[position]}")
            
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