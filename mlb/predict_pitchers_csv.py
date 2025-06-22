#!/usr/bin/env python3
"""
MLB Pitcher Predictions from CSV
Streamlined script to predict fantasy points for pitchers from CSV input data
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class MLBPitcherPredictor:
    """Streamlined pitcher prediction from CSV data"""
    
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.model = None
        self.scaler = None
        self.performance = {}
        self.load_model()
    
    def load_model(self):
        """Load pitcher model"""
        try:
            # Load performance metrics
            perf_file = os.path.join(self.models_dir, 'model_performance.json')
            with open(perf_file, 'r') as f:
                self.performance = json.load(f)
            
            # Load pitcher model
            model_file = os.path.join(self.models_dir, 'mlb_p_model.pkl')
            scaler_file = os.path.join(self.models_dir, 'mlb_p_scaler.pkl')
            
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                r2_score = self.performance['P']['r2']
                print(f"✅ Loaded pitcher model (R²={r2_score:.3f})")
            else:
                print(f"❌ Pitcher model files not found")
                print(f"   Expected: {model_file}")
                print(f"   Expected: {scaler_file}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Failed to load pitcher model: {e}")
            sys.exit(1)
    
    def validate_csv_format(self, df):
        """Validate CSV has required columns for pitcher predictions"""
        required_cols = [
            'player_name',
            'avg_fantasy_points_L15',
            'avg_fantasy_points_L10', 
            'avg_fantasy_points_L5',
            'games_since_last_good_game',
            'trend_last_5_games',
            'consistency_score'
        ]
        
        optional_cols = ['position']  # Should be 'P' for pitchers
        
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
        """Run predictions for all pitchers in CSV file"""
        try:
            # Load CSV data
            print(f"📊 Loading data from: {csv_file}")
            df = pd.read_csv(csv_file)
            
            # Validate format
            if not self.validate_csv_format(df):
                return None
            
            # Filter for pitchers only
            if 'position' in df.columns:
                pitcher_data = df[df['position'] == 'P'].copy()
                if len(pitcher_data) == 0:
                    print("❌ No pitchers found in CSV (position = 'P')")
                    print(f"📋 Available positions: {df['position'].unique()}")
                    return None
            else:
                # If no position column, assume all are pitchers
                pitcher_data = df.copy()
                print("📋 No position column found, assuming all players are pitchers")
            
            print(f"🎯 Found {len(pitcher_data)} pitchers to predict")
            
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
            
            # Predict for each pitcher
            for idx, row in pitcher_data.iterrows():
                try:
                    player_name = row['player_name']
                    
                    # Prepare features
                    features = row[feature_cols].values.reshape(1, -1)
                    features = np.nan_to_num(features, nan=0.0)  # Handle NaN values
                    
                    # Scale features
                    features_scaled = self.scaler.transform(features)
                    
                    # Predict
                    prediction = self.model.predict(features_scaled)[0]
                    
                    # Calculate confidence based on model performance
                    model_r2 = self.performance['P']['r2']
                    confidence = min(0.9, max(0.3, model_r2))
                    
                    results.append({
                        'player_name': player_name,
                        'position': 'P',
                        'predicted_fantasy_points': round(prediction, 2),
                        'confidence': round(confidence, 2),
                        'model_r2': round(model_r2, 3),
                        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    print(f"✅ {player_name}: {prediction:.2f} points [confidence: {confidence:.2f}]")
                    
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
                output_file = f'pitcher_predictions_{timestamp}.csv'
            
            results_df.to_csv(output_file, index=False)
            
            # Summary
            print(f"\n📊 PITCHER PREDICTION SUMMARY:")
            print(f"{'='*50}")
            print(f"📋 Total pitchers processed: {len(pitcher_data)}")
            print(f"✅ Successful predictions: {len(results_df)}")
            print(f"📁 Output file: {output_file}")
            
            # Statistics
            predictions = results_df['predicted_fantasy_points']
            print(f"\n📈 Prediction statistics:")
            print(f"  Average: {predictions.mean():.2f} points")
            print(f"  Range: {predictions.min():.2f} - {predictions.max():.2f} points")
            print(f"  Median: {predictions.median():.2f} points")
            
            # Top predictions
            top_pitchers = results_df.nlargest(5, 'predicted_fantasy_points')
            print(f"\n🏆 Top 5 predicted performances:")
            for idx, row in top_pitchers.iterrows():
                print(f"  {row['player_name']}: {row['predicted_fantasy_points']:.2f} points")
            
            print(f"\n✅ Pitcher predictions saved to: {output_file}")
            return results_df
            
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return None

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MLB Pitcher Fantasy Predictions from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CSV Format Requirements:
  Required columns:
    - player_name: Pitcher name
    - avg_fantasy_points_L15: Average fantasy points last 15 games
    - avg_fantasy_points_L10: Average fantasy points last 10 games  
    - avg_fantasy_points_L5: Average fantasy points last 5 games
    - games_since_last_good_game: Games since >10 fantasy points
    - trend_last_5_games: Trend in last 5 games (positive = improving)
    - consistency_score: Performance consistency (0-1, higher = more consistent)
  
  Optional columns:
    - position: Should be 'P' for pitchers (if missing, assumes all are pitchers)

Examples:
  python predict_pitchers_csv.py pitchers.csv
  python predict_pitchers_csv.py pitchers.csv --output results.csv
  python predict_pitchers_csv.py pitchers.csv --models custom_models/
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file with pitcher data')
    parser.add_argument('--output', '-o', help='Output CSV file (auto-generated if not specified)')
    parser.add_argument('--models', '-m', default='models', help='Models directory (default: models)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ Input file not found: {args.csv_file}")
        sys.exit(1)
    
    # Initialize predictor
    print("🚀 MLB PITCHER PREDICTION FROM CSV")
    print("=" * 50)
    print(f"📊 Input file: {args.csv_file}")
    print(f"🎯 Models directory: {args.models}")
    
    predictor = MLBPitcherPredictor(models_dir=args.models)
    
    # Run predictions
    results = predictor.predict_from_csv(args.csv_file, args.output)
    
    if results is not None:
        print(f"\n🎉 Pitcher predictions completed successfully!")
    else:
        print(f"\n❌ Pitcher predictions failed")
        sys.exit(1)

if __name__ == "__main__":
    main()