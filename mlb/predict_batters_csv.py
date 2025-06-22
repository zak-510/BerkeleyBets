#!/usr/bin/env python3
"""
MLB Batter Predictions from CSV
Streamlined script to predict fantasy points for batters from CSV input data
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class MLBBatterPredictor:
    """Streamlined batter prediction from CSV data"""
    
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.performance = {}
        self.load_models()
    
    def load_models(self):
        """Load all batter position models"""
        try:
            # Load performance metrics
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.performance = json.load(f)
            
            # Load batter models (all positions except P)
            batter_positions = ['C', '1B', '2B', '3B', 'SS', 'OF']
            
            for position in batter_positions:
                try:
                    model_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_model.pkl')
                    scaler_file = os.path.join(self.models_dir, f'mlb_{position.lower()}_scaler.pkl')
                    
                    if os.path.exists(model_file) and os.path.exists(scaler_file):
                        self.models[position] = joblib.load(model_file)
                        self.scalers[position] = joblib.load(scaler_file)
                        print(f"✅ Loaded {position} model (R²={self.performance[position]['r2']:.3f})")
                    else:
                        print(f"⚠️ Model files not found for {position}")
                        
                except Exception as e:
                    print(f"❌ Failed to load {position} model: {e}")
            
            print(f"📈 Successfully loaded {len(self.models)} batter models")
            
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            sys.exit(1)
    
    def validate_csv_format(self, df):
        """Validate CSV has required columns for batter predictions"""
        required_cols = [
            'player_name',
            'avg_fantasy_points_L15',
            'avg_fantasy_points_L10', 
            'avg_fantasy_points_L5',
            'games_since_last_good_game',
            'trend_last_5_games',
            'consistency_score'
        ]
        
        optional_cols = ['position']  # Will default to OF if missing
        
        missing_required = [col for col in required_cols if col not in df.columns]
        
        if missing_required:
            print(f"❌ Missing required columns: {missing_required}")
            print(f"📋 Required columns: {required_cols}")
            print(f"📋 Optional columns: {optional_cols}")
            return False
        
        print(f"✅ CSV format validation passed")
        print(f"📊 Input data: {len(df)} players")
        return True
    
    def predict_from_csv(self, csv_file, output_file=None):
        """Run predictions for all batters in CSV file"""
        try:
            # Load CSV data
            print(f"📊 Loading data from: {csv_file}")
            df = pd.read_csv(csv_file)
            
            # Validate format
            if not self.validate_csv_format(df):
                return None
            
            # Add default position if missing
            if 'position' not in df.columns:
                df['position'] = 'OF'
                print("📋 No position column found, defaulting all players to OF")
            
            # Filter for batter positions only
            batter_positions = ['C', '1B', '2B', '3B', 'SS', 'OF']
            batter_mask = df['position'].isin(batter_positions)
            batter_data = df[batter_mask].copy()
            
            if len(batter_data) == 0:
                print("❌ No batter data found in CSV (positions: C, 1B, 2B, 3B, SS, OF)")
                return None
            
            print(f"🎯 Found {len(batter_data)} batters to predict")
            
            # Prepare features
            feature_cols = [
                'avg_fantasy_points_L15',
                'avg_fantasy_points_L10', 
                'avg_fantasy_points_L5',
                'games_since_last_good_game',
                'trend_last_5_games',
                'consistency_score'
            ]
            
            # Initialize results
            results = []
            
            # Predict for each player
            for idx, row in batter_data.iterrows():
                try:
                    player_name = row['player_name']
                    position = row['position']
                    
                    # Use OF model if specific position model not available
                    model_position = position if position in self.models else 'OF'
                    
                    if model_position not in self.models:
                        print(f"⚠️ No model available for {player_name} ({position})")
                        continue
                    
                    # Prepare features
                    features = row[feature_cols].values.reshape(1, -1)
                    features = np.nan_to_num(features, nan=0.0)  # Handle NaN values
                    
                    # Scale features
                    features_scaled = self.scalers[model_position].transform(features)
                    
                    # Predict
                    prediction = self.models[model_position].predict(features_scaled)[0]
                    
                    # Calculate confidence based on model performance
                    model_r2 = self.performance[model_position]['r2']
                    confidence = min(0.9, max(0.3, model_r2))
                    
                    results.append({
                        'player_name': player_name,
                        'position': position,
                        'model_used': model_position,
                        'predicted_fantasy_points': round(prediction, 2),
                        'confidence': round(confidence, 2),
                        'model_r2': round(model_r2, 3),
                        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    print(f"✅ {player_name} ({position}): {prediction:.2f} points [confidence: {confidence:.2f}]")
                    
                except Exception as e:
                    print(f"❌ Failed to predict for {row.get('player_name', 'Unknown')}: {e}")
                    continue
            
            # Create results DataFrame
            results_df = pd.DataFrame(results)
            
            if len(results_df) == 0:
                print("❌ No successful predictions generated")
                return None
            
            # Save results
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f'batter_predictions_{timestamp}.csv'
            
            results_df.to_csv(output_file, index=False)
            
            # Summary
            print(f"\n📊 BATTER PREDICTION SUMMARY:")
            print(f"{'='*50}")
            print(f"📋 Total players processed: {len(batter_data)}")
            print(f"✅ Successful predictions: {len(results_df)}")
            print(f"📁 Output file: {output_file}")
            
            # Performance by position
            print(f"\n📈 Predictions by position:")
            for pos in results_df['position'].unique():
                pos_data = results_df[results_df['position'] == pos]
                avg_pred = pos_data['predicted_fantasy_points'].mean()
                print(f"  {pos}: {len(pos_data)} players, avg {avg_pred:.2f} points")
            
            print(f"\n✅ Batter predictions saved to: {output_file}")
            return results_df
            
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return None

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MLB Batter Fantasy Predictions from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format Requirements:
  Required columns:
    - player_name: Player name
    - avg_fantasy_points_L15: Average fantasy points last 15 games
    - avg_fantasy_points_L10: Average fantasy points last 10 games  
    - avg_fantasy_points_L5: Average fantasy points last 5 games
    - games_since_last_good_game: Games since >10 fantasy points
    - trend_last_5_games: Trend in last 5 games (positive = improving)
    - consistency_score: Performance consistency (0-1, higher = more consistent)
  
  Optional columns:
    - position: Player position (C, 1B, 2B, 3B, SS, OF) - defaults to OF

Examples:
  python predict_batters_csv.py batters.csv
  python predict_batters_csv.py batters.csv --output results.csv
  python predict_batters_csv.py batters.csv --models custom_models/
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file with batter data')
    parser.add_argument('--output', '-o', help='Output CSV file (auto-generated if not specified)')
    parser.add_argument('--models', '-m', default='models', help='Models directory (default: models)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ Input file not found: {args.csv_file}")
        sys.exit(1)
    
    # Initialize predictor
    print("🚀 MLB BATTER PREDICTION FROM CSV")
    print("=" * 50)
    print(f"📊 Input file: {args.csv_file}")
    print(f"🎯 Models directory: {args.models}")
    
    predictor = MLBBatterPredictor(models_dir=args.models)
    
    # Run predictions
    results = predictor.predict_from_csv(args.csv_file, args.output)
    
    if results is not None:
        print(f"\n🎉 Batter predictions completed successfully!")
    else:
        print(f"\n❌ Batter predictions failed")
        sys.exit(1)

if __name__ == "__main__":
    main()